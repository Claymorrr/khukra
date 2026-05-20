from typing import Any

import numpy as np
from scipy.stats import norm

from khukra.core.model import Model, ModelResult


class BlackScholesOption(Model):
    """European option pricing with Greeks under Black-Scholes."""

    domain = "finance"
    subdomain = "derivatives_risk"
    name = "black_scholes_option"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "spot_price": 100.0,
            "strike_price": 105.0,
            "risk_free_rate": 0.05,
            "volatility": 0.25,
            "time_to_maturity_years": 0.5,
            "option_type": "call",
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        s, k, r, sigma, t = (
            p["spot_price"],
            p["strike_price"],
            p["risk_free_rate"],
            p["volatility"],
            p["time_to_maturity_years"],
        )

        d1 = (np.log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        if p["option_type"].lower() == "put":
            price = k * np.exp(-r * t) * norm.cdf(-d2) - s * norm.cdf(-d1)
            delta = norm.cdf(d1) - 1
        else:
            price = s * norm.cdf(d1) - k * np.exp(-r * t) * norm.cdf(d2)
            delta = norm.cdf(d1)

        gamma = norm.pdf(d1) / (s * sigma * np.sqrt(t))
        vega = s * norm.pdf(d1) * np.sqrt(t) / 100
        theta = (
            -(s * norm.pdf(d1) * sigma) / (2 * np.sqrt(t))
            - r * k * np.exp(-r * t) * norm.cdf(d2 if p["option_type"].lower() == "call" else -d2)
        ) / 365

        spots = np.linspace(s * 0.7, s * 1.3, 50)
        payoffs = np.maximum(spots - k, 0) if p["option_type"].lower() == "call" else np.maximum(k - spots, 0)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "option_price": float(price),
                "delta": float(delta),
                "gamma": float(gamma),
                "vega": float(vega),
                "theta_per_day": float(theta),
            },
            series={
                "spot_price": spots.tolist(),
                "intrinsic_value": payoffs.tolist(),
            },
        )
