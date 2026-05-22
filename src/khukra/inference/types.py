from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeatureField:
    name: str
    type: str
    default: Any
    label: str
    required: bool = False
    description: str = ""
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class OutputField:
    name: str
    label: str
    unit: str = ""
    description: str = ""


@dataclass
class InferenceModelSpec:
    domain: str
    subdomain: str
    model_id: str
    version: str
    label: str
    predictor_type: str
    description: str
    feature_schema: list[FeatureField]
    output_schema: list[OutputField]
    supports_uncertainty: bool = False
    model_kind: str | None = None


@dataclass
class PredictionValue:
    value: float
    confidence: float | None = None
    unit: str = ""


@dataclass
class PredictionResult:
    inference_id: str
    domain: str
    subdomain: str
    model_id: str
    model_version: str
    predictor_type: str
    inputs: dict[str, Any]
    predictions: dict[str, PredictionValue]
    traces: dict[str, list[float]] = field(default_factory=dict)
    explanation: str = ""
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def predictions_flat(self) -> dict[str, float]:
        return {k: v.value for k, v in self.predictions.items()}

    def confidence_flat(self) -> dict[str, float]:
        return {k: v.confidence for k, v in self.predictions.items() if v.confidence is not None}
