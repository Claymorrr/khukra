from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult


class CantileverBeam(Model):
    """Euler-Bernoulli cantilever beam under uniform distributed load."""

    domain = "physical"
    subdomain = "structural_mechanics"
    name = "cantilever_beam"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "length": 5.0,
            "youngs_modulus": 210e9,
            "second_moment": 3.4e-6,
            "load": 1200.0,
            "points": 100,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        l_val, e_val, i_val, q = p["length"], p["youngs_modulus"], p["second_moment"], p["load"]

        x = np.linspace(0, l_val, int(p["points"]))
        # w(x) = q x^2 (6 L^2 - 3 L x + x^2) / (24 E I)
        deflection = q * x**2 * (6 * l_val**2 - 3 * l_val * x + x**2) / (24 * e_val * i_val)
        moment = q * x**2 * (l_val - x) / 2
        shear = q * (l_val - x)

        max_deflection = q * l_val**4 / (8 * e_val * i_val)
        max_moment = q * l_val**2 / 2

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "max_deflection_mm": float(max_deflection * 1000),
                "max_moment_knm": float(max_moment / 1000),
                "tip_deflection_mm": float(deflection[-1] * 1000),
            },
            series={
                "position_m": x.tolist(),
                "deflection_mm": (deflection * 1000).tolist(),
                "bending_moment_knm": (moment / 1000).tolist(),
                "shear_force_kn": (shear / 1000).tolist(),
            },
        )
