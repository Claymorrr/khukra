from typing import Any

from khukra.domains.registry import DOMAINS, SUBDOMAIN_LABELS, get_model
from khukra.inference.types import FeatureField, InferenceModelSpec, OutputField

_COMMON_OUTPUTS = [
    ("forecast_mae", "Forecast MAE", ""),
    ("forecast_rmse", "Forecast RMSE", ""),
    ("final_level", "Final forecast level", ""),
    ("trend_slope", "Trend slope", "/step"),
]

_MODEL_META: dict[str, dict[str, Any]] = {
    "turbomachinery_health_forecast": {"type": "stochastic_degradation_jump_diffusion", "uncertainty": True},
    "combustion_instability_forecast": {"type": "stochastic_regime_hawkes_combustion", "uncertainty": True},
    "hybrid_propulsion_mission_forecast": {"type": "stochastic_control_regime_forecast", "uncertainty": True},
    "lob_liquidity_forecast": {"type": "stochastic_microstructure_hawkes", "uncertainty": True},
    "spread_mean_reversion_forecast": {"type": "stochastic_arbitrage_regime_jump", "uncertainty": True},
    "execution_slippage_forecast": {"type": "stochastic_execution_cost_process", "uncertainty": True},
    "defect_rate_forecast": {"type": "stochastic_quality_drift_process", "uncertainty": True},
    "disruption_risk_forecast": {"type": "stochastic_hawkes_disruption_process", "uncertainty": True},
    "recovery_time_forecast": {"type": "stochastic_resilience_shock_process", "uncertainty": True},
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
        supports_uncertainty=True,
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
