from typing import Any

import numpy as np

from khukra.core.model import Model, ModelResult


class InventorySimulation(Model):
    """(s, S) inventory policy with stochastic demand and lead time."""

    domain = "supply_chain"
    subdomain = "inventory_management"
    name = "inventory_simulation"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "initial_inventory": 100,
            "reorder_point": 40,
            "order_up_to": 120,
            "lead_time_days": 3,
            "demand_mean": 12.0,
            "demand_std": 4.0,
            "holding_cost": 0.5,
            "stockout_cost": 8.0,
            "order_cost": 25.0,
            "days": 90,
            "seed": 7,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}
        rng = np.random.default_rng(p["seed"])

        inventory = float(p["initial_inventory"])
        on_order = 0
        pending: list[tuple[int, float]] = []

        inv_levels: list[float] = []
        daily_holding: list[float] = []
        daily_stockouts: list[float] = []
        orders_placed: list[int] = []

        for day in range(p["days"]):
            arrivals = [qty for eta, qty in pending if eta == day]
            if arrivals:
                inventory += sum(arrivals)
                on_order -= sum(arrivals)
            pending = [(eta, qty) for eta, qty in pending if eta != day]

            demand = max(0.0, rng.normal(p["demand_mean"], p["demand_std"]))
            fulfilled = min(inventory, demand)
            stockout = demand - fulfilled
            inventory -= fulfilled

            if inventory <= p["reorder_point"] and on_order == 0:
                order_qty = p["order_up_to"] - inventory
                pending.append((day + p["lead_time_days"], order_qty))
                on_order += order_qty
                orders_placed.append(1)
            else:
                orders_placed.append(0)

            inv_levels.append(inventory)
            daily_holding.append(p["holding_cost"] * inventory)
            daily_stockouts.append(p["stockout_cost"] * stockout)

        order_cost_total = sum(orders_placed) * p["order_cost"]
        total_cost = sum(daily_holding) + sum(daily_stockouts) + order_cost_total

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "total_cost": float(total_cost),
                "avg_inventory": float(np.mean(inv_levels)),
                "service_level": float(1 - sum(d > 0 for d in daily_stockouts) / p["days"]),
                "orders_count": float(sum(orders_placed)),
            },
            series={
                "day": list(range(p["days"])),
                "inventory": inv_levels,
                "holding_cost": daily_holding,
                "stockout_cost": daily_stockouts,
            },
        )
