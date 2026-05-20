from typing import Any

import numpy as np
from scipy.optimize import linprog

from khukra.core.model import Model, ModelResult


class TransportOptimization(Model):
    """Minimum-cost transportation problem: plants to distribution centers."""

    domain = "supply_chain"
    subdomain = "network_logistics"
    name = "transport_optimization"

    def default_parameters(self) -> dict[str, Any]:
        return {
            "plant_a_supply": 120,
            "plant_b_supply": 80,
            "dc1_demand": 70,
            "dc2_demand": 90,
            "dc3_demand": 40,
        }

    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        p = {**self.default_parameters(), **(parameters or {})}

        # Cost matrix [plant_a, plant_b] x [dc1, dc2, dc3]
        costs = np.array([
            [4, 6, 9],
            [8, 5, 7],
        ]).flatten()

        supply = [p["plant_a_supply"], p["plant_b_supply"]]
        demand = [p["dc1_demand"], p["dc2_demand"], p["dc3_demand"]]

        n_plants, n_dcs = 2, 3
        a_eq = []
        b_eq = []

        for i in range(n_plants):
            row = np.zeros(n_plants * n_dcs)
            row[i * n_dcs : (i + 1) * n_dcs] = 1
            a_eq.append(row)
            b_eq.append(supply[i])

        for j in range(n_dcs):
            row = np.zeros(n_plants * n_dcs)
            for i in range(n_plants):
                row[i * n_dcs + j] = 1
            a_eq.append(row)
            b_eq.append(demand[j])

        result = linprog(costs, A_eq=np.array(a_eq), b_eq=np.array(b_eq), bounds=(0, None), method="highs")
        flows = result.x.reshape(n_plants, n_dcs) if result.success else np.zeros((n_plants, n_dcs))

        return ModelResult(
            domain=self.domain,
            subdomain=self.subdomain,
            model_name=self.name,
            parameters=p,
            metrics={
                "total_transport_cost": float(result.fun if result.success else 0),
                "plant_a_utilization": float(flows[0].sum() / supply[0]),
                "plant_b_utilization": float(flows[1].sum() / supply[1]),
            },
            series={
                "route": [
                    "A→DC1", "A→DC2", "A→DC3", "B→DC1", "B→DC2", "B→DC3",
                ],
                "shipment_units": flows.flatten().tolist(),
                "unit_cost": costs.tolist(),
            },
        )
