"""Trading research models: synthetic series + forecast + trading lifecycle metrics."""

from typing import Any, Callable

import numpy as np

from khukra.core.model import ModelResult
from khukra.domains.research_base import ResearchForecastModel, make_research_model


def _returns_from_level(level: np.ndarray) -> np.ndarray:
    if len(level) < 2:
        return np.array([0.0])
    return np.diff(level) / np.maximum(np.abs(level[:-1]), 1e-8)


def _sharpe_proxy(returns: np.ndarray, periods_per_year: float = 252.0) -> float:
    if len(returns) < 2:
        return 0.0
    std = float(np.std(returns))
    if std < 1e-12:
        return 0.0
    return float(np.mean(returns) / std * np.sqrt(periods_per_year))


def _max_drawdown(level: np.ndarray) -> float:
    if len(level) < 2:
        return 0.0
    peak = np.maximum.accumulate(level)
    dd = (level - peak) / np.maximum(peak, 1e-8)
    return float(np.min(dd))


def _hit_rate(returns: np.ndarray) -> float:
    if len(returns) == 0:
        return 0.0
    return float(np.mean(returns > 0))


TradingMetricsFn = Callable[
    [dict[str, np.ndarray], np.ndarray, dict[str, float]],
    dict[str, float],
]


def _default_market_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    rets = _returns_from_level(target)
    return {
        "liquidity_score": float(np.clip(1.0 - np.std(target) / max(np.mean(target), 0.01), 0, 1)),
        "regime_volatility": float(np.std(rets)),
        "signal_score": float(base.get("final_level", 0.0)),
    }


def _default_signal_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    rets = _returns_from_level(target)
    half_life = series_data.get("half_life_proxy")
    hl = float(np.mean(half_life)) if half_life is not None else 10.0
    return {
        "signal_score": float(np.clip(np.mean(target[-20:]), -2, 2)),
        "expected_return": float(np.mean(rets) * 252),
        "half_life_bars": hl,
    }


def _default_backtest_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    rets = _returns_from_level(target)
    equity = np.cumprod(1.0 + np.clip(rets, -0.05, 0.05))
    return {
        "sharpe_ratio": _sharpe_proxy(rets),
        "hit_rate": _hit_rate(rets),
        "max_drawdown": abs(_max_drawdown(equity)),
        "turnover_proxy": float(np.mean(np.abs(rets))),
        "exposure": float(np.clip(np.mean(np.abs(target)), 0, 1)),
    }


def _default_execution_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    participation = series_data.get("participation")
    part = float(np.mean(participation)) if participation is not None else 0.15
    return {
        "slippage_bps": float(np.mean(target) * 10000),
        "fill_rate": float(np.clip(1.0 - np.std(target) * 2, 0.5, 1.0)),
        "market_impact_proxy": float(np.mean(target) * part),
        "participation_rate": part,
    }


def _default_risk_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    dd_proxy = series_data.get("max_drawdown_proxy")
    mdd = float(np.max(dd_proxy)) if dd_proxy is not None else abs(_max_drawdown(target))
    return {
        "max_drawdown": mdd,
        "var_proxy": float(np.percentile(target, 5)) if len(target) else 0.0,
        "risk_envelope": float(np.max(target)),
        "limit_utilization": float(np.clip(np.mean(target) / max(np.max(target), 1e-6), 0, 1)),
    }


def _default_delivery_metrics(
    series_data: dict[str, np.ndarray],
    target: np.ndarray,
    base: dict[str, float],
) -> dict[str, float]:
    readiness = series_data.get("readiness")
    if readiness is not None:
        score = float(np.mean(readiness))
    else:
        score = float(np.clip(1.0 - base.get("forecast_mae", 0.1), 0, 1))
    gate = score >= 0.65 and base.get("forecast_mae", 1.0) < 0.5
    return {
        "readiness_score": score,
        "gate_passed": 1.0 if gate else 0.0,
        "release_status": 1.0 if gate else 0.0,
    }


METRIC_ENRICHERS: dict[str, TradingMetricsFn] = {
    "market": _default_market_metrics,
    "signal": _default_signal_metrics,
    "backtest": _default_backtest_metrics,
    "execution": _default_execution_metrics,
    "risk": _default_risk_metrics,
    "delivery": _default_delivery_metrics,
}


def make_trading_research_model(
    subdomain_id: str,
    model_name: str,
    generator: Callable[[int, np.random.Generator, dict[str, Any]], dict[str, np.ndarray]],
    lifecycle: str,
    default_overrides: dict[str, Any] | None = None,
    horizon: int = 24,
    metrics_fn: TradingMetricsFn | None = None,
) -> type[ResearchForecastModel]:
    """Factory for finance trading models with enriched lifecycle metrics."""
    enricher = metrics_fn or METRIC_ENRICHERS[lifecycle]
    base_cls = make_research_model(
        "finance",
        subdomain_id,
        model_name,
        generator,
        default_overrides,
        horizon,
    )

    class TradingModel(base_cls):
        def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
            result = super().run(parameters)
            n = int(result.parameters.get("history_length", 200))
            rng = np.random.default_rng(int(result.parameters.get("seed", 42)))
            series_data = self.generate_series(n, rng, result.parameters)
            target = series_data["target"]
            trading_metrics = enricher(series_data, target, result.metrics)
            result.metrics = {**result.metrics, **trading_metrics}
            result.metadata = {
                **result.metadata,
                "lifecycle": lifecycle,
                "trading_product": "automated_research_to_paper",
                "paper_trading_only": True,
            }
            return result

    TradingModel.__name__ = base_cls.__name__
    return TradingModel
