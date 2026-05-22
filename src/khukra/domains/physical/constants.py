"""Backward-compatible exports; canonical metadata lives in models_registry."""

from khukra.domains.physical.models_registry import (
    ARTIFACT_ROLES,
    DEFAULT_ARTIFACT_ROLE,
    MODEL_CLASSIFICATION,
    MODEL_KINDS,
    artifact_role,
    model_kind,
)

__all__ = [
    "ARTIFACT_ROLES",
    "DEFAULT_ARTIFACT_ROLE",
    "MODEL_CLASSIFICATION",
    "MODEL_KINDS",
    "artifact_role",
    "model_kind",
]
