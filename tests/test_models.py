"""Tests for Khukra Logistics models."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from khukra_logistics.registry import MODELS, get_model, list_models


@pytest.fixture
def data_root(tmp_path, monkeypatch):
    monkeypatch.setenv("KHUKRA_LOGISTICS_DATA_ROOT", str(tmp_path))
    return tmp_path


def test_registry_lists_three_models():
    models = list_models()
    assert len(models) == 3
    assert {m["model_id"] for m in models} == set(MODELS.keys())


@pytest.mark.parametrize("model_id", list(MODELS.keys()))
def test_models_run_and_persist(model_id: str, data_root: Path):
    result = get_model(model_id).run({"horizon_days": 120, "persist_synthetic": True})
    assert result.metrics
    assert result.series.get("time")
    assert result.metadata.get("scenario_id")
    scenario_dir = data_root / "scenarios" / result.domain / result.subdomain
    assert scenario_dir.exists()
    assert any(scenario_dir.glob("*.parquet"))


def test_cli_list(capsys):
    from khukra_logistics.cli import main

    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "disruption_risk_forecast" in out


def test_cli_run_json(capsys, data_root: Path):
    from khukra_logistics.cli import main

    assert main(["run", "recovery_time_forecast", "--param", "horizon_days=90"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["model_name"] == "recovery_time_forecast"
    assert "recovery_days_p50" in payload["metrics"]
