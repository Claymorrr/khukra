"""Strategy backtesting: validation metrics and Sharpe gates."""

import numpy as np

from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import (
    ar_process,
    jump_diffusion,
    regime_switch_series,
    shock_process,
)

StrategyBacktestValidation = make_trading_research_model(
    "strategy_backtesting",
    "strategy_backtest_validation",
    lambda n, rng, p: {
        "target": np.cumsum(
            ar_process(n, 0.88, 0.03, rng)
            + 0.12 * jump_diffusion(n, 0.0005, 0.02, 0.015, 0.0, 0.18, rng)
        ),
        "signal": ar_process(n, 0.9, 0.05, rng),
    },
    lifecycle="backtest",
    default_overrides={"history_length": 480, "forecast_horizon": 24},
)

SharpeRatioBacktest = make_trading_research_model(
    "strategy_backtesting",
    "sharpe_ratio_backtest",
    lambda n, rng, p: {
        "target": shock_process(n, 0.15, 0.04, 0.1, rng)
        + 0.2 * regime_switch_series(n, (0.02, 0.08), (0.01, 0.03), 0.05, rng)[0],
        "benchmark": ar_process(n, 0.95, 0.02, rng) * 0.5,
    },
    lifecycle="backtest",
    default_overrides={"history_length": 420, "forecast_horizon": 20},
)
