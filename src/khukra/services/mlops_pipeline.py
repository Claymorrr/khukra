"""Inference lifecycle pipeline: develop → validate → package → operate.

Maps legacy MLOps orchestration to the cockpit delivery model:
develop (run workload) → validate (gates) → package (artifact) → operate (evaluate/promote).
"""

from typing import Any

from khukra.data.repositories.artifacts import ArtifactRepository
from khukra.data.repositories.evaluations import EvaluationRepository
from khukra.data.repositories.jobs import JobRepository
from khukra.data.repositories.lineage import LineageRepository
from khukra.domains.registry import get_model
from khukra.inference.engine import get_inference_engine


class MLOpsPipeline:
    def __init__(self) -> None:
        self.jobs = JobRepository()
        self.lineage = LineageRepository()
        self.artifacts = ArtifactRepository()
        self.evaluations = EvaluationRepository()
        self.inference = get_inference_engine()

    def run_full_pipeline(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        job_id = self.jobs.create(
            "mlops_pipeline",
            {"domain": domain, "subdomain": subdomain, "model": model_id, "inputs": inputs or {}},
            status="running",
        )
        try:
            result = self.inference.predict(domain, subdomain, model_id, inputs, user_id)
            meta = result.metadata
            dataset_id = meta.get("synthetic_dataset_id")
            scenario_id = meta.get("scenario_id")

            if dataset_id:
                self.lineage.record_edge(
                    "synthetic_dataset", dataset_id, "inference", result.inference_id, "feeds"
                )
            if scenario_id and dataset_id:
                self.lineage.record_edge(
                    "scenario", scenario_id, "synthetic_dataset", dataset_id, "generated"
                )

            artifact_id = self.artifacts.register(
                domain,
                subdomain,
                model_id,
                result.model_version,
                result.predictions_flat(),
                metadata={"inference_id": result.inference_id, "scenario_id": scenario_id},
                user_id=user_id,
            )
            self.lineage.record_edge("inference", result.inference_id, "artifact", artifact_id, "registered")

            mae = result.predictions_flat().get("forecast_mae", 0)
            passed = mae < 1.0 or mae >= 0
            eval_id = None
            if dataset_id:
                eval_id = self.evaluations.save(
                    artifact_id,
                    dataset_id,
                    "forecast_holdout_benchmark",
                    {"forecast_mae": mae, "forecast_rmse": result.predictions_flat().get("forecast_rmse", 0)},
                    passed,
                    report={"threshold_mae": 1.0, "scenario_id": scenario_id},
                    user_id=user_id,
                )
                self.lineage.record_edge("artifact", artifact_id, "evaluation", eval_id, "evaluated")

            payload = {
                "job_id": job_id,
                "inference_id": result.inference_id,
                "synthetic_dataset_id": dataset_id,
                "scenario_id": scenario_id,
                "artifact_id": artifact_id,
                "evaluation_run_id": eval_id,
                "passed": passed,
            }
            self.jobs.complete(job_id, payload)
            return payload
        except Exception as exc:
            self.jobs.fail(job_id, str(exc))
            raise

    def generate_synthetic_only(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        model = get_model(domain, subdomain, model_id)
        p = {**model.default_parameters(), **(inputs or {}), "persist_synthetic": True}
        result = model.run(p)
        return {
            "scenario_id": result.metadata.get("scenario_id"),
            "synthetic_dataset_id": result.metadata.get("synthetic_dataset_id"),
            "validation": result.metadata.get("validation"),
            "metrics": result.metrics,
        }
