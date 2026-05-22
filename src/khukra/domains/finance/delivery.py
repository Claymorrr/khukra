"""Strategy delivery: release readiness and paper-trading deployment gates."""

import numpy as np

from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import ar_process, shock_process

StrategyReleaseReadiness = make_trading_research_model(
    "strategy_delivery",
    "strategy_release_readiness",
    lambda n, rng, p: {
        "target": np.clip(
            0.5 + 0.35 * ar_process(n, 0.88, 0.04, rng) - 0.1 * shock_process(n, 0.08, 0.02, 0.05, rng),
            0,
            1,
        ),
        "readiness": np.clip(
            0.6 + 0.25 * ar_process(n, 0.9, 0.03, rng) - 0.08 * shock_process(n, 0.05, 0.02, 0.04, rng),
            0,
            1,
        ),
    },
    lifecycle="delivery",
    default_overrides={"history_length": 320, "forecast_horizon": 12},
)

PaperTradingDeliveryGate = make_trading_research_model(
    "strategy_delivery",
    "paper_trading_delivery_gate",
    lambda n, rng, p: {
        "target": np.clip(ar_process(n, 0.86, 0.05, rng) + 0.15, 0, 1.5),
        "readiness": np.clip(
            0.55 + 0.3 * ar_process(n, 0.87, 0.04, rng) - 0.12 * shock_process(n, 0.06, 0.025, 0.06, rng),
            0,
            1,
        ),
    },
    lifecycle="delivery",
    default_overrides={"history_length": 300, "forecast_horizon": 10},
)
