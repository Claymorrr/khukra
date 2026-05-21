import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import ar_process, degradation_curve, jump_diffusion, regime_switch_series

AerodesignPerformance = make_research_model(
    "physical",
    "aerodesign",
    "aerodynamic_performance_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            0.85
            + 0.12 * np.sin(np.linspace(0, 5 * np.pi, n))
            + 0.08 * ar_process(n, 0.9, 0.04, rng)
            - 0.06 * degradation_curve(n, 0.05, 0.003, 0.012, rng)
            + 0.04 * jump_diffusion(n, 0.0, 0.03, 0.02, -0.15, 0.1, rng),
            0.35,
            1.25,
        ),
        "lift_proxy": np.clip(
            0.9 + 0.1 * np.sin(np.linspace(0, 3 * np.pi, n)) + 0.05 * ar_process(n, 0.85, 0.05, rng),
            0.4,
            1.3,
        ),
        "drag_proxy": np.clip(
            0.25
            + 0.08 * regime_switch_series(n, (0.18, 0.32), (0.02, 0.05), 0.03, rng)[0]
            + 0.04 * ar_process(n, 0.88, 0.03, rng),
            0.1,
            0.55,
        ),
    },
    {"history_length": 220, "forecast_horizon": 40},
)

AerodesignStaticMargin = make_research_model(
    "physical",
    "aerodesign",
    "static_margin_stability_forecast",
    lambda n, rng, p: {
        "static_margin": np.clip(
            0.15
            + 0.06 * np.sin(np.linspace(0, 4 * np.pi, n))
            + 0.05 * ar_process(n, 0.88, 0.04, rng)
            - 0.03 * degradation_curve(n, 0.04, 0.002, 0.01, rng),
            0.05,
            0.45,
        ),
        "cg_shift_proxy": np.clip(
            0.5 + 0.08 * ar_process(n, 0.9, 0.03, rng) + 0.02 * jump_diffusion(n, 0, 0.02, 0.01, -0.08, 0.06, rng),
            0.2,
            0.9,
        ),
    },
    {"history_length": 180, "forecast_horizon": 30},
)

AerodesignMissionRange = make_research_model(
    "physical",
    "aerodesign",
    "mission_range_envelope_forecast",
    lambda n, rng, p: {
        "range_nm": np.clip(
            1200
            + 80 * np.sin(np.linspace(0, 2 * np.pi, n))
            + 40 * ar_process(n, 0.92, 0.08, rng)
            - 25 * degradation_curve(n, 0.03, 0.001, 0.008, rng),
            800,
            1600,
        ),
        "fuel_burn_proxy": np.clip(
            0.55 + 0.12 * regime_switch_series(n, (0.48, 0.62), (0.01, 0.03), 0.02, rng)[0],
            0.3,
            0.85,
        ),
    },
    {"history_length": 200, "forecast_horizon": 35},
)
