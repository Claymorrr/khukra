"""Base class for research forecasting models driven by synthetic data."""

import uuid
from abc import abstractmethod
from typing import Any, Callable

import numpy as np

from khukra.core.model import Model, ModelResult
from khukra.synthetic.generator import SyntheticDataEngine, SyntheticScenario
from khukra.synthetic.primitives import forecast_holt_linear


class ResearchForecastModel(Model):
    """Generate synthetic observations, fit forecast, return metrics + intervals."""

    forecast_horizon: int = 24

    def default_parameters(self) -> dict[str, Any]:
        return {
            "history_length": 200,
            "forecast_horizon": self.forecast_horizon,
            "seed": 42,
            "persist_synthetic": True,
        }

    @abstractmethod
    def generate_series(self, n: int, rng: np.random.Generator, params: dict[str, Any]) -> dict[str, np.ndarray]:
        """Return dict with at least 'target' and optional feature arrays."""
        ...

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        horizon = int(p.get("forecast_horizon", self.forecast_horizon))
        n = int(p["history_length"])
        rng = np.random.default_rng(int(p["seed"]))

        series_data = self.generate_series(n, rng, p)
        target = series_data["target"]
        time = np.arange(n, dtype=float)

        train_n = int(n * 0.75)
        y_train = target[:train_n]
        y_hold = target[train_n:]

        forecast, lower, upper = forecast_holt_linear(y_train, horizon)
        hold_forecast, _, _ = forecast_holt_linear(y_train, len(y_hold))
        mae = float(np.mean(np.abs(y_hold - hold_forecast[: len(y_hold)]))) if len(y_hold) else 0.0
        rmse = float(np.sqrt(np.mean((y_hold - hold_forecast[: len(y_hold)]) ** 2))) if len(y_hold) else 0.0

        future_t = np.arange(n, n + horizon, dtype=float)
        scenario = SyntheticScenario(
            scenario_id=str(uuid.uuid4())[:12],
            domain=self.domain,
            subdomain=self.subdomain,
            model_id=self.name,
            seed=int(p["seed"]),
            parameters=p,
        )

        metadata: dict[str, Any] = {
            "scenario_id": scenario.scenario_id,
            "synthetic": True,
            "forecast_horizon": horizon,
            "train_size": train_n,
            "holdout_mae": mae,
        }

        if p.get("persist_synthetic", True):
            engine = SyntheticDataEngine()
            df = SyntheticDataEngine.build_timeseries_df(
                time,
                target,
                {k: v for k, v in series_data.items() if k != "target"},
            )
            persisted = engine.persist_dataset(scenario, df, split="full")
            metadata["synthetic_dataset_id"] = persisted["dataset_id"]
            metadata["validation"] = persisted["validation"]

        out_series: dict[str, list[float]] = {
            "time": time.tolist(),
            "observed": target.tolist(),
            "forecast_time": future_t.tolist(),
            "forecast": forecast.tolist(),
            "forecast_lower": lower.tolist(),
            "forecast_upper": upper.tolist(),
        }
        for key, arr in series_data.items():
            if key != "target" and len(arr) == n:
                out_series[key] = arr.tolist()

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "forecast_mae": mae,
                "forecast_rmse": rmse,
                "final_level": float(forecast[-1]),
                "trend_slope": float((forecast[-1] - forecast[0]) / max(horizon, 1)),
            },
            series=out_series,
            metadata=metadata,
        )


def make_research_model(
    domain_id: str,
    subdomain_id: str,
    model_name: str,
    generator: Callable[[int, np.random.Generator, dict[str, Any]], dict[str, np.ndarray]],
    default_overrides: dict[str, Any] | None = None,
    horizon: int = 24,
) -> type[ResearchForecastModel]:
    """Factory for compact research model class definitions."""

    class _Model(ResearchForecastModel):
        domain = domain_id
        subdomain = subdomain_id
        name = model_name
        forecast_horizon = horizon

        def default_parameters(self) -> dict[str, Any]:
            base = super().default_parameters()
            if default_overrides:
                base.update(default_overrides)
            return base

        def generate_series(self, n: int, rng: np.random.Generator, params: dict[str, Any]) -> dict[str, np.ndarray]:
            return generator(n, rng, params)

    _Model.__name__ = "".join(w.capitalize() for w in model_name.split("_"))
    return _Model
