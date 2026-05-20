"""Platform workspace manifest - drives dynamic UI navigation and capabilities."""

from __future__ import annotations

from typing import Any

PLATFORM_MODULES: list[dict[str, Any]] = [
    {
        "id": "overview",
        "label": "Overview",
        "description": "Platform health snapshot and module launcher.",
        "route_id": "overview",
        "icon": "layout-dashboard",
        "order": 0,
        "capabilities": ["summary", "navigation"],
        "actions": [],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "data_generation",
        "label": "Data Generation",
        "description": "Create and inspect synthetic datasets from catalog models.",
        "route_id": "data_generation",
        "icon": "database",
        "order": 1,
        "capabilities": ["catalog", "generate", "dataset_preview", "sql_preview"],
        "actions": [
            {"id": "generate", "label": "Generate synthetic dataset", "endpoint": "/api/platform/data-generation"},
            {"id": "preview_sql", "label": "Preview with SQL", "endpoint": "/api/platform/analytics"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "mlops",
        "label": "MLOps",
        "description": "Orchestrate synthetic to inference to registry to evaluation to lineage.",
        "route_id": "mlops",
        "icon": "workflow",
        "order": 2,
        "capabilities": ["pipeline_templates", "jobs", "artifacts", "evaluations"],
        "actions": [
            {"id": "run_pipeline", "label": "Run full pipeline", "endpoint": "/api/platform/mlops/pipeline"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "ml_inference",
        "label": "ML Inferencing",
        "description": "Run registered forecasting models with schema-validated inputs.",
        "route_id": "ml_inference",
        "icon": "brain-circuit",
        "order": 3,
        "capabilities": ["model_catalog", "predict", "traces", "predictions"],
        "actions": [
            {"id": "predict", "label": "Run ML inference", "endpoint": "/api/platform/ml-inference"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "analytics",
        "label": "Analytics",
        "description": "Read-only DuckDB SQL against warehouse tables and Parquet files.",
        "route_id": "analytics",
        "icon": "bar-chart",
        "order": 4,
        "capabilities": ["sql_editor", "table_catalog", "query_examples"],
        "actions": [
            {"id": "run_query", "label": "Run SQL", "endpoint": "/api/platform/analytics"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "insights",
        "label": "Insights",
        "description": "Warehouse health, registry status, evaluations, and ML readiness summaries.",
        "route_id": "insights",
        "icon": "brain",
        "order": 5,
        "capabilities": ["health_cards", "explain", "artifacts", "evaluations"],
        "actions": [
            {"id": "explain", "label": "Explain target", "endpoint": "/api/platform/insights/explain"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
]


class PlatformManifestService:
    def build(self) -> dict[str, Any]:
        return {
            "version": "1.0",
            "workspace": "platform",
            "feature_flags": {
                "dynamic_navigation": True,
                "dynamic_forms": True,
                "dataset_to_inference": True,
                "pipeline_templates": True,
            },
            "modules": [m for m in PLATFORM_MODULES if m.get("enabled", True)],
        }
