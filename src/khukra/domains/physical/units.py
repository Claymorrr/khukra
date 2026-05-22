"""Lightweight unit registry and conversion helpers for Physical Systems solvers.

The registry is intentionally small and deterministic. It covers the units used by
the current solver specs without pulling in a third-party units dependency yet.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class UnitDefinition:
    """Canonical unit definition.

    ``scale_to_si`` converts a value in this unit to the canonical SI-like base
    for its dimension. Offset is included for future absolute temperature support,
    but current solvers use Celsius deltas/values directly.
    """

    unit: str
    dimension: str
    scale_to_si: float = 1.0
    offset_to_si: float = 0.0
    description: str = ""


UNIT_REGISTRY: dict[str, UnitDefinition] = {
    "": UnitDefinition("", "dimensionless", description="Dimensionless value"),
    "m": UnitDefinition("m", "length", description="metre"),
    "mm": UnitDefinition("mm", "length", 1e-3, description="millimetre"),
    "kg": UnitDefinition("kg", "mass", description="kilogram"),
    "N": UnitDefinition("N", "force", description="newton"),
    "N/m": UnitDefinition("N/m", "distributed_load", description="newton per metre"),
    "N*s/m": UnitDefinition("N*s/m", "damping", description="newton-second per metre"),
    "Pa": UnitDefinition("Pa", "pressure", description="pascal"),
    "m^4": UnitDefinition("m^4", "second_moment", description="metre to the fourth power"),
    "s": UnitDefinition("s", "time", description="second"),
    "m/s": UnitDefinition("m/s", "velocity", description="metre per second"),
    "J": UnitDefinition("J", "energy", description="joule"),
    "W/K": UnitDefinition("W/K", "thermal_conductance", description="watt per kelvin"),
    "W": UnitDefinition("W", "power", description="watt"),
    "kW": UnitDefinition("kW", "power", 1000.0, description="kilowatt"),
    "deg C": UnitDefinition("deg C", "temperature", description="degree Celsius"),
    "deg": UnitDefinition("deg", "angle", description="degree"),
    "kN*m": UnitDefinition("kN*m", "moment", 1000.0, description="kilonewton metre"),
}

CANONICAL_UNITS: tuple[str, ...] = tuple(UNIT_REGISTRY.keys())

_ALIASES: dict[str, str] = {
    "": "",
    "1": "",
    "dimensionless": "",
    "count": "",
    "points": "",
    "m": "m",
    "meter": "m",
    "meters": "m",
    "metre": "m",
    "metres": "m",
    "mm": "mm",
    "millimeter": "mm",
    "millimeters": "mm",
    "millimetre": "mm",
    "millimetres": "mm",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "n": "N",
    "newton": "N",
    "newtons": "N",
    "n/m": "N/m",
    "n*m^-1": "N/m",
    "n*s/m": "N*s/m",
    "n-s/m": "N*s/m",
    "pa": "Pa",
    "pascal": "Pa",
    "pascals": "Pa",
    "m4": "m^4",
    "m^4": "m^4",
    "s": "s",
    "sec": "s",
    "second": "s",
    "seconds": "s",
    "m/s": "m/s",
    "mps": "m/s",
    "j": "J",
    "joule": "J",
    "joules": "J",
    "w/k": "W/K",
    "watt/kelvin": "W/K",
    "w": "W",
    "watt": "W",
    "watts": "W",
    "kw": "kW",
    "kilowatt": "kW",
    "kilowatts": "kW",
    "degc": "deg C",
    "deg c": "deg C",
    "degreec": "deg C",
    "celsius": "deg C",
    "c": "deg C",
    "deg": "deg",
    "degree": "deg",
    "degrees": "deg",
    "kn*m": "kN*m",
    "kn-m": "kN*m",
}


@dataclass(frozen=True)
class UnitConversionError(ValueError):
    """Raised when a unit cannot be parsed or converted."""

    unit: str

    def __str__(self) -> str:
        return f"Unsupported unit: {self.unit!r}"


def normalize_unit(unit: str) -> str:
    """Normalize unit string to canonical registry key."""
    raw = (unit or "").strip()
    if not raw:
        return ""
    lookup = raw.lower().replace("·", "*")
    if lookup in _ALIASES:
        return _ALIASES[lookup]
    if raw in UNIT_REGISTRY:
        return raw
    raise UnitConversionError(unit)


def is_supported_unit(unit: str) -> bool:
    try:
        normalize_unit(unit)
        return True
    except UnitConversionError:
        return False


def parse_unit(unit: str) -> UnitDefinition:
    """Parse a unit string into its canonical registry definition."""
    return UNIT_REGISTRY[normalize_unit(unit)]


def convert_value(value: float, from_unit: str, to_unit: str) -> float:
    """Convert numeric value between supported units of the same dimension."""
    src = parse_unit(from_unit)
    dst = parse_unit(to_unit)
    if src.unit == dst.unit:
        return float(value)
    if src.dimension == dst.dimension:
        si_value = float(value) * src.scale_to_si + src.offset_to_si
        return (si_value - dst.offset_to_si) / dst.scale_to_si
    raise UnitConversionError(f"{from_unit} -> {to_unit}")


def canonicalize_parameter(
    name: str,
    value: Any,
    spec_unit: str,
    *,
    input_unit: str | None = None,
) -> Any:
    """
    Normalize a single parameter value to the solver spec's canonical unit.
    Numeric values stay numeric; non-numeric values pass through unchanged.
    """
    if isinstance(value, dict) and "value" in value:
        input_unit = str(value.get("unit") or input_unit or spec_unit)
        value = value["value"]
    if not isinstance(value, (int, float)):
        return value
    target = normalize_unit(spec_unit) if spec_unit else ""
    if not target:
        return value
    source = normalize_unit(input_unit) if input_unit else target
    if source == target:
        return float(value)
    return convert_value(float(value), source, target)


def normalize_solver_inputs(
    parameters: dict[str, Any],
    param_units: dict[str, str],
    *,
    input_units: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Convert/validate physical solver inputs before Model.run()."""
    units_in = input_units or {}
    out: dict[str, Any] = {}
    for key, val in parameters.items():
        if key in {"units", "__units__"}:
            continue
        spec_u = param_units.get(key, "")
        if spec_u:
            out[key] = canonicalize_parameter(
                key, val, spec_u, input_unit=units_in.get(key)
            )
        else:
            out[key] = val
    return out


def parameter_schema_from_solver_param(
    name: str,
    param_type: str,
    default: Any,
    label: str,
    unit: str = "",
    description: str = "",
) -> dict[str, Any]:
    """Build catalog parameter schema fields with physical unit metadata."""
    return {
        "name": name,
        "type": param_type,
        "default": default,
        "label": label,
        "description": description,
        "unit": unit,
        "min": None,
        "max": None,
        "step": None,
        "options": [],
    }


def list_supported_units() -> list[str]:
    """Return sorted list of canonical unit keys (non-empty)."""
    return sorted(u for u in UNIT_REGISTRY if u)


def unit_registry_metadata() -> dict[str, dict[str, Any]]:
    """Expose unit registry details for tests, docs, or future catalog endpoints."""
    return {unit: asdict(defn) for unit, defn in UNIT_REGISTRY.items()}
