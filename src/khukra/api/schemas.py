from typing import Any

from pydantic import BaseModel, Field


class ParameterSchema(BaseModel):
    name: str
    type: str
    default: Any
    label: str
    description: str = ""
    unit: str = ""
    min: float | int | None = None
    max: float | int | None = None
    step: float | int | None = None
    options: list[str | int | float | bool] = Field(default_factory=list)


class ModelInfo(BaseModel):
    id: str
    label: str
    parameters: list[ParameterSchema]
    model_kind: str = ""
    predictor_type: str = ""
    solver_spec: dict[str, Any] = Field(default_factory=dict)


class SubdomainInfo(BaseModel):
    id: str
    label: str
    description: str
    models: list[ModelInfo]


class DataProductBindingInfo(BaseModel):
    family_id: str
    label: str
    kind: str = "synthetic"
    description: str = ""


class DomainManifestInfo(BaseModel):
    entity_id: str = ""
    version: str = "1.0.0"
    tagline: str = ""
    positioning: str = ""
    primary_focus: list[str] = Field(default_factory=list)
    model_families: list[str] = Field(default_factory=list)
    data_products: list[str] = Field(default_factory=list)
    data_product_bindings: list[DataProductBindingInfo] = Field(default_factory=list)
    data_product_ids: list[str] = Field(default_factory=list)
    recommended_workflows: list[str] = Field(default_factory=list)
    ops_capabilities: list[str] = Field(default_factory=list)
    module_order: list[str] = Field(default_factory=list)
    roadmap: list[str] = Field(default_factory=list)


class DataProductInfo(BaseModel):
    product_id: str
    name: str
    kind: str
    domain_ids: list[str] = Field(default_factory=list)
    source_type: str
    source_id: str
    storage_uri: str | None = None
    row_count: int | None = None
    column_schema: dict[str, Any] = Field(default_factory=dict)
    contract_id: str | None = None
    version_label: str = "1.0.0"
    quality_status: str = "unknown"
    lineage_status: str = "partial"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None


class DataProductListResponse(BaseModel):
    products: list[DataProductInfo]
    total: int


class DataProductDetail(DataProductInfo):
    versions: list[dict[str, Any]] = Field(default_factory=list)
    lineage_edges: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] | None = None
    preview: dict[str, Any] | None = None
    knowledge_assets: list["KnowledgeAssetInfo"] = Field(default_factory=list)
    saved_queries: list["SavedQueryInfo"] = Field(default_factory=list)


class LakeAssetInfo(BaseModel):
    lake_asset_id: str
    name: str
    lake_space: str
    asset_kind: str
    domain: str
    source_type: str
    source_id: str
    legacy_product_id: str | None = None
    storage_uri: str | None = None
    row_count: int | None = None
    column_schema: dict[str, Any] = Field(default_factory=dict)
    contract_id: str | None = None
    version_label: str = "1.0.0"
    quality_status: str = "unknown"
    lineage_status: str = "partial"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None


class LakeAssetListResponse(BaseModel):
    domain: str
    lake_space: str | None = None
    assets: list[LakeAssetInfo]
    total: int


class LakeArtifactInfo(BaseModel):
    artifact_id: str
    lake_asset_id: str | None = None
    domain: str
    artifact_type: str
    title: str
    content: dict[str, Any] = Field(default_factory=dict)
    version_label: str = "1.0.0"
    created_at: str | None = None


class LakeArtifactCreate(BaseModel):
    artifact_type: str
    title: str
    content: dict[str, Any] = Field(default_factory=dict)
    lake_asset_id: str | None = None


class DomainLakeSummary(BaseModel):
    domain: str
    research_lake: dict[str, Any]
    product_development_lake: dict[str, Any]
    totals: dict[str, int]


class DomainLakeDetail(LakeAssetInfo):
    versions: list[dict[str, Any]] = Field(default_factory=list)
    lineage_edges: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] | None = None
    preview: dict[str, Any] | None = None
    knowledge_assets: list["KnowledgeAssetInfo"] = Field(default_factory=list)
    saved_queries: list["SavedQueryInfo"] = Field(default_factory=list)
    research_artifacts: list[LakeArtifactInfo] = Field(default_factory=list)
    development_artifacts: list[LakeArtifactInfo] = Field(default_factory=list)


class KnowledgeAssetInfo(BaseModel):
    asset_id: str
    asset_type: str
    title: str
    product_id: str | None = None
    domain: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    version_label: str = "1.0.0"
    created_at: str | None = None


class KnowledgeAssetCreate(BaseModel):
    asset_type: str
    title: str
    content: dict[str, Any] = Field(default_factory=dict)
    product_id: str | None = None
    domain: str | None = None


class SavedQueryInfo(BaseModel):
    query_id: str
    name: str
    sql_text: str
    product_id: str | None = None
    domain: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None


class SavedQueryCreate(BaseModel):
    name: str
    sql_text: str
    product_id: str | None = None
    domain: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EntityVersionInfo(BaseModel):
    version_id: str
    entity_type: str
    entity_id: str
    version_label: str
    status: str = "active"
    content_hash: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_version_id: str | None = None
    created_at: Any = None


class EntityVersionListResponse(BaseModel):
    entity_type: str
    entity_id: str
    latest: EntityVersionInfo | None = None
    versions: list[EntityVersionInfo] = Field(default_factory=list)


class VersioningSummaryResponse(BaseModel):
    app_release: str
    catalog_schema_version: str
    total_versions: int
    entity_counts: dict[str, int] = Field(default_factory=dict)
    compatibility_policy: dict[str, str] = Field(default_factory=dict)


class DomainInfo(BaseModel):
    id: str
    label: str
    color: str
    manifest: DomainManifestInfo = Field(default_factory=DomainManifestInfo)
    subdomains: list[SubdomainInfo]


class CatalogResponse(BaseModel):
    schema_version: str = "1.0"
    domains: list[DomainInfo]


class RunRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    domain: str
    subdomain: str
    model_name: str
    parameters: dict[str, Any]
    metrics: dict[str, float]
    series: dict[str, list[float]]
    metadata: dict[str, Any] = Field(default_factory=dict)


class InferenceRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: dict[str, Any] = Field(default_factory=dict)


class PredictionField(BaseModel):
    value: float
    confidence: float | None = None
    unit: str = ""


class FeatureSchemaField(BaseModel):
    name: str
    type: str
    default: Any
    label: str
    required: bool = False
    description: str = ""


class OutputSchemaField(BaseModel):
    name: str
    label: str
    unit: str = ""
    description: str = ""


class InferenceModelInfo(BaseModel):
    key: str
    domain: str
    subdomain: str
    model_id: str
    label: str
    version: str
    predictor_type: str
    description: str
    supports_uncertainty: bool
    feature_schema: list[FeatureSchemaField]
    output_schema: list[OutputSchemaField]


class InferenceModelsResponse(BaseModel):
    models: list[InferenceModelInfo]


class InferenceResponse(BaseModel):
    inference_id: str
    run_id: str
    domain: str
    subdomain: str
    model_name: str
    model_version: str
    predictor_type: str
    inputs: dict[str, Any]
    predictions: dict[str, PredictionField]
    outputs: dict[str, float]
    confidence: dict[str, float] = Field(default_factory=dict)
    traces: dict[str, list[float]]
    explanation: str = ""
    latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchInferenceRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: list[dict[str, Any]] = Field(default_factory=list)


class BatchInferenceResponse(BaseModel):
    batch_id: str
    results: list[InferenceResponse]


class RunSummary(BaseModel):
    run_id: str
    timestamp: str
    domain: str
    subdomain: str | None = None
    model_name: str
    metrics: dict[str, float]
    sweep_id: str | None = None


class SweepRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    sweep: dict[str, list[Any]]
    base_parameters: dict[str, Any] = Field(default_factory=dict)


class SweepResponse(BaseModel):
    sweep_id: str
    run_ids: list[str]
    total_runs: int
    status: str


class ComparisonRequest(BaseModel):
    name: str
    run_ids: list[str]


class ComparisonResponse(BaseModel):
    comparison_id: str
    name: str
    run_ids: list[str]
    summary: dict[str, Any]
    runs: list[dict[str, Any] | None] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]


class DatasetInfo(BaseModel):
    dataset_id: str
    name: str
    source_type: str
    row_count: int
    domain_tag: str | None = None
    created_at: str


class IngestResponse(BaseModel):
    job_id: str
    dataset_id: str
    product_id: str | None = None
    rows: int
    columns: list[str]


class QueryRequest(BaseModel):
    sql: str
    limit: int = Field(default=100, ge=1, le=1000)


class QueryResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    limited_to: int
    duration_ms: float


class InsightCard(BaseModel):
    title: str
    value: str
    detail: str
    tone: str = "neutral"


class PlatformSummaryResponse(BaseModel):
    headline: str
    cards: list[InsightCard]
    modules: list[dict[str, Any]]


class DataGenerationRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: dict[str, Any] = Field(default_factory=dict)


class DataGenerationResponse(BaseModel):
    scenario_id: str | None = None
    synthetic_dataset_id: str | None = None
    validation: dict[str, Any] | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class MLInsightExplainRequest(BaseModel):
    target: str


class PlatformModuleAction(BaseModel):
    id: str
    label: str
    endpoint: str = ""


class PlatformModuleManifest(BaseModel):
    id: str
    label: str
    description: str
    route_id: str
    icon: str = "layout-dashboard"
    order: int = 0
    capabilities: list[str] = Field(default_factory=list)
    actions: list[PlatformModuleAction] = Field(default_factory=list)
    required_roles: list[str] = Field(default_factory=list)
    enabled: bool = True


class PlatformDomainManifest(BaseModel):
    id: str
    label: str
    color: str = "#38bdf8"
    icon: str = "box"
    order: int = 0


class PlatformManifestResponse(BaseModel):
    version: str
    workspace: str
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    domains: list[PlatformDomainManifest] = Field(default_factory=list)
    modules: list[PlatformModuleManifest]


class PipelineTemplateInfo(BaseModel):
    id: str
    label: str
    description: str
    endpoint: str
    required_inputs: list[str] = Field(default_factory=list)
    optional_inputs: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)


class PipelineTemplatesResponse(BaseModel):
    templates: list[PipelineTemplateInfo]


class QueryExampleGroup(BaseModel):
    group: str
    examples: list[dict[str, str]]


class AnalyticsCatalogResponse(BaseModel):
    tables: list[dict[str, Any]]
    examples: list[dict[str, str]] = Field(default_factory=list)
    example_groups: list[QueryExampleGroup] = Field(default_factory=list)


class DatasetCatalogItem(BaseModel):
    dataset_id: str
    scenario_id: str | None = None
    domain: str | None = None
    subdomain: str | None = None
    model_id: str | None = None
    file_uri: str | None = None
    row_count: int | None = None
    created_at: str | None = None
    column_schema: dict[str, Any] | None = None
    profile: dict[str, Any] | None = None
    contract_result: dict[str, Any] | None = None
    actions: list[dict[str, str]] = Field(default_factory=list)


class DataGenerationCatalogResponse(BaseModel):
    datasets: list[DatasetCatalogItem]
