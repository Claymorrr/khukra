from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from khukra.core.model import Model, ModelResult


class PointMassUAV(Model):
    """2D point-mass UAV with thrust vectoring, drag, and gravity."""

    domain = "physical"
    subdomain = "flight_dynamics"
    name = "point_mass_uav"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "mass_kg": 25.0,
            "thrust_n": 350.0,
            "pitch_deg": 15.0,
            "drag_coeff": 0.08,
            "initial_altitude_m": 100.0,
            "initial_speed_mps": 20.0,
            "duration_s": 30.0,
            "dt": 0.1,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        g = 9.81
        pitch = np.radians(p["pitch_deg"])

        def dynamics(_t, state):
            x, z, vx, vz = state
            speed = max(np.hypot(vx, vz), 1e-6)
            drag = p["drag_coeff"] * speed**2
            drag_x = drag * vx / speed
            drag_z = drag * vz / speed
            ax = (p["thrust_n"] * np.cos(pitch) - drag_x) / p["mass_kg"]
            az = (p["thrust_n"] * np.sin(pitch) - drag_z) / p["mass_kg"] - g
            return [vx, vz, ax, az]

        t_eval = np.arange(0, p["duration_s"] + p["dt"], p["dt"])
        sol = solve_ivp(
            dynamics,
            (0, p["duration_s"]),
            [0.0, p["initial_altitude_m"], p["initial_speed_mps"], 0.0],
            t_eval=t_eval,
            method="RK45",
        )

        x, z, vx, vz = sol.y
        speed = np.hypot(vx, vz)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "max_altitude_m": float(np.max(z)),
                "max_speed_mps": float(np.max(speed)),
                "range_m": float(x[-1]),
                "final_altitude_m": float(z[-1]),
            },
            series={
                "time_s": sol.t.tolist(),
                "altitude_m": z.tolist(),
                "range_m": x.tolist(),
                "speed_mps": speed.tolist(),
            },
        )
