from typing import Any

from khukra.core.model import Model
from khukra.inference.types import InferenceModelSpec, PredictionResult, PredictionValue


class RuleBasedPredictor:
    """Wraps a domain Model as a Khukra inference predictor."""

    def __init__(self, spec: InferenceModelSpec, model: Model):
        self.spec = spec
        self.model = model

    def predict(self, inputs: dict[str, Any]) -> PredictionResult:
        result = self.model.run(inputs)
        predictions = self._map_predictions(result.metrics, result.metadata)
        explanation = self._build_explanation(predictions)

        return PredictionResult(
            inference_id="",
            domain=result.domain,
            subdomain=result.subdomain,
            model_id=result.model_name,
            model_version=self.spec.version,
            predictor_type=self.spec.predictor_type,
            inputs=result.parameters,
            predictions=predictions,
            traces=result.series,
            explanation=explanation,
            metadata={
                **result.metadata,
                "engine": "rule_based",
                "model_class": self.model.__class__.__name__,
            },
        )

    def _map_predictions(
        self,
        metrics: dict[str, float],
        metadata: dict[str, Any],
    ) -> dict[str, PredictionValue]:
        output_units = {o.name: o.unit for o in self.spec.output_schema}
        predictions: dict[str, PredictionValue] = {}

        for key, value in metrics.items():
            confidence = self._confidence_for(key, value, metadata)
            predictions[key] = PredictionValue(
                value=float(value),
                confidence=confidence,
                unit=output_units.get(key, ""),
            )

        return predictions

    def _confidence_for(
        self,
        key: str,
        value: float,
        metadata: dict[str, Any],
    ) -> float | None:
        if not self.spec.supports_uncertainty:
            return 1.0

        if key == "var_95":
            return 0.95
        if key == "cvar_95":
            return 0.95
        if "simulations" in metadata and key == "expected_terminal_price":
            return 0.85

        return 0.9

    def _build_explanation(self, predictions: dict[str, PredictionValue]) -> str:
        if not predictions:
            return "No predictions produced."
        top = sorted(predictions.items(), key=lambda item: abs(item[1].value), reverse=True)[:3]
        parts = [
            f"{name.replace('_', ' ')} = {pred.value:.4f}"
            + (f" (confidence {pred.confidence:.0%})" if pred.confidence is not None else "")
            for name, pred in top
        ]
        return f"{self.spec.label} inference completed. Key outputs: " + "; ".join(parts) + "."
