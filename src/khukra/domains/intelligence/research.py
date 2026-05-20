import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import (
    ar_process,
    bayesian_belief_state,
    compound_poisson_shocks,
    hawkes_events,
    jump_diffusion,
    regime_switch_series,
    stochastic_volatility,
)

SignalFusion = make_research_model(
    "intelligence",
    "signal_fusion",
    "multi_source_detection_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            0.25 * hawkes_events(n, 0.08, 0.65, 0.14, rng)
            + 0.45 * np.abs(ar_process(n, 0.85, 0.12, rng))
            + 0.3
            * bayesian_belief_state(
                np.abs(jump_diffusion(n, 0.0, 0.08, 0.03, 0.1, 0.4, rng)),
                0.04,
                0.12,
                rng,
            ),
            0,
            5,
        ),
        "source_a": ar_process(n, 0.78, 0.1, rng) + stochastic_volatility(n, 0.03, 0.08, 0.2, rng),
        "source_b": ar_process(n, 0.72, 0.11, rng)
        + compound_poisson_shocks(n, 0.02, 1.4, 0.3, rng),
    },
    {"history_length": 280, "forecast_horizon": 20},
)

InfluenceDynamics = make_research_model(
    "intelligence",
    "influence_dynamics",
    "narrative_cascade_forecast",
    lambda n, rng, p: {
        "target": np.maximum(
            regime_switch_series(n, (0.1, 1.2), (0.05, 0.22), 0.05, rng)[0]
            + 0.18 * hawkes_events(n, 0.05, 0.5, 0.2, rng)
            + 0.12 * jump_diffusion(n, 0.0, 0.05, 0.04, 0.0, 0.35, rng),
            0,
        ),
        "engagement": ar_process(n, 0.84, 0.14, rng)
        + stochastic_volatility(n, 0.05, 0.1, 0.22, rng)
        + 1,
    },
    {"history_length": 320, "forecast_horizon": 40},
)

AdversarialIndications = make_research_model(
    "intelligence",
    "adversarial_indications",
    "early_warning_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            ar_process(n, 0.9, 0.08, rng)
            + compound_poisson_shocks(n, 0.025, 2.2, 0.4, rng)
            + 0.25 * np.maximum(jump_diffusion(n, 0.0, 0.06, 0.03, 0.1, 0.5, rng), 0),
            0,
            3,
        ),
        "anomaly_score": bayesian_belief_state(
            np.abs(ar_process(n, 0.65, 0.18, rng)), 0.05, 0.12, rng
        ),
    },
    {"history_length": 250, "forecast_horizon": 18},
)
