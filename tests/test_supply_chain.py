"""Tests for supply chain quality, disruption, and resilience simulations."""

import pytest

from khukra.domains.registry import get_model, list_models, list_subdomains
from khukra.inference.registry import get_spec, model_key


def test_supply_chain_subdomains():
    subs = set(list_subdomains("supply_chain"))
    assert subs == {"quality_drift", "disruption_intelligence", "resilience_planning"}
    legacy = {"demand_planning", "inventory_management", "network_logistics"}
    assert subs.isdisjoint(legacy)


def test_supply_chain_model_ids():
    assert list_models("supply_chain", "quality_drift") == ["defect_rate_forecast"]
    assert list_models("supply_chain", "disruption_intelligence") == ["disruption_risk_forecast"]
    assert list_models("supply_chain", "resilience_planning") == ["recovery_time_forecast"]


@pytest.mark.parametrize(
    "subdomain,model_id,required_metrics,required_series",
    [
        (
            "quality_drift",
            "defect_rate_forecast",
            {"defect_rate", "cpk_min", "escape_risk", "warranty_exposure_p90"},
            {"defect_rate", "cpk_proxy", "escape_risk"},
        ),
        (
            "disruption_intelligence",
            "disruption_risk_forecast",
            {"global_risk_index", "expected_delay_days", "supplier_contagion", "port_delay_p95"},
            {"global_risk_index", "port_delay_index", "supplier_contagion"},
        ),
        (
            "resilience_planning",
            "recovery_time_forecast",
            {"recovery_days_p50", "recovery_days_p90", "service_level_at_risk", "buffer_utilization"},
            {"recovery_days", "buffer_level", "service_level"},
        ),
    ],
)
def test_supply_chain_runs(subdomain, model_id, required_metrics, required_series):
    result = get_model("supply_chain", subdomain, model_id).run(
        {"horizon_days": 60, "persist_synthetic": False, "seed": 1}
    )
    assert result.domain == "supply_chain"
    assert result.subdomain == subdomain
    assert result.model_name == model_id
    assert required_metrics <= set(result.metrics.keys())
    assert required_series <= set(result.series.keys())
    assert result.metadata.get("model_kind", "").endswith("_simulation")
    assert "time" in result.series
    assert len(result.series["time"]) == 60


def test_quality_metadata_persistence():
    result = get_model("supply_chain", "quality_drift", "defect_rate_forecast").run(
        {"horizon_days": 40, "persist_synthetic": True, "seed": 2}
    )
    assert result.metadata.get("synthetic_dataset_id")
    assert result.metadata.get("scenario_id")


@pytest.mark.parametrize(
    "subdomain,model_id,output_name",
    [
        ("quality_drift", "defect_rate_forecast", "defect_rate"),
        ("disruption_intelligence", "disruption_risk_forecast", "global_risk_index"),
        ("resilience_planning", "recovery_time_forecast", "recovery_days_p50"),
    ],
)
def test_inference_specs_supply_chain(subdomain, model_id, output_name):
    spec = get_spec("supply_chain", subdomain, model_id)
    assert spec.predictor_type.startswith("supply_chain_")
    assert any(o.name == output_name for o in spec.output_schema)
    key = model_key("supply_chain", subdomain, model_id)
    assert key == f"{spec.domain}.{spec.subdomain}.{spec.model_id}"
