"""Shared types for physics solver metadata and scientific outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PhysicalQuantity:
    """Named physical quantity with unit and optional description."""

    name: str
    unit: str
    description: str = ""


@dataclass(frozen=True)
class SolverParameter:
    """Model input parameter with physical meaning."""

    name: str
    unit: str
    default: float | int | bool
    description: str = ""


@dataclass(frozen=True)
class SolverVariable:
    """State or spatial variable tracked by the solver."""

    name: str
    unit: str
    role: str  # e.g. state, spatial, derived
    description: str = ""


@dataclass(frozen=True)
class SolverOutput:
    """Scalar metric emitted by a solver run."""

    name: str
    unit: str
    label: str
    description: str = ""


@dataclass
class SolverSpec:
    """Scientific specification for a registered physics solver."""

    model_id: str
    subdomain: str
    model_kind: str
    title: str
    governing_equations: str
    assumptions: list[str] = field(default_factory=list)
    parameters: list[SolverParameter] = field(default_factory=list)
    state_variables: list[SolverVariable] = field(default_factory=list)
    outputs: list[SolverOutput] = field(default_factory=list)
    equations: list["EquationSpec"] = field(default_factory=list)
    predictor_type: str = ""
    artifact_role: str = "solver_output"
    version: str = "1.0.0"
    supports_uncertainty: bool = False

    def to_metadata(self) -> dict[str, Any]:
        return {
            "solver_spec": {
                "model_id": self.model_id,
                "subdomain": self.subdomain,
                "model_kind": self.model_kind,
                "title": self.title,
                "governing_equations": self.governing_equations,
                "assumptions": self.assumptions,
                "parameters": [asdict(p) for p in self.parameters],
                "state_variables": [asdict(v) for v in self.state_variables],
                "outputs": [asdict(o) for o in self.outputs],
                "equations": [asdict(e) for e in self.equations],
            }
        }


@dataclass(frozen=True)
class EquationVariable:
    """Symbolic or structural variable in an equation system."""

    name: str
    unit: str = ""
    role: str = "state"
    description: str = ""


@dataclass(frozen=True)
class EquationSpec:
    """Structured equation specification for a physics solver."""

    name: str
    form: str
    variables: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    equation_type: str = "algebraic"
    residual: str | None = None
    description: str = ""


@dataclass
class SolverResultSummary:
    """Numerical status and analytic summaries attached to a run."""

    integration_success: bool = True
    n_steps: int = 0
    notes: str = ""

    def to_metadata(self) -> dict[str, Any]:
        return {"numerical_status": asdict(self)}
