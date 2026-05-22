"""Smoke tests for research MLOps expansion."""

import pytest

from khukra.data.engine import get_engine
from khukra.domains.registry import DOMAINS, list_domains, list_models, list_subdomains
from khukra.inference.engine import get_inference_engine
from khukra.inference.registry import get_registry, model_key
from khukra.services.mlops_pipeline import MLOpsPipeline


def test_five_domains_twenty_six_models():
    assert len(list_domains()) == 5
    total = sum(
        len(list_models(d, s))
        for d in list_domains()
        for s in list_subdomains(d)
    )
    assert total == 26
    assert len(list_models("finance", "market_research")) == 2
    assert len(list_models("finance", "strategy_delivery")) == 2
    physical_subs = list_subdomains("physical")
    assert "mechanics" in physical_subs
    assert "thermofluid" in physical_subs
    assert "dynamics" in physical_subs


def test_inference_registry_covers_all_models():
    reg = get_registry()
    for domain, subs in DOMAINS.items():
        for subdomain, models in subs.items():
            for model_id in models:
                assert model_key(domain, subdomain, model_id) in reg


def test_mlops_pipeline():
    pipeline = MLOpsPipeline()
    out = pipeline.run_full_pipeline(
        "computing",
        "distributed_systems_reliability",
        "latency_incident_forecast",
        {"seed": 1, "history_length": 60},
    )
    assert out["inference_id"]
    assert out["artifact_id"]


def test_migration_v3_tables():
    engine = get_engine()
    with engine.connect() as conn:
        tables = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchdf()["table_name"].tolist()
    for name in ("synthetic_datasets", "model_artifacts", "lineage_edges", "evaluation_runs"):
        assert name in tables
