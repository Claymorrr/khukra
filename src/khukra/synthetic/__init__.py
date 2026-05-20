"""Synthetic data generation for research inference pipelines."""

from khukra.synthetic.generator import SyntheticDataEngine, SyntheticScenario
from khukra.synthetic.primitives import (
    ar_process,
    degradation_curve,
    hawkes_events,
    regime_switch_series,
    shock_process,
)

__all__ = [
    "SyntheticDataEngine",
    "SyntheticScenario",
    "ar_process",
    "degradation_curve",
    "hawkes_events",
    "regime_switch_series",
    "shock_process",
]
