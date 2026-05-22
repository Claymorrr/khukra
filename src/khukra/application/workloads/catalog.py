"""Workload catalog — maps domain models to operating-environment metadata."""

from __future__ import annotations

from typing import Any, Literal

from khukra.domains.registry import DOMAINS, SUBDOMAIN_LABELS, list_domains, list_models, list_subdomains
from khukra.inference.registry import get_spec, model_key

LifecycleStage = Literal["develop", "validate", "package", "operate"]
WorkloadKind = Literal[
    "simulation",
    "solver",
    "inference",
    "backtest",
    "forecast",
    "dynamic_simulation",
]

DOMAIN_VERBS: dict[str, str] = {
    "physical": "Solve",
    "finance": "Run",
    "supply_chain": "Simulate",
    "intelligence": "Analyze",
    "computing": "Simulate",
}

# model_id -> workload metadata overrides
_WORKLOAD_META: dict[str, dict[str, Any]] = {
    # physical
    "cantilever_beam": {"kind": "solver", "stage": "develop", "operation_verb": "Solve"},
    "damped_oscillator": {"kind": "dynamic_simulation", "stage": "develop", "operation_verb": "Simulate"},
    "counterflow_heat_exchanger": {"kind": "solver", "stage": "develop", "operation_verb": "Solve"},
    "point_mass_2d": {"kind": "dynamic_simulation", "stage": "develop", "operation_verb": "Simulate"},
    # finance delivery / backtest
    "strategy_backtest_validation": {"kind": "backtest", "stage": "validate"},
    "sharpe_ratio_backtest": {"kind": "backtest", "stage": "validate"},
    "strategy_release_readiness": {"kind": "inference", "stage": "package"},
    "paper_trading_delivery_gate": {"kind": "inference", "stage": "operate"},
    "execution_slippage_sim": {"kind": "simulation", "stage": "develop"},
    "paper_order_fill_sim": {"kind": "simulation", "stage": "validate"},
}

_DOMAIN_DEFAULT_KIND: dict[str, WorkloadKind] = {
    "physical": "solver",
    "finance": "algorithm",
    "supply_chain": "simulation",
    "intelligence": "forecast",
    "computing": "forecast",
}


def _infer_kind(domain: str, model_id: str, spec_kind: str | None) -> str:
    if model_id in _WORKLOAD_META:
        return _WORKLOAD_META[model_id].get("kind", "inference")
    if domain == "physical" and spec_kind in ("solver", "dynamic_simulation"):
        return spec_kind
    if "backtest" in model_id or "validation" in model_id:
        return "backtest"
    if "sim" in model_id or domain == "supply_chain":
        return "simulation"
    return _DOMAIN_DEFAULT_KIND.get(domain, "inference")


def _infer_stage(domain: str, model_id: str, kind: str) -> LifecycleStage:
    if model_id in _WORKLOAD_META and _WORKLOAD_META[model_id].get("stage"):
        return _WORKLOAD_META[model_id]["stage"]
    if kind == "backtest" or "validation" in model_id or "readiness" in model_id or "gate" in model_id:
        return "validate"
    if "delivery" in model_id or "paper" in model_id:
        return "operate"
    if domain == "finance" and kind == "inference":
        return "develop"
    return "develop"


def build_workload_entry(domain: str, subdomain: str, model_id: str) -> dict[str, Any]:
    spec = get_spec(domain, subdomain, model_id)
    kind = _infer_kind(domain, model_id, spec.model_kind)
    stage = _infer_stage(domain, model_id, kind)
    verb = _WORKLOAD_META.get(model_id, {}).get("operation_verb") or DOMAIN_VERBS.get(domain, "Run")
    validation_gates = _validation_gates(domain, model_id, kind)
    return {
        "workload_id": model_key(domain, subdomain, model_id),
        "domain": domain,
        "subdomain": subdomain,
        "model_id": model_id,
        "label": spec.label,
        "description": spec.description,
        "version": spec.version,
        "workload_kind": kind,
        "lifecycle_stage": stage,
        "operation_verb": verb,
        "predictor_type": spec.predictor_type,
        "supports_uncertainty": spec.supports_uncertainty,
        "validation_gates": validation_gates,
        "default_parameters": {f.name: f.default for f in spec.feature_schema},
        "output_fields": [{"name": o.name, "label": o.label, "unit": o.unit} for o in spec.output_schema],
    }


def _validation_gates(domain: str, model_id: str, kind: str) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    if domain == "physical":
        gates.append({"id": "solver_residual", "label": "Solver residual within tolerance", "metric": "max_residual"})
        if kind == "solver":
            gates.append({"id": "energy_balance", "label": "Energy / force balance check", "metric": "balance_ok"})
    if domain == "finance":
        if kind == "backtest" or "validation" in model_id:
            gates.extend(
                [
                    {"id": "sharpe_min", "label": "Sharpe ratio threshold", "metric": "sharpe_ratio", "threshold": 0.5},
                    {"id": "drawdown_cap", "label": "Max drawdown cap", "metric": "max_drawdown", "threshold": 0.25},
                ]
            )
        if "readiness" in model_id or "gate" in model_id:
            gates.append({"id": "readiness_gate", "label": "Release readiness gate", "metric": "readiness_score"})
    if domain == "supply_chain":
        gates.append({"id": "quality_contract", "label": "Data contract quality", "metric": "forecast_mae"})
    gates.append({"id": "execution_complete", "label": "Run completed successfully", "metric": "execution_status"})
    return gates


def list_domain_workloads(domain: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if domain not in DOMAINS:
        return out
    for subdomain in list_subdomains(domain):
        for model_id in list_models(domain, subdomain):
            out.append(build_workload_entry(domain, subdomain, model_id))
    return out


def domain_environment_summary(domain: str) -> dict[str, Any]:
    workloads = list_domain_workloads(domain)
    by_stage: dict[str, int] = {"develop": 0, "validate": 0, "package": 0, "operate": 0}
    by_kind: dict[str, int] = {}
    for w in workloads:
        by_stage[w["lifecycle_stage"]] = by_stage.get(w["lifecycle_stage"], 0) + 1
        k = w["workload_kind"]
        by_kind[k] = by_kind.get(k, 0) + 1
    return {
        "domain": domain,
        "operation_verb": DOMAIN_VERBS.get(domain, "Run"),
        "subdomains": [
            {"id": sid, "label": SUBDOMAIN_LABELS[domain][sid], "workload_count": len(list_models(domain, sid))}
            for sid in list_subdomains(domain)
        ],
        "workloads": workloads,
        "totals": {"workloads": len(workloads), "by_stage": by_stage, "by_kind": by_kind},
    }


def list_all_environments() -> list[dict[str, Any]]:
    return [domain_environment_summary(d) for d in list_domains()]
