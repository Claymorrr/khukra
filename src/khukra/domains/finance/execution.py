"""Execution simulation: slippage, market impact, and paper-order fills."""

import numpy as np

from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    shock_process,
    stochastic_volatility,
)

ExecutionSlippageSim = make_trading_research_model(
    "execution_simulation",
    "execution_slippage_sim",
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
    lifecycle="execution",
    default_overrides={"history_length": 390, "forecast_horizon": 16},
)

PaperOrderFillSim = make_trading_research_model(
    "execution_simulation",
    "paper_order_fill_sim",
    lambda n, rng, p: {
        "target": np.clip(
            0.85
            + 0.1 * ar_process(n, 0.82, 0.05, rng)
            - 0.05 * compound_poisson_shocks(n, 0.02, 0.8, 0.1, rng),
            0.4,
            1.0,
        ),
        "participation": np.clip(rng.uniform(0.08, 0.3, n), 0, 1),
    },
    lifecycle="execution",
    default_overrides={"history_length": 360, "forecast_horizon": 12},
)
