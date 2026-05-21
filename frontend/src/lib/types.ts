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
}

export interface SubdomainInfo {
  id: string;
  label: string;
  description: string;
  models: ModelInfo[];
}

export interface DomainManifestInfo {
  entity_id?: string;
  version?: string;
  tagline: string;
  positioning: string;
  primary_focus: string[];
  model_families: string[];
  data_products: string[];
  ops_capabilities: string[];
  module_order: string[];
  roadmap: string[];
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
