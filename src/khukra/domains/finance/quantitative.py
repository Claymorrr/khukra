import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    hawkes_events,
    jump_diffusion,
    regime_switch_series,
    shock_process,
    stochastic_volatility,
)

MarketMicrostructure = make_research_model(
    "finance",
    "market_microstructure",
    "lob_liquidity_forecast",
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
    {"history_length": 500, "forecast_horizon": 20},
)

StatisticalArbitrage = make_research_model(
    "finance",
    "statistical_arbitrage",
    "spread_mean_reversion_forecast",
    lambda n, rng, p: {
        "target": ar_process(n, 0.92, 0.04, rng)
        + 0.2 * regime_switch_series(n, (-0.1, 0.12), (0.025, 0.04), 0.06, rng)[0]
        + 0.1 * jump_diffusion(n, 0.0, 0.03, 0.03, 0.0, 0.25, rng),
        "regime": regime_switch_series(n, (-0.1, 0.1), (0.02, 0.03), 0.05, rng)[1],
    },
    {"history_length": 400, "forecast_horizon": 24},
)

RiskExecutionResearch = make_research_model(
    "finance",
    "risk_and_execution_research",
    "execution_slippage_forecast",
    lambda n, rng, p: {
        "target": np.maximum(
            ar_process(n, 0.78, 0.06, rng)
            + shock_process(n, 0.1, 0.03, 0.08, rng)
            + 0.15 * compound_poisson_shocks(n, 0.015, 2.0, 0.15, rng)
            + stochastic_volatility(n, 0.02, 0.08, 0.15, rng),
            0,
        ),
        "participation": np.clip(rng.uniform(0.05, 0.25, n), 0, 1),
    },
    {"history_length": 390, "forecast_horizon": 16},
)
