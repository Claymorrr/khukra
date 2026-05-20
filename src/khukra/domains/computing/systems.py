import numpy as np

from khukra.domains.research_base import make_research_model
from khukra.synthetic.primitives import (
    ar_process,
    bayesian_belief_state,
    compound_poisson_shocks,
    degradation_curve,
    jump_diffusion,
    queueing_load,
    regime_switch_series,
    stochastic_volatility,
)

DistributedReliability = make_research_model(
    "computing",
    "distributed_systems_reliability",
    "latency_incident_forecast",
    lambda n, rng, p: {
        "target": queueing_load(n, 8.0, 6.5, rng)
        + 4.0 * stochastic_volatility(n, 0.04, 0.08, 0.25, rng)
        + compound_poisson_shocks(n, 0.025, 2.0, 0.8, rng),
        "error_rate": np.clip(
            ar_process(n, 0.74, 0.05, rng)
            + 0.03 * np.maximum(jump_diffusion(n, 0.0, 0.04, 0.03, 0.1, 0.35, rng), 0)
            + 0.01,
            0,
            1,
        ),
    },
    {"history_length": 360, "forecast_horizon": 24},
)

MLAcceleratorWorkloads = make_research_model(
    "computing",
    "ml_accelerator_workloads",
    "gpu_throughput_forecast",
    lambda n, rng, p: {
        "target": np.clip(
            0.8
            + ar_process(n, 0.88, 0.08, rng)
            - degradation_curve(n, 0.15, 0.001, 0.01, rng)
            - 0.12 * compound_poisson_shocks(n, 0.02, 1.5, 0.35, rng)
            + 0.08 * regime_switch_series(n, (-0.2, 0.2), (0.04, 0.06), 0.04, rng)[0],
            0.1,
            1.2,
        ),
        "memory_pressure": np.clip(
            bayesian_belief_state(
                np.abs(ar_process(n, 0.9, 0.05, rng)) + stochastic_volatility(n, 0.03, 0.1, 0.18, rng),
                0.04,
                0.1,
                rng,
            ),
            0,
            1,
        ),
    },
    {"history_length": 300, "forecast_horizon": 20},
)

CyberPhysicalCompute = make_research_model(
    "computing",
    "cyber_physical_compute",
    "edge_compute_degradation_forecast",
    lambda n, rng, p: {
        "target": degradation_curve(n, 1.0, 0.0015, 0.03, rng)
        * regime_switch_series(n, (1.0, 0.6), (0.02, 0.05), 0.035, rng)[0]
        - 0.08 * compound_poisson_shocks(n, 0.018, 1.8, 0.25, rng)
        + 0.06 * jump_diffusion(n, 0.0, 0.04, 0.02, 0.0, 0.25, rng),
        "sensor_backlog": queueing_load(n, 4.0, 3.2, rng) / 10
        + stochastic_volatility(n, 0.02, 0.08, 0.15, rng),
    },
    {"history_length": 240, "forecast_horizon": 28},
)
