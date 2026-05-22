"""Lightweight hooks for solver-generated surrogate predictor candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SurrogateCandidateSpec:
    """Metadata for a future predictor trained from solver outputs."""

    source_model_id: str
    target_outputs: list[str]
    input_parameters: list[str]
    training_family_id: str = "physical.surrogate_eval"
    validation_metrics: list[str] = field(default_factory=lambda: ["mae", "rmse", "max_error"])
    notes: str = ""

    def to_metadata(self) -> dict[str, Any]:
        return {"surrogate_candidate": asdict(self)}


def default_surrogate_candidate(
    source_model_id: str,
    input_parameters: list[str],
    target_outputs: list[str],
) -> SurrogateCandidateSpec:
    """Create default surrogate metadata for a solver sweep dataset."""
    return SurrogateCandidateSpec(
        source_model_id=source_model_id,
        input_parameters=input_parameters,
        target_outputs=target_outputs,
    )
