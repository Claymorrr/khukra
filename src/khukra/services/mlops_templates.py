"""MLOps pipeline template metadata for dynamic platform controls."""

from __future__ import annotations

from typing import Any

PIPELINE_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "generate_only",
        "label": "Generate synthetic data",
        "description": "Run domain model with persist_synthetic; no inference or registry.",
        "endpoint": "/api/platform/data-generation",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": ["seed", "history_length", "forecast_horizon", "persist_synthetic"],
        "expected_outputs": ["scenario_id", "synthetic_dataset_id", "validation", "metrics"],
    },
    {
        "id": "inference_only",
        "label": "ML inference only",
        "description": "Execute a single validated prediction without full MLOps orchestration.",
        "endpoint": "/api/platform/ml-inference",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": ["seed", "history_length", "forecast_horizon"],
        "expected_outputs": ["inference_id", "predictions", "traces", "metadata"],
    },
    {
        "id": "full_pipeline",
        "label": "Full MLOps pipeline",
        "description": "Synthetic → inference → artifact registry → evaluation → lineage.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": ["seed", "history_length", "forecast_horizon"],
        "expected_outputs": [
            "job_id",
            "inference_id",
            "synthetic_dataset_id",
            "artifact_id",
            "evaluation_run_id",
            "passed",
        ],
    },
    {
        "id": "evaluate_artifact",
        "label": "Evaluate artifact (via full pipeline)",
        "description": "Runs full pipeline to produce artifact and holdout evaluation.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": [],
        "expected_outputs": ["artifact_id", "evaluation_run_id", "passed"],
    },
]


class MLOpsTemplateService:
    def list_templates(self) -> list[dict[str, Any]]:
        return PIPELINE_TEMPLATES
