"""Signal research: alpha decay and statistical arbitrage signals."""

import numpy as np

from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    jump_diffusion,
    regime_switch_series,
)

SpreadSignalResearch = make_trading_research_model(
    "signal_research",
    "spread_signal_research",
    lambda n, rng, p: {
        "target": ar_process(n, 0.92, 0.04, rng)
        + 0.2 * regime_switch_series(n, (-0.1, 0.12), (0.025, 0.04), 0.06, rng)[0]
        + 0.1 * jump_diffusion(n, 0.0, 0.03, 0.03, 0.0, 0.25, rng),
        "regime": regime_switch_series(n, (-0.1, 0.1), (0.02, 0.03), 0.05, rng)[1],
    },
    lifecycle="signal",
    default_overrides={"history_length": 400, "forecast_horizon": 24},
)

AlphaDecaySignal = make_trading_research_model(
    "signal_research",
    "alpha_decay_signal",
    lambda n, rng, p: {
        "target": np.clip(
            ar_process(n, 0.9, 0.05, rng) * np.exp(-np.linspace(0, 0.8, n))
            + 0.15 * jump_diffusion(n, 0.0, 0.02, 0.02, 0.0, 0.2, rng),
            -1.5,
            1.5,
        ),
        "half_life_proxy": np.clip(
            5 + 3 * ar_process(n, 0.85, 0.1, rng) + compound_poisson_shocks(n, 0.01, 1.5, 0.2, rng),
            1,
            20,
        ),
    },
    lifecycle="signal",
    default_overrides={"history_length": 360, "forecast_horizon": 20},
)
