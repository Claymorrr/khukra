"""Physical Systems: physics solvers, scientific analytics, and surrogate-ready outputs."""

from khukra.domains.physical.models_registry import (
    ARTIFACT_ROLES,
    DEFAULT_ARTIFACT_ROLE,
    MODEL_CLASSIFICATION,
    MODEL_KINDS,
    SOLVER_SPECS,
    artifact_role,
    get_solver_spec,
    inference_meta_for,
    model_kind,
)
from khukra.domains.physical.surrogates import SurrogateCandidateSpec, default_surrogate_candidate

__all__ = [
    "ARTIFACT_ROLES",
    "DEFAULT_ARTIFACT_ROLE",
    "MODEL_CLASSIFICATION",
    "MODEL_KINDS",
    "SOLVER_SPECS",
    "artifact_role",
    "get_solver_spec",
    "inference_meta_for",
    "model_kind",
    "SurrogateCandidateSpec",
    "default_surrogate_candidate",
]
