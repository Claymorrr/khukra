"""Inference lifecycle ops templates — develop, validate, package, operate."""

from __future__ import annotations

from typing import Any

from khukra.versioning.service import get_version_registry

LIFECYCLE_STAGES = ("develop", "validate", "package", "operate")

PIPELINE_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "generate_only",
        "version": "1.0.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "lifecycle_stage": "develop",
        "label": "Develop — generate domain data",
        "description": "Run workload with persist_synthetic; registers domain data plane asset.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "optional_inputs": ["seed", "history_length", "forecast_horizon"],
        "expected_outputs": ["workflow_run_id", "synthetic_dataset_id", "product_id", "validation"],
    },
    {
        "id": "physics_solver_sweep",
        "version": "1.0.0",
        "domains": ["physical"],
        "lifecycle_stage": "develop",
        "label": "Develop — physics solver sweep",
        "description": "Run mechanics/thermofluid/dynamics solver and register simulation traces.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {"domain": "physical", "subdomain": "mechanics", "model": "cantilever_beam"},
        "expected_outputs": ["product_id", "validation"],
    },
    {
        "id": "physics_surrogate_mlops",
        "version": "1.0.0",
        "domains": ["physical"],
        "lifecycle_stage": "operate",
        "label": "Operate — physics surrogate lifecycle",
        "description": "Develop run → validate → package artifact → evaluate for surrogate candidates.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {"domain": "physical", "subdomain": "thermofluid", "model": "counterflow_heat_exchanger"},
        "expected_outputs": ["artifact_id", "evaluation_run_id", "passed"],
    },
    {
        "id": "quant_research_loop",
        "version": "2.0.0",
        "domains": ["finance"],
        "lifecycle_stage": "develop",
        "label": "Develop — quant research loop",
        "description": "Market scenario generation → signal research → experiment artifact.",
        "endpoint": "/api/v1/workflows/generate",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {
            "domain": "finance",
            "subdomain": "market_research",
            "model": "market_scenario_research",
        },
        "expected_outputs": ["product_id", "validation", "synthetic_dataset_id"],
    },
    {
        "id": "strategy_backtest_gate",
        "version": "2.0.0",
        "domains": ["finance"],
        "lifecycle_stage": "validate",
        "label": "Validate — strategy backtest gate",
        "description": "Signal bundle → backtest validation → Sharpe/drawdown threshold check.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {
            "domain": "finance",
            "subdomain": "strategy_backtesting",
            "model": "strategy_backtest_validation",
        },
        "expected_outputs": ["artifact_id", "evaluation_run_id", "passed"],
    },
    {
        "id": "paper_trading_delivery",
        "version": "2.0.0",
        "domains": ["finance"],
        "lifecycle_stage": "operate",
        "label": "Operate — paper trading delivery",
        "description": "Validated strategy → execution simulation → paper release candidate.",
        "endpoint": "/api/platform/mlops/pipeline",
        "required_inputs": ["domain", "subdomain", "model"],
        "default": {
            "domain": "finance",
            "subdomain": "strategy_delivery",
            "model": "paper_trading_delivery_gate",
        },
        "expected_outputs": ["artifact_id", "evaluation_run_id", "readiness_score", "gate_passed"],
    },
    {
        "id": "inference_only",
        "version": "1.0.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "lifecycle_stage": "develop",
        "label": "Develop — inference run",
        "description": "Single workload execution via workflow infer (execution runtime).",
        "endpoint": "/api/v1/workflows/infer",
        "required_inputs": ["domain", "subdomain", "model"],
        "expected_outputs": ["workflow_run_id", "inference_id"],
    },
    {
        "id": "full_pipeline",
        "version": "1.1.0",
        "domains": ["physical", "finance", "supply_chain", "intelligence", "computing"],
        "lifecycle_stage": "operate",
        "label": "Operate — full lifecycle pipeline",
        "description": "Develop → validate → package → evaluate with lineage on the domain data plane.",
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
