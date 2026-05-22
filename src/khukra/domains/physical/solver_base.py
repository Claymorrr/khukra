"""Base helpers for physics solvers producing enriched ModelResult metadata."""

from __future__ import annotations

from typing import Any

from khukra.core.model import Model, ModelResult
from khukra.domains.physical.core import SolverResultSummary, SolverSpec
from khukra.domains.physical.models_registry import get_solver_spec
from khukra.domains.physical.units import normalize_solver_inputs


def prepare_solver_parameters(
    model: Model,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge defaults with user inputs and canonicalize physical units from SolverSpec."""
    raw = dict(parameters or {})
    input_units = raw.pop("units", None) or raw.pop("__units__", None)
    merged = {**model.default_parameters(), **raw}
    spec = get_solver_spec(getattr(model, "name", ""))
    if not spec:
        return merged
    param_units = {p.name: p.unit for p in spec.parameters if p.unit}
    return normalize_solver_inputs(
        merged,
        param_units,
        input_units=input_units if isinstance(input_units, dict) else None,
    )


def enrich_solver_result(
    result: ModelResult,
    spec: SolverSpec,
    *,
    numerical: SolverResultSummary | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> ModelResult:
    """Attach solver spec and numerical status to an existing ModelResult."""
    meta = {**spec.to_metadata()}
    if numerical:
        meta.update(numerical.to_metadata())
    if extra_metadata:
        meta.update(extra_metadata)
    result.metadata = {**result.metadata, **meta}
    result.metadata.setdefault("model_kind", spec.model_kind)
    result.metadata.setdefault("artifact_role", spec.artifact_role)
    return result
