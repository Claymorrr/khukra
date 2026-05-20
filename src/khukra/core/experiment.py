import itertools
import uuid
from typing import Any

from khukra.core.model import Model, ModelResult
from khukra.data.repositories.runs import RunRepository


class ExperimentRunner:
    """Run single models or parameter sweeps."""

    def __init__(self, runs: RunRepository | None = None):
        self.runs = runs or RunRepository()

    def run_once(
        self,
        model: Model,
        parameters: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> ModelResult:
        result = model.run(parameters)
        run_id = self.runs.save(result, user_id=user_id)
        result.metadata["run_id"] = run_id
        return result

    def run_sweep(
        self,
        model: Model,
        sweep: dict[str, list[Any]],
        base_parameters: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> list[ModelResult]:
        keys = list(sweep.keys())
        values = [sweep[k] for k in keys]
        results: list[ModelResult] = []

        for combo in itertools.product(*values):
            params = dict(base_parameters or model.default_parameters())
            params.update(dict(zip(keys, combo)))
            results.append(self.run_once(model, params, user_id=user_id))

        return results
