from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from khukra.core.model import Model, ModelResult
from khukra.domains.physical.core import SolverResultSummary
from khukra.domains.physical.models_registry import SOLVER_SPECS
from khukra.domains.physical.solver_base import enrich_solver_result, prepare_solver_parameters


class PointMass2D(Model):
    """2D point-mass with constant applied force, quadratic drag, and gravity."""

    domain = "physical"
    subdomain = "dynamics"
    name = "point_mass_2d"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "mass_kg": 25.0,
            "applied_force_n": 350.0,
            "force_angle_deg": 15.0,
            "drag_coeff": 0.08,
            "initial_height_m": 100.0,
            "initial_speed_mps": 20.0,
            "duration_s": 30.0,
            "dt": 0.1,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = prepare_solver_parameters(self, parameters)
        g = 9.81
        angle = np.radians(p["force_angle_deg"])

        def dynamics(_t, state):
            x, z, vx, vz = state
            speed = max(np.hypot(vx, vz), 1e-6)
            drag = p["drag_coeff"] * speed**2
            drag_x = drag * vx / speed
            drag_z = drag * vz / speed
            ax = (p["applied_force_n"] * np.cos(angle) - drag_x) / p["mass_kg"]
            az = (p["applied_force_n"] * np.sin(angle) - drag_z) / p["mass_kg"] - g
            return [vx, vz, ax, az]

        t_eval = np.arange(0, p["duration_s"] + p["dt"], p["dt"])
        sol = solve_ivp(
            dynamics,
            (0, p["duration_s"]),
            [0.0, p["initial_height_m"], p["initial_speed_mps"], 0.0],
            t_eval=t_eval,
            method="RK45",
        )

        x, z, vx, vz = sol.y
        speed = np.hypot(vx, vz)

        result = ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "max_height_m": float(np.max(z)),
                "max_speed_mps": float(np.max(speed)),
                "displacement_x_m": float(x[-1]),
                "final_height_m": float(z[-1]),
            },
            series={
                "time_s": sol.t.tolist(),
                "position_x_m": x.tolist(),
                "position_z_m": z.tolist(),
                "speed_mps": speed.tolist(),
            },
        )
        spec = SOLVER_SPECS[self.name]
        numerical = SolverResultSummary(
            integration_success=bool(sol.success),
            n_steps=int(sol.t.size),
            notes=str(sol.message) if sol.message else "",
        )
        return enrich_solver_result(result, spec, numerical=numerical)
