from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult


class GeometricBrownianMotion(Model):
    """Monte Carlo stock price paths under GBM."""

    domain = "finance"
    subdomain = "stochastic_processes"
    name = "geometric_brownian_motion"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "initial_price": 100.0,
            "drift": 0.08,
            "volatility": 0.2,
            "horizon_years": 1.0,
            "steps": 252,
            "simulations": 500,
            "seed": 42,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        rng = np.random.default_rng(p["seed"])

        dt = p["horizon_years"] / p["steps"]
        time = np.linspace(0, p["horizon_years"], p["steps"] + 1)
        prices = np.empty((p["simulations"], p["steps"] + 1))
        prices[:, 0] = p["initial_price"]

        for t in range(1, p["steps"] + 1):
            z = rng.standard_normal(p["simulations"])
            prices[:, t] = prices[:, t - 1] * np.exp(
                (p["drift"] - 0.5 * p["volatility"] ** 2) * dt + p["volatility"] * np.sqrt(dt) * z
            )

        terminal = prices[:, -1]
        returns = terminal / p["initial_price"] - 1

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "expected_terminal_price": float(np.mean(terminal)),
                "var_95": float(np.percentile(returns, 5)),
                "cvar_95": float(returns[returns <= np.percentile(returns, 5)].mean()),
                "max_drawdown_median": float(np.median(self._max_drawdown(prices))),
            },
            series={
                "time": time.tolist(),
                "mean_price": prices.mean(axis=0).tolist(),
                "p05_price": np.percentile(prices, 5, axis=0).tolist(),
                "p95_price": np.percentile(prices, 95, axis=0).tolist(),
            },
            metadata={"simulations": p["simulations"]},
        )

    @staticmethod
    def _max_drawdown(paths: np.ndarray) -> np.ndarray:
        running_max = np.maximum.accumulate(paths, axis=1)
        drawdown = paths / running_max - 1
        return drawdown.min(axis=1)
