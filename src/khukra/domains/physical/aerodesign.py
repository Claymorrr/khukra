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
