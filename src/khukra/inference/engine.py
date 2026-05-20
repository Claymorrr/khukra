import time
import uuid
from typing import Any

from khukra.data.repositories.inferences import InferenceRepository
from khukra.data.repositories.lineage import LineageRepository
from khukra.domains.registry import get_model
from khukra.inference.predictors.rule_based import RuleBasedPredictor
from khukra.inference.registry import get_spec, model_key
from khukra.inference.types import InferenceModelSpec, PredictionResult
from khukra.inference.validator import InputValidationError, validate_inputs

_engine: "InferenceEngine | None" = None


class InferenceEngine:
    """Execute validated inference requests and persist prediction events."""

    def __init__(self, repo: InferenceRepository | None = None):
        self.repo = repo or InferenceRepository()
        self.lineage = LineageRepository(self.repo.engine)

    def get_spec(self, domain: str, subdomain: str, model_id: str) -> InferenceModelSpec:
        return get_spec(domain, subdomain, model_id)

    def list_models(self) -> list[InferenceModelSpec]:
        from khukra.inference.registry import list_specs

        return list_specs()

    def predict(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> PredictionResult:
        spec = get_spec(domain, subdomain, model_id)
        validated = validate_inputs(spec, inputs)

        start = time.perf_counter()
        model = get_model(domain, subdomain, model_id)
        predictor = RuleBasedPredictor(spec, model)
        result = predictor.predict(validated)
        result.latency_ms = round((time.perf_counter() - start) * 1000, 2)

        inference_id = self.repo.save(result, user_id=user_id)
        result.inference_id = inference_id

        self._sync_legacy_run(result, user_id)
        self._record_lineage(result)
        return result

    def _record_lineage(self, result: PredictionResult) -> None:
        dataset_id = result.metadata.get("synthetic_dataset_id")
        scenario_id = result.metadata.get("scenario_id")
        if scenario_id and dataset_id:
            self.lineage.record_edge(
                "scenario", scenario_id, "synthetic_dataset", dataset_id, "generated"
            )
        if dataset_id:
            self.lineage.record_edge(
                "synthetic_dataset", dataset_id, "inference", result.inference_id, "feeds"
            )

    def predict_batch(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        input_sets: list[dict[str, Any]],
        user_id: str | None = None,
    ) -> tuple[str, list[PredictionResult]]:
        batch_id = str(uuid.uuid4())[:12]
        results: list[PredictionResult] = []

        for raw in input_sets:
            result = self.predict(domain, subdomain, model_id, raw, user_id)
            results.append(result)

        self.repo.save_batch(batch_id, domain, subdomain, model_id, [r.inference_id for r in results], user_id)
        return batch_id, results

    def get(self, inference_id: str) -> dict[str, Any] | None:
        return self.repo.get(inference_id)

    def list_recent(self, domain: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.repo.list_recent(domain=domain, limit=limit)

    def _sync_legacy_run(self, result: PredictionResult, user_id: str | None) -> None:
        """Keep simulation_runs populated for history/export compatibility."""
        from khukra.core.model import ModelResult

        legacy = ModelResult(
            domain=result.domain,
            subdomain=result.subdomain,
            model_name=result.model_id,
            parameters=result.inputs,
            metrics=result.predictions_flat(),
            series=result.traces,
            metadata={**result.metadata, "inference_id": result.inference_id},
        )
        self.repo.runs.save(legacy, run_id=result.inference_id, user_id=user_id)


def get_inference_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine


__all__ = ["InferenceEngine", "get_inference_engine", "InputValidationError", "model_key"]
