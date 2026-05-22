export interface ParameterSchema {
  name: string;
  type: string;
  default: string | number | boolean;
  label: string;
  description?: string;
  unit?: string;
  min?: number | null;
  max?: number | null;
  step?: number | null;
  options?: Array<string | number | boolean>;
}

export interface ModelInfo {
  id: string;
  label: string;
  parameters: ParameterSchema[];
  model_kind?: string;
  predictor_type?: string;
  solver_spec?: Record<string, unknown>;
}

export interface SubdomainInfo {
  id: string;
  label: string;
  description: string;
  models: ModelInfo[];
}

export interface DataProductBindingInfo {
  family_id: string;
  label: string;
  kind: string;
  description?: string;
}

export interface DomainManifestInfo {
  entity_id?: string;
  version?: string;
  tagline: string;
  positioning: string;
  primary_focus: string[];
  model_families: string[];
  data_products: string[];
  data_product_bindings?: DataProductBindingInfo[];
  data_product_ids?: string[];
  recommended_workflows?: string[];
  ops_capabilities: string[];
  module_order: string[];
  roadmap: string[];
}

export interface DataProductInfo {
  product_id: string;
  name: string;
  kind: string;
  domain_ids: string[];
  source_type: string;
  source_id: string;
  storage_uri?: string | null;
  row_count?: number | null;
  column_schema: Record<string, string>;
  contract_id?: string | null;
  version_label: string;
  quality_status: string;
  lineage_status: string;
  metadata: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DataProductDetail extends DataProductInfo {
  versions: Array<Record<string, unknown>>;
  lineage_edges: Array<Record<string, unknown>>;
  profile?: Record<string, unknown> | null;
  preview?: { columns: string[]; rows: Array<Record<string, unknown>> } | null;
  knowledge_assets: KnowledgeAssetInfo[];
  saved_queries: SavedQueryInfo[];
}

/** Domain research / product development lake asset */
export interface LakeAssetInfo {
  lake_asset_id: string;
  name: string;
  lake_space: "research" | "development" | string;
  asset_kind: string;
  domain: string;
  source_type: string;
  source_id: string;
  legacy_product_id?: string | null;
  storage_uri?: string | null;
  row_count?: number | null;
  column_schema: Record<string, string>;
  contract_id?: string | null;
  version_label: string;
  quality_status: string;
  lineage_status: string;
  metadata: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DomainLakeSummary {
  domain: string;
  research_lake: {
    assets: LakeAssetInfo[];
    total: number;
    artifacts: Array<Record<string, unknown>>;
  };
  product_development_lake: {
    assets: LakeAssetInfo[];
    total: number;
    artifacts: Array<Record<string, unknown>>;
  };
  totals: {
    lake_assets: number;
    research_artifacts: number;
    development_artifacts: number;
  };
}

export interface DomainLakeDetail extends LakeAssetInfo {
  versions: Array<Record<string, unknown>>;
  lineage_edges: Array<Record<string, unknown>>;
  profile?: Record<string, unknown> | null;
  preview?: { columns: string[]; rows: Array<Record<string, unknown>> } | null;
  knowledge_assets: KnowledgeAssetInfo[];
  saved_queries: SavedQueryInfo[];
  research_artifacts: Array<Record<string, unknown>>;
  development_artifacts: Array<Record<string, unknown>>;
}

export interface KnowledgeAssetInfo {
  asset_id: string;
  asset_type: string;
  title: string;
  product_id?: string | null;
  domain?: string | null;
  content: Record<string, unknown>;
  version_label: string;
  created_at?: string | null;
}

export interface SavedQueryInfo {
  query_id: string;
  name: string;
  sql_text: string;
  product_id?: string | null;
  domain?: string | null;
  metadata: Record<string, unknown>;
  created_at?: string | null;
}

export interface VersioningSummary {
  app_release: string;
  catalog_schema_version: string;
  total_versions: number;
  entity_counts: Record<string, number>;
  compatibility_policy: Record<string, string>;
}

export interface DomainInfo {
  id: string;
  label: string;
  color: string;
  manifest?: DomainManifestInfo | null;
  subdomains: SubdomainInfo[];
}

export interface CatalogResponse {
  schema_version?: string;
  domains: DomainInfo[];
}

export interface PredictionField {
  value: number;
  confidence?: number | null;
  unit?: string;
}

export interface InferenceResponse {
  inference_id: string;
  run_id: string;
  domain: string;
  subdomain: string;
  model_name: string;
  model_version: string;
  predictor_type: string;
  inputs: Record<string, unknown>;
  predictions: Record<string, PredictionField>;
  outputs: Record<string, number>;
  confidence: Record<string, number>;
  traces: Record<string, number[]>;
  explanation: string;
  latency_ms: number;
  metadata: Record<string, unknown>;
}

export interface RunResponse {
  run_id: string;
  domain: string;
  subdomain: string;
  model_name: string;
  parameters: Record<string, unknown>;
  metrics: Record<string, number>;
  series: Record<string, number[]>;
  metadata: Record<string, unknown>;
  predictions?: Record<string, PredictionField>;
  confidence?: Record<string, number>;
  explanation?: string;
  model_version?: string;
  predictor_type?: string;
  latency_ms?: number;
}

export interface RunSummary {
  run_id: string;
  timestamp: string;
  domain: string;
  subdomain: string | null;
  model_name: string;
  metrics: Record<string, number>;
  sweep_id?: string | null;
}

export interface SweepResponse {
  sweep_id: string;
  run_ids: string[];
  total_runs: number;
  status: string;
}

export interface ComparisonResponse {
  comparison_id: string;
  name: string;
  run_ids: string[];
  summary: {
    metrics_table?: Array<Record<string, unknown>>;
    delta?: Record<string, { absolute: number; percent: number }>;
  };
  runs: Array<Record<string, unknown> | null>;
}

export interface UserInfo {
  user_id: string;
  email: string;
  display_name: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

export interface DatasetInfo {
  dataset_id: string;
  name: string;
  source_type: string;
  row_count: number;
  domain_tag: string | null;
  created_at: string;
}

export type Selection = {
  domainId: string;
  subdomainId: string;
  modelId: string;
};
