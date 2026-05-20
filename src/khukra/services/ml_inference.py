"""Platform-facing ML inference service."""

from __future__ import annotations

from typing import Any

from khukra.inference.engine import get_inference_engine
from khukra.inference.types import PredictionResult


class MLInferenceService:
    """Small service boundary for platform ML inference workflows."""

    def list_models(self) -> list[Any]:
        return get_inference_engine().list_models()

    def predict(
        self,
        domain: str,
        subdomain: str,
        model: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> PredictionResult:
        return get_inference_engine().predict(
            domain,
            subdomain,
            model,
            inputs or {},
            user_id=user_id,
        )
