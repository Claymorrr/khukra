"""Platform workspace API: data generation, MLOps, ML inference, analytics, insights."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from khukra.api.routes.query import query_catalog, run_query
from khukra.api.schemas import (
    AnalyticsCatalogResponse,
    DataGenerationCatalogResponse,
    DataGenerationRequest,
    DataGenerationResponse,
    DatasetCatalogItem,
    FeatureSchemaField,
    InferenceModelInfo,
    InferenceModelsResponse,
    InferenceRequest,
    InferenceResponse,
    MLInsightExplainRequest,
    OutputSchemaField,
    PipelineTemplatesResponse,
    PlatformManifestResponse,
    PlatformSummaryResponse,
    PredictionField,
    QueryRequest,
    QueryResponse,
)
from khukra.auth.deps import require_user
from khukra.data.engine import get_engine
from khukra.inference.registry import model_key
from khukra.inference.types import PredictionResult
from khukra.inference.validator import InputValidationError
from khukra.services.insights import InsightsService
from khukra.services.ml_inference import MLInferenceService
from khukra.services.mlops_pipeline import MLOpsPipeline
from khukra.services.mlops_templates import MLOpsTemplateService
from khukra.services.platform_manifest import PlatformManifestService

router = APIRouter(prefix="/platform")
_mlops = MLOpsPipeline()
_ml = MLInferenceService()
_insights = InsightsService()
_manifest = PlatformManifestService()
_templates = MLOpsTemplateService()


@router.get("/manifest", response_model=PlatformManifestResponse)
def platform_manifest(_user: dict = Depends(require_user)) -> PlatformManifestResponse:
    return PlatformManifestResponse(**_manifest.build())


@router.get("/mlops/templates", response_model=PipelineTemplatesResponse)
def platform_mlops_templates(_user: dict = Depends(require_user)) -> PipelineTemplatesResponse:
    return PipelineTemplatesResponse(templates=_templates.list_templates())


def _to_inference_response(result: PredictionResult) -> InferenceResponse:
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
            "kind": "platform_ml_inference",
            "model_key": model_key(result.domain, result.subdomain, result.model_id),
        },
    )


@router.get("/summary", response_model=PlatformSummaryResponse)
def platform_summary(_user: dict = Depends(require_user)) -> PlatformSummaryResponse:
    data = _insights.platform_summary()
    return PlatformSummaryResponse(**data)


def _parse_json_field(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return None


@router.get("/data-generation/catalog", response_model=DataGenerationCatalogResponse)
def data_generation_catalog(_user: dict = Depends(require_user)) -> DataGenerationCatalogResponse:
    engine = get_engine()
    with engine.connect() as conn:
        df = conn.execute(
            """
            SELECT dataset_id, scenario_id, domain, subdomain, model_id,
                   file_uri, row_count, created_at, column_schema, profile, contract_result
            FROM synthetic_datasets
            ORDER BY created_at DESC
            LIMIT 50
            """
        ).fetchdf()
    datasets: list[DatasetCatalogItem] = []
    for _, row in df.iterrows():
        item = row.to_dict()
        created = item.get("created_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        domain = item.get("domain")
        subdomain = item.get("subdomain")
        model_id = item.get("model_id")
        actions = []
        if domain and subdomain and model_id:
            actions.append(
                {
                    "id": "send_to_ml_inference",
                    "label": "Send to ML inference",
                    "endpoint": "/api/platform/ml-inference",
                    "domain": domain,
                    "subdomain": subdomain,
                    "model": model_id,
                }
            )
        if item.get("file_uri"):
            actions.append(
                {
                    "id": "preview_sql",
                    "label": "Preview Parquet",
                    "sql": f"SELECT * FROM read_parquet('{item['file_uri']}') LIMIT 20",
                }
            )
        datasets.append(
            DatasetCatalogItem(
                dataset_id=str(item["dataset_id"]),
                scenario_id=str(item.get("scenario_id")) if item.get("scenario_id") else None,
                domain=str(domain) if domain else None,
                subdomain=str(subdomain) if subdomain else None,
                model_id=str(model_id) if model_id else None,
                file_uri=str(item.get("file_uri")) if item.get("file_uri") else None,
                row_count=int(item["row_count"]) if item.get("row_count") is not None else None,
                created_at=str(created) if created else None,
                column_schema=_parse_json_field(item.get("column_schema")),
                profile=_parse_json_field(item.get("profile")),
                contract_result=_parse_json_field(item.get("contract_result")),
                actions=actions,
            )
        )
    return DataGenerationCatalogResponse(datasets=datasets)


@router.post("/data-generation", response_model=DataGenerationResponse)
def platform_generate(
    body: DataGenerationRequest,
    _user: dict = Depends(require_user),
) -> DataGenerationResponse:
    try:
        result = _mlops.generate_synthetic_only(
            body.domain, body.subdomain, body.model, body.inputs
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return DataGenerationResponse(**result)


@router.post("/mlops/pipeline")
def platform_mlops_pipeline(
    body: DataGenerationRequest,
    user: dict = Depends(require_user),
) -> dict[str, Any]:
    try:
        return _mlops.run_full_pipeline(
            body.domain,
            body.subdomain,
            body.model,
            body.inputs,
            user.get("user_id"),
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/ml-inference/models", response_model=InferenceModelsResponse)
def platform_ml_models(_user: dict = Depends(require_user)) -> InferenceModelsResponse:
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
                OutputSchemaField(
                    name=o.name,
                    label=o.label,
                    unit=o.unit,
                    description=o.description,
                )
                for o in s.output_schema
            ],
        )
        for s in _ml.list_models()
    ]
    return InferenceModelsResponse(models=models)


@router.post("/ml-inference", response_model=InferenceResponse)
def platform_ml_inference(
    body: InferenceRequest,
    user: dict = Depends(require_user),
) -> InferenceResponse:
    try:
        result = _ml.predict(
            body.domain,
            body.subdomain,
            body.model,
            body.inputs,
            user_id=user.get("user_id"),
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except InputValidationError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
    return _to_inference_response(result)


@router.post("/analytics", response_model=QueryResponse)
def platform_analytics(
    body: QueryRequest,
    user: dict = Depends(require_user),
) -> QueryResponse:
    return run_query(body, user)


@router.get("/analytics/catalog", response_model=AnalyticsCatalogResponse)
def platform_analytics_catalog(user: dict = Depends(require_user)) -> AnalyticsCatalogResponse:
    data = query_catalog(user)
    return AnalyticsCatalogResponse(**data)


@router.get("/insights")
def platform_insights(_user: dict = Depends(require_user)) -> dict[str, Any]:
    return {
        "headline": "Insights engineering",
        "cards": _insights.build_cards(),
    }


@router.post("/insights/explain")
def platform_explain(
    body: MLInsightExplainRequest,
    _user: dict = Depends(require_user),
) -> dict[str, Any]:
    target = body.target.strip() or "platform"
    cards = _insights.build_cards()
    return {
        "answer": (
            f"ML insight summary for {target}: review dataset freshness, inference volume, "
            "lineage coverage, registry activity, and evaluation pass rate before promotion."
        ),
        "cards": cards,
    }
