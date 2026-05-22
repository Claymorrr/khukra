"""Market research: scenarios, liquidity regimes, and microstructure features."""

import numpy as np

from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    hawkes_events,
    regime_switch_series,
    shock_process,
    stochastic_volatility,
)

MarketScenarioResearch = make_trading_research_model(
    "market_research",
    "market_scenario_research",
    lambda n, rng, p: {
        "target": np.clip(
            shock_process(n, 0.35, 0.04, 0.3, rng)
            + 0.08 * hawkes_events(n, 0.08, 0.55, 0.18, rng)
            + stochastic_volatility(n, 0.03, 0.1, 0.2, rng),
            0,
            5,
        ),
        "spread_bps": np.abs(ar_process(n, 0.86, 0.04, rng)) * 10
        + compound_poisson_shocks(n, 0.02, 1.3, 0.4, rng)
        + 1,
    },
    lifecycle="market",
    default_overrides={"history_length": 500, "forecast_horizon": 20},
)

LiquidityRegimeForecast = make_trading_research_model(
    "market_research",
    "liquidity_regime_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            regime_switch_series(n, (0.8, 2.5), (0.03, 0.08), 0.05, rng)[0]
            + 0.1 * hawkes_events(n, 0.06, 0.5, 0.2, rng),
            0,
            4,
        ),
        "regime": regime_switch_series(n, (0, 1), (0.02, 0.03), 0.04, rng)[1],
    },
    lifecycle="market",
    default_overrides={"history_length": 450, "forecast_horizon": 18},
)
