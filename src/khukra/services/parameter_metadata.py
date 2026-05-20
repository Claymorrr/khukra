"""Shared parameter metadata hints for dynamic forms."""

from __future__ import annotations

from typing import Any

PARAMETER_HINTS: dict[str, dict[str, Any]] = {
    "seed": {
        "description": "Random seed for reproducible stochastic scenarios.",
        "min": 0,
        "max": 999999,
        "step": 1,
        "unit": "",
    },
    "history_length": {
        "description": "Number of historical time steps in the synthetic series.",
        "min": 24,
        "max": 2000,
        "step": 1,
        "unit": "steps",
    },
    "forecast_horizon": {
        "description": "Forecast steps beyond the observed history.",
        "min": 1,
        "max": 500,
        "step": 1,
        "unit": "steps",
    },
    "persist_synthetic": {
        "description": "Persist generated scenario to Parquet and warehouse catalog.",
        "options": [True, False],
    },
    "noise_scale": {
        "description": "Scale factor for stochastic noise components.",
        "min": 0.0,
        "max": 5.0,
        "step": 0.05,
        "unit": "",
    },
    "jump_intensity": {
        "description": "Intensity of jump events in the stochastic process.",
        "min": 0.0,
        "max": 2.0,
        "step": 0.01,
        "unit": "",
    },
}


def enrich_parameter(name: str, param_type: str, default: Any, label: str) -> dict[str, Any]:
    hints = PARAMETER_HINTS.get(name, {})
    return {
        "name": name,
        "type": param_type,
        "default": default,
        "label": label,
        "description": hints.get("description", ""),
        "unit": hints.get("unit", ""),
        "min": hints.get("min"),
        "max": hints.get("max"),
        "step": hints.get("step"),
        "options": hints.get("options", []),
    }
