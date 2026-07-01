"""Resilience planning: recovery time, buffers, and service level under disruption."""

from __future__ import annotations

from typing import Any

import numpy as np

from khukra_logistics.core.model import Model, ModelResult
from khukra_logistics.simulation.primitives import ar_process, compound_poisson_shocks, shock_process
from khukra_logistics.simulation.shared import (
    holdout_forecast_metrics,
    merge_params,
    persist_scenario_series,
    recovery_trajectory,
    time_axis,
)


class ResiliencePlanning(Model):
    """Recovery planning with buffers, alternate suppliers, and quality containment."""

    domain = "logistics"
    subdomain = "resilience_planning"
    name = "recovery_time_forecast"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "horizon_days": 200,
            "buffer_days": 10.0,
            "alternate_supplier_fraction": 0.3,
            "expedite_capacity_factor": 1.2,
            "disruption_baseline": 0.4,
            "quality_containment_load": 0.15,
            "seed": 42,
            "persist_synthetic": True,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = merge_params(self.default_parameters(), parameters)
        n = int(p["horizon_days"])
        rng = np.random.default_rng(int(p["seed"]))

        severity = (
            p["disruption_baseline"]
            + shock_process(n, 0.5, 0.03, 0.5, rng)
            + compound_poisson_shocks(n, 0.025, 2.0, 0.6, rng)
            + 0.3 * np.abs(ar_process(n, 0.9, 0.2, rng))
        )
        severity += p["quality_containment_load"] * ar_process(n, 0.85, 0.12, rng)
        severity = np.maximum(severity, 0.0)

        recovery_days, buffer_level, service_level = recovery_trajectory(
            n,
            severity,
            float(p["buffer_days"]),
            float(p["alternate_supplier_fraction"]),
            float(p["expedite_capacity_factor"]),
            rng,
        )

        mae, rmse, forecast, lower, upper = holdout_forecast_metrics(recovery_days)
        t = time_axis(n)
        future_t = np.arange(n, n + len(forecast), dtype=float)
        buffer_utilization = 1.0 - buffer_level / max(float(p["buffer_days"]), 0.1)

        metadata: dict[str, Any] = {
            "model_kind": "resilience_simulation",
            "buffer_days_nominal": float(p["buffer_days"]),
        }
        if p.get("persist_synthetic", True):
            metadata.update(
                persist_scenario_series(
                    self.domain,
                    self.subdomain,
                    self.name,
                    p,
                    t,
                    recovery_days,
                    {
                        "buffer_level": buffer_level,
                        "service_level": service_level,
                        "disruption_severity": severity,
                    },
                )
            )

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "recovery_days_p50": float(np.percentile(recovery_days, 50)),
                "recovery_days_p90": float(np.percentile(recovery_days, 90)),
                "service_level_at_risk": float(np.min(service_level)),
                "buffer_utilization": float(np.mean(buffer_utilization[-30:])),
                "forecast_mae": mae,
                "forecast_rmse": rmse,
            },
            series={
                "time": t.tolist(),
                "recovery_days": recovery_days.tolist(),
                "buffer_level": buffer_level.tolist(),
                "service_level": service_level.tolist(),
                "disruption_severity": severity.tolist(),
                "forecast_time": future_t.tolist(),
                "forecast": forecast.tolist(),
                "forecast_lower": lower.tolist(),
                "forecast_upper": upper.tolist(),
            },
            metadata=metadata,
        )
