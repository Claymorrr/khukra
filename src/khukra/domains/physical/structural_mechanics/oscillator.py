from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from khukra.core.model import Model, ModelResult


class DampedOscillator(Model):
    """Mass-spring-damper: m x'' + c x' + k x = 0."""

    domain = "physical"
    subdomain = "structural_mechanics"
    name = "damped_oscillator"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "mass": 1.0,
            "damping": 0.5,
            "stiffness": 4.0,
            "initial_displacement": 1.0,
            "initial_velocity": 0.0,
            "duration": 10.0,
            "dt": 0.05,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        m, c, k = p["mass"], p["damping"], p["stiffness"]

        def dynamics(_t, state):
            x, v = state
            return [v, (-c * v - k * x) / m]

        t_eval = np.arange(0, p["duration"] + p["dt"], p["dt"])
        sol = solve_ivp(
            dynamics,
            (0, p["duration"]),
            [p["initial_displacement"], p["initial_velocity"]],
            t_eval=t_eval,
            method="RK45",
        )

        displacement = sol.y[0]
        velocity = sol.y[1]
        energy = 0.5 * m * velocity**2 + 0.5 * k * displacement**2

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "peak_displacement": float(np.max(np.abs(displacement))),
                "final_energy": float(energy[-1]),
                "settling_time": float(self._settling_time(sol.t, displacement)),
            },
            series={
                "time": sol.t.tolist(),
                "displacement": displacement.tolist(),
                "velocity": velocity.tolist(),
                "energy": energy.tolist(),
            },
        )

    @staticmethod
    def _settling_time(time: np.ndarray, displacement: np.ndarray, threshold: float = 0.05) -> float:
        peak = np.max(np.abs(displacement))
        if peak == 0:
            return 0.0
        within = np.abs(displacement) <= threshold * peak
        if not within.any():
            return float(time[-1])
        return float(time[np.argmax(within)])
