from typing import Any

from khukra.domains.registry import DOMAINS, SUBDOMAIN_LABELS, get_model
from khukra.inference.types import FeatureField, InferenceModelSpec, OutputField

_COMMON_OUTPUTS = [
    ("forecast_mae", "Forecast MAE", ""),
    ("forecast_rmse", "Forecast RMSE", ""),
    ("final_level", "Final forecast level", ""),
    ("trend_slope", "Trend slope", "/step"),
]

_FORECAST_OUTPUTS = [
    ("forecast_mae", "Forecast MAE", ""),
    ("forecast_rmse", "Forecast RMSE", ""),
    ("final_level", "Final forecast level", ""),
    ("trend_slope", "Trend slope", "/step"),
]

def _physical_model_meta() -> dict[str, dict[str, Any]]:
    from khukra.domains.physical.models_registry import SOLVER_SPECS, inference_meta_for

    return {model_id: inference_meta_for(model_id) for model_id in SOLVER_SPECS}


_FINANCE_OUTPUTS: dict[str, list[tuple[str, str, str]]] = {
    "market": [
        ("forecast_mae", "Forecast MAE", ""),
        ("liquidity_score", "Liquidity score", ""),
        ("regime_volatility", "Regime volatility", ""),
        ("signal_score", "Signal score", ""),
    ],
    "signal": [
        ("forecast_mae", "Forecast MAE", ""),
        ("signal_score", "Signal score", ""),
        ("expected_return", "Expected return (annualized proxy)", ""),
        ("half_life_bars", "Alpha half-life (bars)", ""),
    ],
    "backtest": [
        ("forecast_mae", "Forecast MAE", ""),
        ("sharpe_ratio", "Sharpe ratio", ""),
        ("hit_rate", "Hit rate", ""),
        ("max_drawdown", "Max drawdown", ""),
        ("turnover_proxy", "Turnover proxy", ""),
        ("exposure", "Exposure", ""),
    ],
    "execution": [
        ("forecast_mae", "Forecast MAE", ""),
        ("slippage_bps", "Slippage (bps proxy)", ""),
        ("fill_rate", "Fill rate", ""),
        ("market_impact_proxy", "Market impact proxy", ""),
    ],
    "risk": [
        ("forecast_mae", "Forecast MAE", ""),
        ("max_drawdown", "Max drawdown", ""),
        ("var_proxy", "VaR proxy", ""),
        ("risk_envelope", "Risk envelope", ""),
    ],
    "delivery": [
        ("forecast_mae", "Forecast MAE", ""),
        ("readiness_score", "Readiness score", ""),
        ("gate_passed", "Gate passed", ""),
        ("release_status", "Release status", ""),
    ],
    "allocation": [
        ("portfolio_return", "Portfolio return", ""),
        ("portfolio_risk", "Portfolio risk", ""),
        ("sharpe_ratio", "Sharpe ratio", ""),
        ("max_drawdown", "Max drawdown", ""),
        ("var_proxy", "VaR proxy", ""),
    ],
}

_FINANCE_MODEL_META: dict[str, dict[str, Any]] = {
    "market_scenario_research": {
        "type": "trading_market_scenario",
        "lifecycle": "market",
        "outputs": _FINANCE_OUTPUTS["market"],
    },
    "liquidity_regime_forecast": {
        "type": "trading_liquidity_regime",
        "lifecycle": "market",
        "outputs": _FINANCE_OUTPUTS["market"],
    },
    "spread_signal_research": {
        "type": "trading_stat_arb_signal",
        "lifecycle": "signal",
        "outputs": _FINANCE_OUTPUTS["signal"],
    },
    "alpha_decay_signal": {
        "type": "trading_alpha_decay",
        "lifecycle": "signal",
        "outputs": _FINANCE_OUTPUTS["signal"],
    },
    "strategy_backtest_validation": {
        "type": "trading_backtest_validation",
        "lifecycle": "backtest",
        "outputs": _FINANCE_OUTPUTS["backtest"],
    },
    "sharpe_ratio_backtest": {
        "type": "trading_sharpe_backtest",
        "lifecycle": "backtest",
        "outputs": _FINANCE_OUTPUTS["backtest"],
    },
    "execution_slippage_sim": {
        "type": "trading_execution_slippage",
        "lifecycle": "execution",
        "outputs": _FINANCE_OUTPUTS["execution"],
    },
    "paper_order_fill_sim": {
        "type": "trading_paper_fill",
        "lifecycle": "execution",
        "outputs": _FINANCE_OUTPUTS["execution"],
    },
    "drawdown_envelope_risk": {
        "type": "trading_drawdown_risk",
        "lifecycle": "risk",
        "outputs": _FINANCE_OUTPUTS["risk"],
    },
    "portfolio_risk_envelope": {
        "type": "trading_portfolio_risk",
        "lifecycle": "risk",
        "outputs": _FINANCE_OUTPUTS["risk"],
    },
    "portfolio_allocation_optimizer": {
        "type": "trading_portfolio_optimizer",
        "lifecycle": "risk",
        "outputs": _FINANCE_OUTPUTS["allocation"],
        "uncertainty": False,
    },
    "strategy_release_readiness": {
        "type": "trading_release_readiness",
        "lifecycle": "delivery",
        "outputs": _FINANCE_OUTPUTS["delivery"],
    },
    "paper_trading_delivery_gate": {
        "type": "trading_paper_delivery_gate",
        "lifecycle": "delivery",
        "outputs": _FINANCE_OUTPUTS["delivery"],
    },
}

_MODEL_META: dict[str, dict[str, Any]] = {
    **_physical_model_meta(),
    **_FINANCE_MODEL_META,
    "defect_rate_forecast": {
        "type": "supply_chain_quality_simulation",
        "uncertainty": True,
        "outputs": [
            ("defect_rate", "Defect rate", ""),
            ("cpk_min", "Minimum Cpk", ""),
            ("escape_risk", "Escape risk", ""),
            ("warranty_exposure_p90", "Warranty exposure P90", ""),
            ("forecast_mae", "Forecast MAE", ""),
            ("forecast_rmse", "Forecast RMSE", ""),
        ],
    },
    "disruption_risk_forecast": {
        "type": "supply_chain_disruption_simulation",
        "uncertainty": True,
        "outputs": [
            ("global_risk_index", "Global risk index", ""),
            ("expected_delay_days", "Expected delay (days)", "days"),
            ("supplier_contagion", "Supplier contagion", ""),
            ("port_delay_p95", "Port delay P95", ""),
            ("forecast_mae", "Forecast MAE", ""),
            ("forecast_rmse", "Forecast RMSE", ""),
        ],
    },
    "recovery_time_forecast": {
        "type": "supply_chain_resilience_simulation",
        "uncertainty": True,
        "outputs": [
            ("recovery_days_p50", "Recovery days P50", "days"),
            ("recovery_days_p90", "Recovery days P90", "days"),
            ("service_level_at_risk", "Service level at risk", ""),
            ("buffer_utilization", "Buffer utilization", ""),
            ("forecast_mae", "Forecast MAE", ""),
            ("forecast_rmse", "Forecast RMSE", ""),
        ],
    },
    "multi_source_detection_forecast": {"type": "stochastic_signal_fusion_belief_system", "uncertainty": True},
    "narrative_cascade_forecast": {"type": "stochastic_influence_diffusion_system", "uncertainty": True},
    "early_warning_forecast": {"type": "stochastic_adversarial_warning_system", "uncertainty": True},
    "latency_incident_forecast": {"type": "stochastic_queueing_reliability_system", "uncertainty": True},
    "gpu_throughput_forecast": {"type": "stochastic_accelerator_workload_system", "uncertainty": True},
    "edge_compute_degradation_forecast": {"type": "stochastic_cyber_physical_compute_system", "uncertainty": True},
}

for _mid, _meta in _MODEL_META.items():
    _meta.setdefault("version", "2.0.0")
    _meta.setdefault("outputs", _COMMON_OUTPUTS)


def _infer_feature_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return "string"


def _build_spec(domain: str, subdomain: str, model_id: str) -> InferenceModelSpec:
    model = get_model(domain, subdomain, model_id)
    defaults = model.default_parameters()
    meta = _MODEL_META.get(
        model_id,
        {"type": "synthetic_forecast", "version": "2.0.0", "uncertainty": True, "outputs": _COMMON_OUTPUTS},
    )
    if domain == "physical":
        from khukra.domains.physical.models_registry import model_kind

        meta = {**meta, "model_kind": meta.get("model_kind") or model_kind(model_id)}

    features = [
        FeatureField(
            name=k,
            type=_infer_feature_type(v),
            default=v,
            label=k.replace("_", " ").title(),
            required=False,
        )
        for k, v in defaults.items()
    ]

    outputs = [
        OutputField(name=name, label=label, unit=unit)
        for name, label, unit in meta.get("outputs", _COMMON_OUTPUTS)
    ]

    return InferenceModelSpec(
        domain=domain,
        subdomain=subdomain,
        model_id=model_id,
        version=meta.get("version", "2.0.0"),
        label=model_id.replace("_", " ").title(),
        predictor_type=meta.get("type", "synthetic_forecast"),
        description=SUBDOMAIN_LABELS[domain][subdomain],
        feature_schema=features,
        output_schema=outputs,
        supports_uncertainty=bool(meta.get("uncertainty", True)),
        model_kind=meta.get("model_kind"),
    )


def build_registry() -> dict[str, InferenceModelSpec]:
    registry: dict[str, InferenceModelSpec] = {}
    for domain, subdomains in DOMAINS.items():
        for subdomain, models in subdomains.items():
            for model_id in models:
                key = model_key(domain, subdomain, model_id)
                registry[key] = _build_spec(domain, subdomain, model_id)
    return registry


def model_key(domain: str, subdomain: str, model_id: str) -> str:
    return f"{domain}.{subdomain}.{model_id}"


_REGISTRY: dict[str, InferenceModelSpec] | None = None


def get_registry() -> dict[str, InferenceModelSpec]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = build_registry()
    return _REGISTRY


def get_spec(domain: str, subdomain: str, model_id: str) -> InferenceModelSpec:
    key = model_key(domain, subdomain, model_id)
    spec = get_registry().get(key)
    if not spec:
        raise KeyError(f"Unknown inference model: {key}")
    return spec


def list_specs() -> list[InferenceModelSpec]:
    return list(get_registry().values())
