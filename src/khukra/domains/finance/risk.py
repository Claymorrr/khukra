"""Portfolio risk: drawdown envelopes, VaR proxies, and allocation."""

from typing import Any

import numpy as np
from scipy.optimize import minimize

from khukra.core.model import Model, ModelResult
from khukra.domains.finance.trading_base import make_trading_research_model
from khukra.synthetic.primitives import (
    ar_process,
    regime_switch_series,
    shock_process,
    stochastic_volatility,
)

DrawdownEnvelopeRisk = make_trading_research_model(
    "portfolio_risk",
    "drawdown_envelope_risk",
    lambda n, rng, p: {
        "target": np.clip(
            shock_process(n, 0.2, 0.05, 0.15, rng)
            + 0.25 * stochastic_volatility(n, 0.04, 0.12, 0.2, rng)
            + 0.1 * regime_switch_series(n, (0.05, 0.35), (0.02, 0.06), 0.04, rng)[0],
            0,
            2,
        ),
        "max_drawdown_proxy": np.clip(
            np.maximum.accumulate(ar_process(n, 0.8, 0.07, rng)) * -0.15 + 0.2,
            0.02,
            0.5,
        ),
    },
    lifecycle="risk",
    default_overrides={"history_length": 420, "forecast_horizon": 18},
)

PortfolioRiskEnvelope = make_trading_research_model(
    "portfolio_risk",
    "portfolio_risk_envelope",
    lambda n, rng, p: {
        "target": np.clip(
            ar_process(n, 0.85, 0.05, rng) + shock_process(n, 0.12, 0.04, 0.1, rng),
            -0.5,
            1.5,
        ),
        "max_drawdown_proxy": np.clip(0.05 + 0.1 * np.abs(ar_process(n, 0.75, 0.08, rng)), 0.02, 0.6),
    },
    lifecycle="risk",
    default_overrides={"history_length": 400, "forecast_horizon": 16},
)


class PortfolioAllocationOptimizer(Model):
    """Markowitz mean-variance portfolio optimization (solver-style, paper-only)."""

    domain = "finance"
    subdomain = "portfolio_risk"
    name = "portfolio_allocation_optimizer"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "target_return": 0.10,
            "risk_free_rate": 0.03,
            "seed": 42,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        names = ["equity", "bonds", "commodities", "reits"]
        mu = np.array([0.12, 0.05, 0.08, 0.09])
        cov = np.array([
            [0.040, 0.005, 0.010, 0.012],
            [0.005, 0.008, 0.002, 0.004],
            [0.010, 0.002, 0.030, 0.006],
            [0.012, 0.004, 0.006, 0.025],
        ])
        n_assets = len(mu)
        target_ret = float(p["target_return"])

        def portfolio_stats(weights: np.ndarray) -> tuple[float, float]:
            ret = weights @ mu
            risk = np.sqrt(weights @ cov @ weights)
            return float(ret), float(risk)

        def objective(weights: np.ndarray) -> float:
            ret, risk = portfolio_stats(weights)
            return risk**2

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w: portfolio_stats(w)[0] - target_ret},
        ]
        bounds = [(0.0, 1.0)] * n_assets
        x0 = np.ones(n_assets) / n_assets
        result = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        weights = result.x if result.success else x0
        port_ret, port_risk = portfolio_stats(weights)
        sharpe = (port_ret - float(p["risk_free_rate"])) / max(port_risk, 1e-8)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "portfolio_return": port_ret,
                "portfolio_risk": port_risk,
                "sharpe_ratio": sharpe,
                "max_drawdown": float(port_risk * 2.5),
                "var_proxy": float(-1.65 * port_risk),
                "limit_utilization": float(np.max(weights)),
            },
            series={
                "assets": names,
                "weights": weights.tolist(),
            },
            metadata={
                "lifecycle": "risk",
                "trading_product": "automated_research_to_paper",
                "paper_trading_only": True,
                "optimizer_status": "success" if result.success else "fallback_equal_weight",
            },
        )
