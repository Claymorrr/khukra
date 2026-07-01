"""Tests for Bayesian inference primitives."""

from __future__ import annotations

import numpy as np

from khukra.disruption.bayesian import (
    bayesian_correlation,
    bayesian_linear_forecast,
    bayesian_model_compare_nested,
)


def test_bayesian_correlation_positive():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 200)
    y = 0.8 * x + rng.normal(0, 0.3, 200)
    post = bayesian_correlation(x, y)
    assert post["r"] > 0.5
    assert post["prob_positive"] > 0.95
    assert post["ci_low"] > 0


def test_bayesian_forecast_returns_bands():
    y = np.linspace(0, 1, 80) + np.random.default_rng(1).normal(0, 0.05, 80)
    out = bayesian_linear_forecast(y, horizon=10)
    assert len(out["forecast"]) == 10
    assert out["forecast_lower"][0] < out["forecast"][0] < out["forecast_upper"][0]


def test_bayesian_model_compare():
    rng = np.random.default_rng(2)
    n = 120
    x = rng.normal(0, 1, n)
    e = rng.normal(0, 0.2, n)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.5 * x[t - 1] + e[t]
    y_v = y[1:]
    X_r = np.column_stack([np.ones(n - 1), y[:-1]])
    X_f = np.column_stack([np.ones(n - 1), y[:-1], x[:-1]])
    cmp = bayesian_model_compare_nested(y_v, X_r, X_f)
    assert 0 <= cmp["posterior_predictive_prob"] <= 1
