import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    degradation_curve,
    jump_diffusion,
    regime_switch_series,
    stochastic_volatility,
)

TurbomachineryDegradation = make_research_model(
    "physical",
    "turbomachinery_degradation",
    "turbomachinery_health_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            degradation_curve(n, 1.0, 0.004, 0.015, rng)
            - 0.03 * compound_poisson_shocks(n, 0.04, 1.5, 0.2, rng)
            + 0.02 * jump_diffusion(n, 0.0, 0.05, 0.02, -0.2, 0.1, rng),
            0.2,
            1.2,
        ),
        "vibration": ar_process(n, 0.9, 0.04, rng) + stochastic_volatility(n, 0.04, 0.08, 0.1, rng),
    },
    {"history_length": 240, "forecast_horizon": 36},
)

CombustionStability = make_research_model(
    "physical",
    "combustion_stability",
    "combustion_instability_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            regime_switch_series(n, (0.2, 0.95), (0.06, 0.22), 0.05, rng)[0]
            + 0.15 * compound_poisson_shocks(n, 0.03, 2.0, 0.25, rng),
            0,
            2,
        ),
        "pressure_osc": ar_process(n, 0.78, 0.08, rng) + jump_diffusion(n, 0.0, 0.03, 0.04, 0.0, 0.3, rng),
    },
    {"history_length": 300, "forecast_horizon": 48},
)

HybridPropulsionControl = make_research_model(
    "physical",
    "hybrid_propulsion_control",
    "hybrid_propulsion_mission_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            0.6 * np.sin(np.linspace(0, 4 * np.pi, n))
            + 0.35 * ar_process(n, 0.92, 0.04, rng)
            + 0.12 * regime_switch_series(n, (-0.2, 0.35), (0.04, 0.08), 0.04, rng)[0]
            + 0.08 * jump_diffusion(n, 0.0, 0.04, 0.03, 0.0, 0.15, rng),
            0,
            1.5,
        ),
        "battery_soc": np.clip(
            1.0 - np.linspace(0, 0.4, n) + 0.04 * ar_process(n, 0.8, 0.2, rng),
            0,
            1,
        ),
    },
    {"history_length": 180, "forecast_horizon": 30},
)
