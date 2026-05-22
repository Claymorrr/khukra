"""Reusable scientific analytics for physics solver outputs."""

from __future__ import annotations

import numpy as np


def peak_abs(series: np.ndarray) -> float:
    return float(np.max(np.abs(series))) if series.size else 0.0


def final_value(series: np.ndarray) -> float:
    return float(series[-1]) if series.size else 0.0


def settling_time(
    time: np.ndarray,
    series: np.ndarray,
    threshold: float = 0.05,
) -> float:
    """Time when |series| first stays within threshold * peak."""
    peak = np.max(np.abs(series))
    if peak == 0 or time.size == 0:
        return 0.0
    within = np.abs(series) <= threshold * peak
    if not within.any():
        return float(time[-1])
    return float(time[np.argmax(within)])


def mechanical_energy(mass: float, velocity: np.ndarray, stiffness: float, displacement: np.ndarray) -> np.ndarray:
    return 0.5 * mass * velocity**2 + 0.5 * stiffness * displacement**2


def relative_steady_state_error(
    series: np.ndarray,
    steady_estimate: float | None = None,
    tail_fraction: float = 0.1,
) -> float:
    """Relative error between tail mean and analytic steady estimate."""
    if series.size < 2:
        return 0.0
    tail_n = max(1, int(series.size * tail_fraction))
    tail_mean = float(np.mean(series[-tail_n:]))
    if steady_estimate is None:
        steady_estimate = tail_mean
    denom = max(abs(steady_estimate), 1e-12)
    return float(abs(tail_mean - steady_estimate) / denom)


def sweep_summary(metrics_rows: list[dict[str, float]], key: str) -> dict[str, float]:
    """Min/max/mean of a metric across a parameter sweep."""
    values = [row[key] for row in metrics_rows if key in row]
    if not values:
        return {}
    arr = np.asarray(values, dtype=float)
    return {
        f"{key}_min": float(np.min(arr)),
        f"{key}_max": float(np.max(arr)),
        f"{key}_mean": float(np.mean(arr)),
    }
