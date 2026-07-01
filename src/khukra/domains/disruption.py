"""Global disruption intelligence: regions, ports, supplier contagion."""

from __future__ import annotations

from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult
from khukra.simulation.primitives import (
    compound_poisson_shocks,
    hawkes_events,
    jump_diffusion,
    shock_process,
)
from khukra.simulation.shared import (
    correlated_region_signals,
    holdout_forecast_metrics,
    merge_params,
    persist_scenario_series,
    supplier_contagion,
    time_axis,
)


class DisruptionIntelligence(Model):
    """Global disruption risk from geopolitical, weather, logistics, and cascade events."""

    domain = "logistics"
    subdomain = "disruption_intelligence"
    name = "disruption_risk_forecast"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "horizon_days": 220,
            "n_regions": 5,
            "n_suppliers": 12,
            "geopolitical_weight": 0.35,
            "weather_weight": 0.25,
            "logistics_weight": 0.4,
            "hawkes_baseline": 0.06,
            "hawkes_excitation": 0.6,
            "hawkes_decay": 0.18,
            "contagion_coupling": 0.45,
            "seed": 42,
            "persist_synthetic": True,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = merge_params(self.default_parameters(), parameters)
        n = int(p["horizon_days"])
        n_regions = int(p["n_regions"])
        n_suppliers = int(p["n_suppliers"])
        rng = np.random.default_rng(int(p["seed"]))

        region_signals = correlated_region_signals(n, n_regions, rng)
        geo = p["geopolitical_weight"] * np.mean(
            np.abs(region_signals) + compound_poisson_shocks(n, 0.03, 2.0, 0.35, rng),
            axis=0,
        )
        weather = p["weather_weight"] * shock_process(n, 0.25, 0.04, 0.3, rng)
        logistics = p["logistics_weight"] * np.maximum(
            jump_diffusion(n, 0.0, 0.03, 0.02, 0.0, 0.5, rng),
            0.0,
        )

        cascades = hawkes_events(
            n, p["hawkes_baseline"], p["hawkes_excitation"], p["hawkes_decay"], rng
        ).astype(float)
        global_risk = geo + weather + logistics + 0.35 * cascades

        supplier_health = rng.normal(0.5, 0.12, (n_suppliers, n)) + region_signals[
            rng.integers(0, n_regions, n_suppliers)
        ]
        supplier_health += 0.2 * global_risk
        contagion = supplier_contagion(supplier_health, p["contagion_coupling"])

        port_delay = shock_process(n, 0.35, 0.03, 0.4, rng) + logistics * 0.6
        expected_delay_days = port_delay * (1.0 + 0.5 * global_risk)

        mae, rmse, forecast, lower, upper = holdout_forecast_metrics(global_risk)
        t = time_axis(n)
        future_t = np.arange(n, n + len(forecast), dtype=float)

        metadata: dict[str, Any] = {
            "model_kind": "disruption_simulation",
            "n_regions": n_regions,
            "n_suppliers": n_suppliers,
        }
        if p.get("persist_synthetic", True):
            metadata.update(
                persist_scenario_series(
                    self.domain,
                    self.subdomain,
                    self.name,
                    p,
                    t,
                    global_risk,
                    {
                        "port_delay_index": port_delay,
                        "supplier_contagion": contagion,
                        "expected_delay_days": expected_delay_days,
                    },
                )
            )

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "global_risk_index": float(global_risk[-1]),
                "expected_delay_days": float(np.mean(expected_delay_days[-14:])),
                "supplier_contagion": float(contagion[-1]),
                "port_delay_p95": float(np.percentile(port_delay, 95)),
                "forecast_mae": mae,
                "forecast_rmse": rmse,
            },
            series={
                "time": t.tolist(),
                "global_risk_index": global_risk.tolist(),
                "port_delay_index": port_delay.tolist(),
                "supplier_contagion": contagion.tolist(),
                "expected_delay_days": expected_delay_days.tolist(),
                "forecast_time": future_t.tolist(),
                "forecast": forecast.tolist(),
                "forecast_lower": lower.tolist(),
                "forecast_upper": upper.tolist(),
            },
            metadata=metadata,
        )
