"""Product quality drift and defect-rate simulation."""

from __future__ import annotations

from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult
from khukra.domains.supply_chain.simulation import (
    holdout_forecast_metrics,
    merge_params,
    persist_scenario_series,
    time_axis,
)
from khukra.synthetic.primitives import (
    ar_process,
    compound_poisson_shocks,
    degradation_curve,
    regime_switch_series,
)


class QualityDrift(Model):
    """Product quality across plants: defect drift, Cpk, escape risk, warranty exposure."""

    domain = "supply_chain"
    subdomain = "quality_drift"
    name = "defect_rate_forecast"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "horizon_days": 260,
            "n_plants": 3,
            "baseline_defect_rate": 0.02,
            "cpk_baseline": 1.33,
            "inspection_coverage": 0.85,
            "supplier_variability": 0.15,
            "special_cause_intensity": 0.04,
            "seed": 42,
            "persist_synthetic": True,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = merge_params(self.default_parameters(), parameters)
        n = int(p["horizon_days"])
        rng = np.random.default_rng(int(p["seed"]))

        drift = degradation_curve(n, p["baseline_defect_rate"], -0.004, 0.003, rng)
        special = compound_poisson_shocks(
            n, p["special_cause_intensity"], 1.5, 0.25, rng
        )
        wear, _ = regime_switch_series(n, (0.0, 0.012), (0.08, 0.2), 0.02, rng)
        supplier_noise = p["supplier_variability"] * ar_process(n, 0.88, 0.04, rng)

        defect_rate = np.clip(drift + special + wear + supplier_noise, 0.0, 1.0)
        cpk_proxy = np.clip(
            p["cpk_baseline"] - defect_rate * 0.35 - ar_process(n, 0.9, 0.05, rng) * 0.15,
            0.5,
            2.5,
        )
        escape_risk = defect_rate * (1.0 - p["inspection_coverage"])
        warranty_exposure = np.cumsum(escape_risk) / np.maximum(np.arange(1, n + 1), 1)

        mae, rmse, forecast, lower, upper = holdout_forecast_metrics(defect_rate)
        t = time_axis(n)
        future_t = np.arange(n, n + len(forecast), dtype=float)

        metadata: dict[str, Any] = {
            "model_kind": "quality_simulation",
            "n_plants": int(p["n_plants"]),
            "inspection_coverage": float(p["inspection_coverage"]),
        }
        if p.get("persist_synthetic", True):
            metadata.update(
                persist_scenario_series(
                    self.domain,
                    self.subdomain,
                    self.name,
                    p,
                    t,
                    defect_rate,
                    {
                        "cpk_proxy": cpk_proxy,
                        "escape_risk": escape_risk,
                        "warranty_exposure": warranty_exposure,
                    },
                )
            )

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "defect_rate": float(defect_rate[-1]),
                "cpk_min": float(np.min(cpk_proxy)),
                "escape_risk": float(escape_risk[-1]),
                "warranty_exposure_p90": float(np.percentile(warranty_exposure, 90)),
                "forecast_mae": mae,
                "forecast_rmse": rmse,
            },
            series={
                "time": t.tolist(),
                "defect_rate": defect_rate.tolist(),
                "cpk_proxy": cpk_proxy.tolist(),
                "escape_risk": escape_risk.tolist(),
                "warranty_exposure": warranty_exposure.tolist(),
                "forecast_time": future_t.tolist(),
                "forecast": forecast.tolist(),
                "forecast_lower": lower.tolist(),
                "forecast_upper": upper.tolist(),
            },
            metadata=metadata,
        )
