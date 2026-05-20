import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    degradation_curve,
    hawkes_events,
    jump_diffusion,
    regime_switch_series,
    shock_process,
)

QualityDrift = make_research_model(
    "supply_chain",
    "quality_drift",
    "defect_rate_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            degradation_curve(n, 0.02, -0.004, 0.003, rng)
            + 0.01 * compound_poisson_shocks(n, 0.03, 1.5, 0.3, rng)
            + 0.004 * regime_switch_series(n, (0.0, 1.0), (0.1, 0.25), 0.025, rng)[0],
            0,
            1,
        ),
        "cpk_proxy": np.clip(1.5 - ar_process(n, 0.9, 0.06, rng) * 0.2, 0.5, 2),
    },
    {"history_length": 260, "forecast_horizon": 28},
)

DisruptionIntelligence = make_research_model(
    "supply_chain",
    "disruption_intelligence",
    "disruption_risk_forecast",
    lambda n, rng, p: {
        "target": (
            hawkes_events(n, 0.06, 0.6, 0.18, rng).astype(float)
            + compound_poisson_shocks(n, 0.04, 2.0, 0.4, rng)
        ),
        "port_delay_index": shock_process(n, 0.3, 0.03, 0.35, rng)
        + np.maximum(jump_diffusion(n, 0.0, 0.03, 0.02, 0.0, 0.5, rng), 0),
    },
    {"history_length": 220, "forecast_horizon": 32},
)

ResiliencePlanning = make_research_model(
    "supply_chain",
    "resilience_planning",
    "recovery_time_forecast",
    lambda n, rng, p: {
        "target": np.maximum(
            5
            + ar_process(n, 0.92, 0.55, rng)
            + shock_process(n, 2.0, 0.03, 1.8, rng)
            + compound_poisson_shocks(n, 0.02, 2.0, 0.7, rng),
            0.5,
        ),
        "buffer_days": np.clip(10 - ar_process(n, 0.85, 0.3, rng), 1, 15),
    },
    {"history_length": 200, "forecast_horizon": 24},
)
