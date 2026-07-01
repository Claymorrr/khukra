"""Stochastic primitives for logistics scenario generation."""

import numpy as np


def ar_process(
    n: int,
    phi: float,
    sigma: float,
    rng: np.random.Generator,
    intercept: float = 0.0,
) -> np.ndarray:
    y = np.zeros(n)
    eps = rng.normal(0, sigma, n)
    for t in range(1, n):
        y[t] = intercept + phi * y[t - 1] + eps[t]
    return y


def regime_switch_series(
    n: int,
    means: tuple[float, float],
    sigmas: tuple[float, float],
    transition: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    states = np.zeros(n, dtype=int)
    y = np.zeros(n)
    states[0] = 0
    y[0] = rng.normal(means[0], sigmas[0])
    for t in range(1, n):
        if rng.random() < transition:
            states[t] = 1 - states[t - 1]
        else:
            states[t] = states[t - 1]
        y[t] = rng.normal(means[states[t]], sigmas[states[t]])
    return y, states.astype(float)


def shock_process(
    n: int,
    base: float,
    shock_prob: float,
    shock_scale: float,
    rng: np.random.Generator,
) -> np.ndarray:
    y = np.full(n, base)
    for t in range(n):
        if rng.random() < shock_prob:
            y[t] += rng.normal(0, shock_scale)
        else:
            y[t] += rng.normal(0, base * 0.02)
    return np.maximum(y, 0.0)


def jump_diffusion(
    n: int,
    drift: float,
    volatility: float,
    jump_intensity: float,
    jump_mean: float,
    jump_std: float,
    rng: np.random.Generator,
    initial: float = 0.0,
) -> np.ndarray:
    y = np.zeros(n)
    y[0] = initial
    for t in range(1, n):
        jump_count = rng.poisson(jump_intensity)
        jump = rng.normal(jump_mean, jump_std, jump_count).sum() if jump_count else 0.0
        y[t] = y[t - 1] + drift + volatility * rng.normal() + jump
    return y


def compound_poisson_shocks(
    n: int,
    intensity: float,
    severity_shape: float,
    severity_scale: float,
    rng: np.random.Generator,
) -> np.ndarray:
    counts = rng.poisson(intensity, n)
    out = np.zeros(n)
    for i, count in enumerate(counts):
        if count:
            out[i] = rng.gamma(severity_shape, severity_scale, count).sum()
    return out


def degradation_curve(
    n: int,
    initial: float,
    rate: float,
    noise: float,
    rng: np.random.Generator,
) -> np.ndarray:
    t = np.arange(n)
    base = initial * np.exp(-rate * t / max(n, 1))
    return base + rng.normal(0, noise, n)


def hawkes_events(
    n_steps: int,
    baseline: float,
    excitation: float,
    decay: float,
    rng: np.random.Generator,
) -> np.ndarray:
    intensity = np.full(n_steps, baseline)
    counts = np.zeros(n_steps)
    for t in range(n_steps):
        lam = baseline + excitation * np.sum(counts[:t] * np.exp(-decay * (t - np.arange(t))))
        intensity[t] = lam
        counts[t] = rng.poisson(max(lam * 0.1, 1e-6))
    return counts


def forecast_holt_linear(
    y: np.ndarray,
    horizon: int,
    alpha: float = 0.35,
    beta: float = 0.15,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(y)
    level = y[0]
    trend = y[1] - y[0] if n > 1 else 0.0
    fitted = np.zeros(n)
    for t in range(n):
        fitted[t] = level + trend
        if t < n - 1:
            level_new = alpha * y[t] + (1 - alpha) * (level + trend)
            trend_new = beta * (level_new - level) + (1 - beta) * trend
            level, trend = level_new, trend_new
    resid_std = float(np.std(y - fitted)) if n > 2 else 0.1
    future = np.array([level + (h + 1) * trend for h in range(horizon)])
    lower = future - 1.96 * resid_std
    upper = future + 1.96 * resid_std
    return future, lower, upper
