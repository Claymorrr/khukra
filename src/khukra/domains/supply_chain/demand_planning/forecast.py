from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult


class DemandForecast(Model):
    """Holt-Winters-style exponential smoothing demand forecast."""

    domain = "supply_chain"
    subdomain = "demand_planning"
    name = "demand_forecast"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "history_weeks": 52,
            "forecast_weeks": 12,
            "base_demand": 200.0,
            "trend": 1.5,
            "seasonality_amplitude": 40.0,
            "noise_std": 10.0,
            "alpha": 0.3,
            "beta": 0.1,
            "seed": 21,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        rng = np.random.default_rng(p["seed"])

        weeks = np.arange(p["history_weeks"])
        seasonal = p["seasonality_amplitude"] * np.sin(2 * np.pi * weeks / 52)
        history = p["base_demand"] + p["trend"] * weeks + seasonal + rng.normal(0, p["noise_std"], p["history_weeks"])
        history = np.maximum(history, 0)

        level = history[0]
        trend = p["trend"]
        forecasts: list[float] = []

        for value in history:
            prev_level = level
            level = p["alpha"] * value + (1 - p["alpha"]) * (level + trend)
            trend = p["beta"] * (level - prev_level) + (1 - p["beta"]) * trend

        for h in range(1, p["forecast_weeks"] + 1):
            seasonal_h = p["seasonality_amplitude"] * np.sin(2 * np.pi * (p["history_weeks"] + h) / 52)
            forecasts.append(level + h * trend + seasonal_h)

        mape = float(np.mean(np.abs((history[1:] - history[:-1]) / np.maximum(history[:-1], 1))) * 100)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "mape_percent": mape,
                "final_level": float(level),
                "final_trend": float(trend),
                "forecast_mean": float(np.mean(forecasts)),
            },
            series={
                "week": list(range(p["history_weeks"] + p["forecast_weeks"])),
                "actual": history.tolist() + [float("nan")] * p["forecast_weeks"],
                "forecast": [float("nan")] * p["history_weeks"] + forecasts,
            },
        )
