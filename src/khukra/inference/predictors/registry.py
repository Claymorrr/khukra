"""Predictor registry — routes inference execution to registered predictor backends."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from khukra.core.model import Model
from khukra.inference.predictors.rule_based import RuleBasedPredictor
from khukra.inference.types import InferenceModelSpec, PredictionResult


class Predictor(Protocol):
    spec: InferenceModelSpec
    model: Model

    def predict(self, inputs: dict[str, Any]) -> PredictionResult: ...


PredictorFactory = Callable[[InferenceModelSpec, Model], Predictor]

_PREDICTOR_REGISTRY: dict[str, PredictorFactory] = {}


def _ensure_defaults() -> None:
    if _PREDICTOR_REGISTRY:
        return
    from khukra.domains.physical.models_registry import SOLVER_SPECS

    for solver_spec in SOLVER_SPECS.values():
        predictor_type = solver_spec.predictor_type
        if not predictor_type:
            continue
        _PREDICTOR_REGISTRY[predictor_type] = RuleBasedPredictor


def register_predictor(predictor_type: str, predictor_factory: PredictorFactory) -> None:
    """Register a predictor implementation for a predictor_type string."""
    _PREDICTOR_REGISTRY[predictor_type] = predictor_factory


def get_predictor(spec: InferenceModelSpec, model: Model) -> Predictor:
    """Resolve predictor for spec; defaults to RuleBasedPredictor for local solvers."""
    _ensure_defaults()
    cls = _PREDICTOR_REGISTRY.get(spec.predictor_type, RuleBasedPredictor)
    return cls(spec, model)


def list_predictor_types() -> list[str]:
    _ensure_defaults()
    return sorted(_PREDICTOR_REGISTRY.keys())
