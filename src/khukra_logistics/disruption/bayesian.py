"""Bayesian inference primitives for disruption signal analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats


def bayesian_correlation(
    x: np.ndarray,
    y: np.ndarray,
    prior_z_mean: float = 0.0,
    prior_z_sd: float = 0.5,
) -> dict[str, float]:
    """Posterior for Pearson r via Fisher-z with normal prior (weakly informative)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = len(x)
    if n < 8:
        return {
            "r": 0.0,
            "ci_low": -1.0,
            "ci_high": 1.0,
            "prob_positive": 0.5,
            "prob_negative": 0.5,
            "prob_strong": 0.0,
        }

    r = float(np.corrcoef(x, y)[0, 1])
    r = float(np.clip(r, -0.999, 0.999))
    z = float(np.arctanh(r))
    lik_prec = max(n - 3, 1)
    prior_prec = 1.0 / (prior_z_sd**2)
    post_prec = prior_prec + lik_prec
    post_mean = (prior_prec * prior_z_mean + lik_prec * z) / post_prec
    post_sd = 1.0 / np.sqrt(post_prec)

    ci_z = post_mean + np.array([-1.96, 1.96]) * post_sd
    ci_r = np.tanh(ci_z)

    prob_positive = float(1.0 - stats.norm.cdf(0.0, post_mean, post_sd))
    prob_negative = float(stats.norm.cdf(0.0, post_mean, post_sd))
    z_cut = np.arctanh(0.3)
    prob_strong = float(
        stats.norm.cdf(-z_cut, post_mean, post_sd) + (1.0 - stats.norm.cdf(z_cut, post_mean, post_sd))
    )

    return {
        "r": r,
        "ci_low": float(ci_r[0]),
        "ci_high": float(ci_r[1]),
        "prob_positive": prob_positive,
        "prob_negative": prob_negative,
        "prob_strong": prob_strong,
    }


def bayesian_regime_prob(
    current: float,
    history: np.ndarray,
    threshold: float = 1.5,
) -> dict[str, float]:
    """P(elevated/depressed) for current level vs rolling history with estimation uncertainty."""
    h = np.asarray(history, dtype=float)
    h = h[np.isfinite(h)]
    n = len(h)
    if n < 10 or not np.isfinite(current):
        return {"z": 0.0, "prob_elevated": 0.0, "prob_depressed": 0.0}

    mu = float(np.mean(h))
    sigma = float(np.std(h, ddof=1)) or 1.0
    z = (current - mu) / sigma
    se_z = 1.0 / np.sqrt(max(n - 1, 1))
    prob_elevated = float(1.0 - stats.norm.cdf(threshold, loc=z, scale=se_z))
    prob_depressed = float(stats.norm.cdf(-threshold, loc=z, scale=se_z))
    return {"z": float(z), "prob_elevated": prob_elevated, "prob_depressed": prob_depressed}


def bayesian_linear_forecast(
    y: np.ndarray,
    horizon: int,
    level: float = 0.95,
) -> dict[str, Any]:
    """Bayesian linear trend with weakly informative priors — posterior predictive bands."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 10:
        raise ValueError("Need at least 10 points for Bayesian forecast.")

    t = np.arange(n, dtype=float)
    X = np.column_stack([np.ones(n), t])
    k = X.shape[1]
    prior_prec = np.eye(k) * 1e-4  # vague prior on (intercept, slope)
    beta_mle, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta_mle
    sigma2 = float(np.sum(resid**2) / max(n - k, 1))

    XtX = X.T @ X
    post_prec = prior_prec + XtX / sigma2
    post_cov = np.linalg.inv(post_prec)
    post_mean = post_cov @ (prior_prec @ np.zeros(k) + XtX @ beta_mle / sigma2)

    t_mean = float(np.mean(t))
    t_var = float(np.sum((t - t_mean) ** 2)) or 1.0
    z_crit = float(stats.norm.ppf(0.5 + level / 2))

    forecast: list[float] = []
    lower: list[float] = []
    upper: list[float] = []
    for h in range(1, horizon + 1):
        t_new = np.array([1.0, n - 1 + h])
        mean = float(t_new @ post_mean)
        var = float(sigma2 * (1.0 + t_new @ post_cov @ t_new))
        sd = np.sqrt(max(var, 1e-12))
        forecast.append(mean)
        lower.append(mean - z_crit * sd)
        upper.append(mean + z_crit * sd)

    # Holdout predictive score (last 25%)
    train_n = max(10, int(n * 0.75))
    hold = y[train_n:]
    hold_pred: list[float] = []
    for i in range(len(hold)):
        t_h = np.array([1.0, train_n + i])
        hold_pred.append(float(t_h @ post_mean[:2] if len(post_mean) == 2 else t_h @ post_mean))
    mae = float(np.mean(np.abs(hold - np.array(hold_pred[: len(hold)])))) if len(hold) else 0.0
    rmse = float(np.sqrt(np.mean((hold - np.array(hold_pred[: len(hold)])) ** 2))) if len(hold) else 0.0

    return {
        "forecast": forecast,
        "forecast_lower": lower,
        "forecast_upper": upper,
        "credible_level": level,
        "holdout_mae": mae,
        "holdout_rmse": rmse,
    }


def bayesian_model_compare_nested(
    y: np.ndarray,
    X_restricted: np.ndarray,
    X_full: np.ndarray,
) -> dict[str, float]:
    """Approximate posterior model probability via BIC (Laplace / unit-information prior)."""
    n = len(y)

    def _fit_ssr(X: np.ndarray) -> tuple[float, int]:
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        ssr = float(np.sum((y - X @ beta) ** 2))
        return max(ssr, 1e-12), X.shape[1]

    ssr_r, k_r = _fit_ssr(X_restricted)
    ssr_f, k_f = _fit_ssr(X_full)
    bic_r = n * np.log(ssr_r / n) + k_r * np.log(n)
    bic_f = n * np.log(ssr_f / n) + k_f * np.log(n)
    log_bf = 0.5 * (bic_r - bic_f)  # log Bayes factor (full vs restricted)
    prob_full = float(1.0 / (1.0 + np.exp(-log_bf)))
    return {
        "posterior_predictive_prob": prob_full,
        "log_bayes_factor": float(log_bf),
        "bic_restricted": float(bic_r),
        "bic_full": float(bic_f),
    }


def composite_posterior(current_z: float, n_signals: int, n_obs: int) -> dict[str, float]:
    """Posterior uncertainty on equal-weight composite z (signals × time)."""
    se = 1.0 / np.sqrt(max(n_signals * min(n_obs, 60), 1))
    ci = current_z + np.array([-1.96, 1.96]) * se
    prob_elevated = float(1.0 - stats.norm.cdf(1.5, loc=current_z, scale=se))
    return {
        "ci_low": float(ci[0]),
        "ci_high": float(ci[1]),
        "prob_elevated": prob_elevated,
        "posterior_sd": float(se),
    }
