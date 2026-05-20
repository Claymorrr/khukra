import itertools
from typing import Any

from khukra.core.model import ModelResult
from khukra.data.repositories.runs import RunRepository
from khukra.data.repositories.sweeps import SweepRepository
from khukra.domains.registry import get_model


class SweepRunner:
    def __init__(
        self,
        sweeps: SweepRepository | None = None,
        runs: RunRepository | None = None,
    ):
        self.sweeps = sweeps or SweepRepository()
        self.runs = runs or RunRepository()

    def execute(
        self,
        domain: str,
        subdomain: str,
        model_name: str,
        sweep_config: dict[str, list[Any]],
        base_parameters: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        sweep_id = self.sweeps.create(
            domain, subdomain, model_name, sweep_config, base_parameters, user_id
        )
        model = get_model(domain, subdomain, model_name)
        keys = list(sweep_config.keys())
        values = [sweep_config[k] for k in keys]
        run_ids: list[str] = []

        try:
            for combo in itertools.product(*values):
                params = dict(base_parameters or model.default_parameters())
                params.update(dict(zip(keys, combo)))
                result: ModelResult = model.run(params)
                run_id = self.runs.save(result, sweep_id=sweep_id, user_id=user_id)
                result.metadata["run_id"] = run_id
                run_ids.append(run_id)

            self.sweeps.update_status(sweep_id, "completed")
        except Exception:
            self.sweeps.update_status(sweep_id, "failed")
            raise

        return {
            "sweep_id": sweep_id,
            "run_ids": run_ids,
            "total_runs": len(run_ids),
            "status": "completed",
        }
