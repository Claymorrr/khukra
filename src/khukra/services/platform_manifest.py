"""Platform workspace manifest - drives dynamic UI navigation and capabilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from khukra.domains.meta import DOMAIN_ICONS, DOMAIN_META
from khukra.domains.registry import list_domains

_PLUGINS_PATH = Path(__file__).resolve().parents[3] / "config" / "plugins.json"

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
        "id": "infraops",
        "label": "InfraOps",
        "description": "Inspect warehouse health, runtime readiness, storage, and service signals.",
        "route_id": "infraops",
        "icon": "server",
        "order": 3,
        "capabilities": ["warehouse_health", "runtime_status", "storage", "service_readiness"],
        "actions": [
            {"id": "ops_summary", "label": "Review ops summary", "endpoint": "/api/platform/ops/summary"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
    {
        "id": "devops",
        "label": "DevOps",
        "description": "Review release readiness, environment config, and delivery signals.",
        "route_id": "devops",
        "icon": "git-branch",
        "order": 4,
        "capabilities": ["release_readiness", "environment_config", "job_health"],
        "actions": [
            {"id": "ops_summary", "label": "Review ops summary", "endpoint": "/api/platform/ops/summary"},
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
        "order": 5,
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
        "order": 6,
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
        "order": 7,
        "capabilities": ["health_cards", "explain", "artifacts", "evaluations"],
        "actions": [
            {"id": "explain", "label": "Explain target", "endpoint": "/api/platform/insights/explain"},
        ],
        "required_roles": ["analyst", "admin"],
        "enabled": True,
    },
]


def _load_plugin_modules() -> list[dict[str, Any]]:
    if not _PLUGINS_PATH.is_file():
        return []
    try:
        raw = json.loads(_PLUGINS_PATH.read_text(encoding="utf-8"))
        return [m for m in raw if isinstance(m, dict) and m.get("enabled", True)]
    except (json.JSONDecodeError, OSError):
        return []


class PlatformManifestService:
    def _build_domains(self) -> list[dict[str, Any]]:
        domains: list[dict[str, Any]] = []
        for order, domain_id in enumerate(list_domains()):
            meta = DOMAIN_META[domain_id]
            domains.append(
                {
                    "id": domain_id,
                    "label": meta["label"],
                    "color": meta["color"],
                    "icon": DOMAIN_ICONS.get(domain_id, "box"),
                    "order": order,
                }
            )
        return domains

    def build(self) -> dict[str, Any]:
        plugins = _load_plugin_modules()
        base = [m for m in PLATFORM_MODULES if m.get("enabled", True)]
        seen = {m["id"] for m in base}
        merged = list(base)
        for plug in plugins:
            if plug.get("id") not in seen:
                merged.append(plug)
                seen.add(plug["id"])
        merged.sort(key=lambda m: m.get("order", 99))
        return {
            "version": "1.1",
            "workspace": "platform",
            "feature_flags": {
                "dynamic_navigation": True,
                "domain_first_navigation": True,
                "dynamic_forms": True,
                "dataset_to_inference": True,
                "pipeline_templates": True,
                "integrated_ops": True,
                "plugin_modules": bool(plugins),
            },
            "domains": self._build_domains(),
            "modules": merged,
            "plugins": plugins,
        }
