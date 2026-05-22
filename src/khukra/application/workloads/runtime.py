"""Workload execution lifecycle: develop, validate, package, operate."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from khukra.application.workloads.catalog import build_workload_entry, domain_environment_summary, list_domain_workloads
from khukra.data.repositories.artifacts import ArtifactRepository
from khukra.data.repositories.evaluations import EvaluationRepository
from khukra.inference.engine import get_inference_engine
from khukra.services.audit import audit_action
from khukra.services.mlops_pipeline import MLOpsPipeline


class WorkloadUseCases:
    def __init__(self) -> None:
        self.engine = get_inference_engine()
        self.pipeline = MLOpsPipeline()
        self.artifacts = ArtifactRepository()
        self.evaluations = EvaluationRepository()

    def get_environment(self, domain: str) -> dict[str, Any]:
        return domain_environment_summary(domain)

    def list_workloads(
        self,
        domain: str,
        lifecycle_stage: str | None = None,
        workload_kind: str | None = None,
    ) -> dict[str, Any]:
        workloads = list_domain_workloads(domain)
        if lifecycle_stage:
            workloads = [w for w in workloads if w["lifecycle_stage"] == lifecycle_stage]
        if workload_kind:
            workloads = [w for w in workloads if w["workload_kind"] == workload_kind]
        return {"domain": domain, "workloads": workloads, "total": len(workloads)}

    def get_workload(self, domain: str, subdomain: str, model_id: str) -> dict[str, Any]:
        entry = build_workload_entry(domain, subdomain, model_id)
        if entry["domain"] != domain:
            raise HTTPException(404, "Workload not found in domain")
        return entry

    def develop(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute workload (inference run / simulation / solver)."""
        result = self.engine.predict(domain, subdomain, model_id, inputs, user_id=user_id)
        audit_action(
            "workload.develop",
            "workload_run",
            result.inference_id,
            user_id=user_id,
            metadata={"domain": domain, "model_id": model_id},
        )
        return self._format_run_result(domain, subdomain, model_id, result)

    def validate(self, domain: str, inference_id: str) -> dict[str, Any]:
        row = self.engine.get(inference_id)
        if not row:
            raise HTTPException(404, "Workload run not found")
        if row.get("domain") != domain:
            raise HTTPException(404, "Run not in domain")
        metrics = {
            k: (v.get("value") if isinstance(v, dict) else v)
            for k, v in (row.get("predictions") or {}).items()
        }
        workload = build_workload_entry(domain, row["subdomain"], row["model_id"])
        checks = []
        passed = True
        for gate in workload.get("validation_gates", []):
            metric = gate.get("metric")
            threshold = gate.get("threshold")
            if metric == "execution_status":
                ok = True
                value = "completed"
            elif metric and metric in metrics:
                value = metrics[metric]
                if isinstance(value, bool):
                    ok = value
                elif threshold is not None:
                    ok = float(value) <= float(threshold) if "drawdown" in metric else float(value) >= float(threshold)
                else:
                    ok = value is not None
            else:
                value = None
                ok = True
            checks.append(
                {
                    "gate_id": gate["id"],
                    "label": gate["label"],
                    "passed": ok,
                    "value": value,
                    "threshold": threshold,
                }
            )
            passed = passed and ok
        return {
            "inference_id": inference_id,
            "domain": domain,
            "passed": passed,
            "checks": checks,
            "metrics": metrics,
            "lifecycle_stage": "validate",
        }

    def package(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inference_id: str,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        validation = self.validate(domain, inference_id)
        if not validation["passed"]:
            raise HTTPException(400, "Validation gates failed; cannot package workload")
        row = self.engine.get(inference_id)
        if not row:
            raise HTTPException(404, "Workload run not found")
        metrics = {
            k: (v.get("value") if isinstance(v, dict) else v)
            for k, v in (row.get("predictions") or {}).items()
        }
        artifact_id = self.artifacts.register(
            domain,
            subdomain,
            model_id,
            row.get("model_version", "1.0.0"),
            metrics,
            metadata={"inference_id": inference_id, "packaged": True},
            user_id=user_id,
        )
        audit_action(
            "workload.package",
            "artifact",
            artifact_id,
            user_id=user_id,
            metadata={"inference_id": inference_id},
        )
        return {
            "artifact_id": artifact_id,
            "inference_id": inference_id,
            "validation": validation,
            "lifecycle_stage": "package",
            "promotion_state": "candidate",
        }

    def operate(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Full lifecycle pipeline: run → validate → package → evaluate."""
        run = self.develop(domain, subdomain, model_id, inputs, user_id=user_id)
        validation = self.validate(domain, run["inference_id"])
        package_result = None
        if validation["passed"]:
            try:
                package_result = self.package(
                    domain, subdomain, model_id, run["inference_id"], user_id=user_id
                )
            except HTTPException:
                package_result = {"error": "packaging_failed", "validation": validation}
        pipeline_result = None
        try:
            pipeline_result = self.pipeline.run_full_pipeline(
                domain, subdomain, model_id, inputs, user_id=user_id
            )
        except Exception as exc:
            pipeline_result = {"error": str(exc)}
        recent = self.engine.list_recent(domain=domain, limit=10)
        return {
            "domain": domain,
            "develop": run,
            "validate": validation,
            "package": package_result,
            "lifecycle_pipeline": pipeline_result,
            "recent_runs": recent,
            "lifecycle_stage": "operate",
        }

    def run_lifecycle_pipeline(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return self.pipeline.run_full_pipeline(domain, subdomain, model_id, inputs, user_id)

    @staticmethod
    def _format_run_result(domain: str, subdomain: str, model_id: str, result: Any) -> dict[str, Any]:
        preds = result.predictions_flat()
        return {
            "inference_id": result.inference_id,
            "domain": domain,
            "subdomain": subdomain,
            "model_id": model_id,
            "latency_ms": result.latency_ms,
            "predictions": preds,
            "traces": result.traces,
            "metadata": result.metadata,
            "lifecycle_stage": "develop",
            "workload_kind": build_workload_entry(domain, subdomain, model_id)["workload_kind"],
        }
