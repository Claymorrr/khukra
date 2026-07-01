"""Tests for advanced exploratory analysis."""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

from khukra.disruption.cache import load_panel, save_signal
from khukra.disruption.exploratory import (
    changepoint_detection,
    correlation_matrices,
    pca_exploration,
    run_advanced_exploration,
    signal_clustering,
)


def _synthetic_panel(n: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=date.today(), periods=n, freq="B")
    base = np.cumsum(rng.normal(0, 1, n))
    return pd.DataFrame(
        {
            "date": dates,
            "vix": 20 + base + rng.normal(0, 0.5, n),
            "oil_wti": 70 + 0.5 * base + rng.normal(0, 1, n),
            "hy_oas": 4 + 0.1 * base + rng.normal(0, 0.1, n),
        }
    )


def test_correlation_matrices():
    panel = _synthetic_panel()
    result = correlation_matrices(panel)
    assert result["n_obs"] == len(panel)
    assert len(result["pearson"]) == 9


def test_pca_exploration():
    panel = _synthetic_panel()
    result = pca_exploration(panel, n_components=2)
    assert len(result["components"]) == 2
    assert result["components"][0]["explained_pct"] > 0


def test_run_advanced_exploration_json_safe(tmp_path, monkeypatch):
    monkeypatch.setenv("KHUKRA_DATA_ROOT", str(tmp_path))
    panel = _synthetic_panel(200)
    for col in ["vix", "oil_wti", "hy_oas"]:
        save_signal(col, panel[["date", col]].rename(columns={col: "value"}))

    loaded = load_panel()
    result = run_advanced_exploration(loaded)
    json.dumps(result)
    assert "pca" in result["methods_run"]
    assert "bayesian_predictive" in result["methods_run"]


def test_run_advanced_exploration_with_sparse_news_stress():
    panel = _synthetic_panel(200)
    # Simulate news_stress: only a handful of non-zero days
    panel["news_stress"] = np.nan
    panel.loc[panel.index[-6:], "news_stress"] = [1.0, 2.0, 3.0, 2.5, 4.0, 3.0]
    result = run_advanced_exploration(panel)
    assert len(result["methods_run"]) == 7
    assert "clustering" in result["methods_run"]


def test_changepoint_and_clustering():
    panel = _synthetic_panel(250)
    cp = changepoint_detection(panel)
    assert "composite" in cp
    cl = signal_clustering(panel)
    assert cl["clusters"]
