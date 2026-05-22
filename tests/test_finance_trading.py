"""Finance automated trading domain — registry, lifecycle metrics, and ModelResult shape."""

import pytest

from khukra.core.model import ModelResult
from khukra.domains.registry import DOMAINS, get_model, list_models, list_subdomains
from khukra.inference.registry import get_spec

FINANCE_SUBDOMAINS = [
    "market_research",
    "signal_research",
    "strategy_backtesting",
    "execution_simulation",
    "portfolio_risk",
    "strategy_delivery",
]

LIFECYCLE_METRICS: dict[str, set[str]] = {
    "market_research": {"liquidity_score", "regime_volatility"},
    "signal_research": {"signal_score", "expected_return"},
    "strategy_backtesting": {"sharpe_ratio", "hit_rate", "max_drawdown"},
    "execution_simulation": {"slippage_bps", "fill_rate"},
    "portfolio_risk": {"max_drawdown", "var_proxy"},
    "strategy_delivery": {"readiness_score", "gate_passed"},
}


def test_finance_subdomains_registered():
    subs = list_subdomains("finance")
    for sid in FINANCE_SUBDOMAINS:
        assert sid in subs


def test_finance_model_count():
    total = sum(len(list_models("finance", s)) for s in FINANCE_SUBDOMAINS)
    assert total == 13


@pytest.mark.parametrize("subdomain,model_id", [
    (sub, mid)
    for sub, models in DOMAINS["finance"].items()
    for mid in models
])
def test_finance_model_run_shape(subdomain: str, model_id: str):
    model = get_model("finance", subdomain, model_id)
    params = {**model.default_parameters(), "history_length": 80, "persist_synthetic": False}
    if model_id == "portfolio_allocation_optimizer":
        result = model.run(params)
        assert isinstance(result, ModelResult)
        assert "sharpe_ratio" in result.metrics
        assert "weights" in result.series
        assert result.metadata.get("paper_trading_only") is True
        return

    result = model.run(params)
    assert isinstance(result, ModelResult)
    assert result.domain == "finance"
    assert result.subdomain == subdomain
    assert "forecast_mae" in result.metrics
    assert "time" in result.series
    assert result.metadata.get("lifecycle")
    assert result.metadata.get("paper_trading_only") is True

    expected = LIFECYCLE_METRICS.get(subdomain, set())
    for key in expected:
        assert key in result.metrics, f"{model_id} missing {key}"


def test_finance_inference_specs():
    for subdomain, models in DOMAINS["finance"].items():
        for model_id in models:
            spec = get_spec("finance", subdomain, model_id)
            assert spec.domain == "finance"
            assert spec.predictor_type.startswith("trading_")
            assert len(spec.output_schema) >= 3


def test_finance_mlops_templates():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "src" / "khukra" / "services" / "mlops_templates.py"
    spec = importlib.util.spec_from_file_location("mlops_templates", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    finance_ids = {
        t["id"]
        for t in mod.PIPELINE_TEMPLATES
        if "finance" in t.get("domains", [])
    }
    assert "quant_research_loop" in finance_ids
    assert "strategy_backtest_gate" in finance_ids
    assert "paper_trading_delivery" in finance_ids


def test_trading_lifecycle_flow():
    """Smoke the research → backtest → delivery chain."""
    market = get_model("finance", "market_research", "market_scenario_research")
    backtest = get_model("finance", "strategy_backtesting", "strategy_backtest_validation")
    delivery = get_model("finance", "strategy_delivery", "paper_trading_delivery_gate")

    p = {"history_length": 100, "persist_synthetic": False, "seed": 1}
    m = market.run(p)
    b = backtest.run(p)
    d = delivery.run(p)

    assert m.metrics["liquidity_score"] >= 0
    assert b.metrics["sharpe_ratio"] is not None
    assert "readiness_score" in d.metrics
