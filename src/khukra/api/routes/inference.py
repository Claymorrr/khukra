from fastapi import APIRouter, Depends, HTTPException

from khukra.api.schemas import (
    BatchInferenceRequest,
    BatchInferenceResponse,
    FeatureSchemaField,
    InferenceModelInfo,
    InferenceModelsResponse,
    InferenceRequest,
    InferenceResponse,
    OutputSchemaField,
    PredictionField,
)
from khukra.auth.deps import get_current_user
from khukra.inference.engine import get_inference_engine
from khukra.inference.registry import model_key
from khukra.inference.types import PredictionResult
from khukra.inference.validator import InputValidationError

router = APIRouter(prefix="/inference")


def _to_response(result: PredictionResult) -> InferenceResponse:
    predictions = {
        k: PredictionField(value=v.value, confidence=v.confidence, unit=v.unit)
        for k, v in result.predictions.items()
    }
    return InferenceResponse(
        inference_id=result.inference_id,
        run_id=result.inference_id,
        domain=result.domain,
        subdomain=result.subdomain,
        model_name=result.model_id,
        model_version=result.model_version,
        predictor_type=result.predictor_type,
        inputs=result.inputs,
        predictions=predictions,
        outputs=result.predictions_flat(),
        confidence=result.confidence_flat(),
        traces=result.traces,
        explanation=result.explanation,
        latency_ms=result.latency_ms,
        metadata={
            **result.metadata,
            "kind": "inference",
            "model_key": model_key(result.domain, result.subdomain, result.model_id),
        },
    )


@router.get("/models", response_model=InferenceModelsResponse)
def list_inference_models() -> InferenceModelsResponse:
    engine = get_inference_engine()
    models = [
        InferenceModelInfo(
            key=model_key(s.domain, s.subdomain, s.model_id),
            domain=s.domain,
            subdomain=s.subdomain,
            model_id=s.model_id,
            label=s.label,
            version=s.version,
            predictor_type=s.predictor_type,
            description=s.description,
            supports_uncertainty=s.supports_uncertainty,
            feature_schema=[
                FeatureSchemaField(
                    name=f.name,
                    type=f.type,
                    default=f.default,
                    label=f.label,
                    required=f.required,
                    description=f.description,
                )
                for f in s.feature_schema
            ],
            output_schema=[
                OutputSchemaField(name=o.name, label=o.label, unit=o.unit, description=o.description)
                for o in s.output_schema
            ],
        )
        for s in engine.list_models()
    ]
    return InferenceModelsResponse(models=models)


@router.get("/{inference_id}", response_model=InferenceResponse)
def get_inference(inference_id: str) -> InferenceResponse:
    record = get_inference_engine().get(inference_id)
    if not record:
        raise HTTPException(404, f"Inference not found: {inference_id}")

    predictions = {
        k: PredictionField(
            value=float(v["value"]),
            confidence=v.get("confidence"),
            unit=v.get("unit", ""),
        )
        for k, v in record["predictions"].items()
    }
    outputs = {k: p.value for k, p in predictions.items()}
    confidence = {k: p.confidence for k, p in predictions.items() if p.confidence is not None}

    return InferenceResponse(
        inference_id=record["inference_id"],
        run_id=record["inference_id"],
        domain=record["domain"],
        subdomain=record["subdomain"],
        model_name=record["model_id"],
        model_version=record["model_version"],
        predictor_type=record["predictor_type"],
        inputs=record["inputs"],
        predictions=predictions,
        outputs=outputs,
        confidence=confidence,
        traces={},
        explanation=record.get("explanation") or "",
        latency_ms=record.get("latency_ms", 0),
        metadata=record.get("metadata") or {},
    )


@router.post("", response_model=InferenceResponse)
def create_inference(
    body: InferenceRequest,
    user: dict | None = Depends(get_current_user),
) -> InferenceResponse:
    engine = get_inference_engine()
    user_id = user["user_id"] if user else None
    try:
        result = engine.predict(
            body.domain,
            body.subdomain,
            body.model,
            body.inputs,
            user_id=user_id,
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except InputValidationError as exc:
        raise HTTPException(422, str(exc)) from exc

    return _to_response(result)


@router.post("/batch", response_model=BatchInferenceResponse)
def create_batch_inference(
    body: BatchInferenceRequest,
    user: dict | None = Depends(get_current_user),
) -> BatchInferenceResponse:
    engine = get_inference_engine()
    user_id = user["user_id"] if user else None
    try:
        batch_id, results = engine.predict_batch(
            body.domain,
            body.subdomain,
            body.model,
            body.inputs,
            user_id=user_id,
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except InputValidationError as exc:
        raise HTTPException(422, str(exc)) from exc

    return BatchInferenceResponse(
        batch_id=batch_id,
        results=[_to_response(r) for r in results],
    )
