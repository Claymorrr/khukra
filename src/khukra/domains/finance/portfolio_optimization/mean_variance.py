from typing import Any

import numpy as np
from scipy.optimize import minimize

from khukra.core.model import Model, ModelResult


class MeanVariancePortfolio(Model):
    """Markowitz mean-variance portfolio optimization."""

    domain = "finance"
    subdomain = "portfolio_optimization"
    name = "mean_variance_portfolio"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "target_return": 0.10,
            "risk_free_rate": 0.03,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}

        # Four-asset universe (annualized expected returns and covariance)
        names = ["equity", "bonds", "commodities", "reits"]
        mu = np.array([0.12, 0.05, 0.08, 0.09])
        cov = np.array([
            [0.040, 0.005, 0.010, 0.012],
            [0.005, 0.008, 0.002, 0.004],
            [0.010, 0.002, 0.030, 0.006],
            [0.012, 0.004, 0.006, 0.025],
        ])
        n = len(mu)

        def portfolio_stats(weights: np.ndarray) -> tuple[float, float]:
            ret = weights @ mu
            risk = np.sqrt(weights @ cov @ weights)
            return float(ret), float(risk)

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w: w @ mu - p["target_return"]},
        ]
        bounds = [(0, 1)] * n
        x0 = np.ones(n) / n

        result = minimize(
            lambda w: w @ cov @ w,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        weights = result.x if result.success else x0
        port_return, port_risk = portfolio_stats(weights)
        sharpe = (port_return - p["risk_free_rate"]) / port_risk if port_risk > 0 else 0

        frontier_returns = np.linspace(mu.min(), mu.max(), 20)
        frontier_risks = []
        for target in frontier_returns:
            cons = [
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},
                {"type": "eq", "fun": lambda w, t=target: w @ mu - t},
            ]
            res = minimize(lambda w: w @ cov @ w, x0, method="SLSQP", bounds=bounds, constraints=cons)
            _, risk = portfolio_stats(res.x if res.success else x0)
            frontier_risks.append(risk)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters={**p, "assets": names},
            metrics={
                "portfolio_return": port_return,
                "portfolio_risk": port_risk,
                "sharpe_ratio": float(sharpe),
                **{f"weight_{name}": float(w) for name, w in zip(names, weights)},
            },
            series={
                "frontier_return": frontier_returns.tolist(),
                "frontier_risk": frontier_risks,
            },
        )
