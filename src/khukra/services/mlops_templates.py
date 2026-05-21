"""MLOps pipeline template metadata — versioned, domain-filterable."""

from __future__ import annotations

from typing import Any

from khukra.versioning.service import get_version_registry

PIPELINE_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "generate_only",
        "version": "1.0.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "label": "Generate synthetic data",
        "description": "Run domain model with persist_synthetic; registers data product.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": ["seed", "history_length", "forecast_horizon"],
        "expected_outputs": ["workflow_run_id", "synthetic_dataset_id", "product_id", "validation"],
    },
    {
        "id": "aerodesign_design_space",
        "version": "1.0.0",
        "domains": ["physical"],
        "label": "Aerodesign design-space generation",
        "description": "Synthetic aerodynamic performance datasets for design-space exploration.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {"domain": "physical", "subdomain": "aerodesign", "model": "aerodynamic_performance_forecast"},
        "expected_outputs": ["product_id", "validation"],
    },
    {
        "id": "aerodesign_full_mlops",
        "version": "1.0.0",
        "domains": ["physical"],
        "label": "Aerodesign full MLOps",
        "description": "Generate → infer → registry → evaluate with lineage.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "expected_outputs": ["artifact_id", "evaluation_run_id", "passed"],
    },
    {
        "id": "quant_market_scenario",
        "version": "1.0.0",
        "domains": ["finance"],
        "label": "Quant market scenario",
        "description": "Synthetic microstructure / arbitrage scenarios for quant research.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {"domain": "finance", "subdomain": "market_microstructure", "model": "lob_liquidity_forecast"},
        "expected_outputs": ["product_id", "validation"],
    },
    {
        "id": "quant_signal_eval",
        "version": "1.0.0",
        "domains": ["finance"],
        "label": "Quant signal evaluation pipeline",
        "description": "Full pipeline with execution-risk evaluation artifacts.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "expected_outputs": ["artifact_id", "evaluation_run_id"],
    },
    {
        "id": "inference_only",
        "version": "1.0.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "label": "ML inference only",
        "description": "Single validated prediction via workflow infer.",
        "endpoint": "/api/v1/workflows/infer",
        "required_inputs": ["domain", "subdomain", "model"],
        "expected_outputs": ["workflow_run_id", "inference_id"],
    },
    {
        "id": "full_pipeline",
        "version": "1.1.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "label": "Full MLOps pipeline",
        "description": "Synthetic → inference → artifact → evaluation → lineage.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "expected_outputs": [
            "job_id",
            "inference_id",
            "synthetic_dataset_id",
            "product_id",
            "artifact_id",
            "evaluation_run_id",
            "passed",
        ],
    },
]


class MLOpsTemplateService:
    def __init__(self) -> None:
        self.versions = get_version_registry()
        for tpl in PIPELINE_TEMPLATES:
            self.versions.register(
                "pipeline_template",
                tpl["id"],
                tpl.get("version", "1.0.0"),
                metadata={"domains": tpl.get("domains", [])},
            )

    def list_templates(self, domain: str | None = None) -> list[dict[str, Any]]:
        if not domain:
            return list(PIPELINE_TEMPLATES)
        return [
            t
            for t in PIPELINE_TEMPLATES
            if domain in t.get("domains", []) or not t.get("domains")
        ]
