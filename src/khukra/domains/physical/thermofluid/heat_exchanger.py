from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from khukra.core.model import Model, ModelResult


class CounterflowHeatExchanger(Model):
    """Lumped counterflow heat exchanger with NTU-effectiveness dynamics."""

    domain = "physical"
    subdomain = "thermofluid"
    name = "counterflow_heat_exchanger"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "hot_inlet_c": 90.0,
            "cold_inlet_c": 20.0,
            "hot_capacity": 5000.0,
            "cold_capacity": 4500.0,
            "ua_w_per_k": 800.0,
            "duration_s": 600.0,
            "dt": 1.0,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        ua = p["ua_w_per_k"]
        ch, cc = p["hot_capacity"], p["cold_capacity"]
        c_min = min(ch, cc)
        ntu = ua / c_min
        cr = c_min / max(ch, cc)
        effectiveness = (1 - np.exp(-ntu * (1 - cr))) / (1 - cr) if abs(cr - 1) > 1e-6 else ntu / (1 + ntu)

        def dynamics(_t, state):
            th, tc = state
            q_dot = ua * (th - tc)
            return [-q_dot / ch, q_dot / cc]

        t_eval = np.arange(0, p["duration_s"] + p["dt"], p["dt"])
        sol = solve_ivp(
            dynamics,
            (0, p["duration_s"]),
            [p["hot_inlet_c"], p["cold_inlet_c"]],
            t_eval=t_eval,
            method="RK45",
        )

        th, tc = sol.y[0], sol.y[1]
        q_transfer = ua * (th - tc)

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "ntu": float(ntu),
                "effectiveness": float(effectiveness),
                "steady_hot_outlet_c": float(th[-1]),
                "steady_cold_outlet_c": float(tc[-1]),
                "peak_heat_transfer_kw": float(np.max(q_transfer) / 1000),
            },
            series={
                "time_s": sol.t.tolist(),
                "hot_temp_c": th.tolist(),
                "cold_temp_c": tc.tolist(),
                "heat_transfer_kw": (q_transfer / 1000).tolist(),
            },
        )
