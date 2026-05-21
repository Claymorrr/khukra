import { getStoredToken } from "./auth";
import type {
  CatalogResponse,
  ComparisonResponse,
  DatasetInfo,
  InferenceResponse,
  RunResponse,
  RunSummary,
  SweepResponse,
  TokenResponse,
  VersioningSummary,
} from "./types";

const API_BASE = "/api";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    try {
      const json = JSON.parse(text) as { detail?: string | Array<{ msg: string }> };
      if (typeof json.detail === "string") throw new Error(json.detail);
      if (Array.isArray(json.detail)) {
        throw new Error(json.detail.map((d) => d.msg).join(", "));
      }
    } catch (e) {
      if (e instanceof Error && e.message !== text) throw e;
    }
    if (res.status === 404) {
      throw new Error("API not found. Start the backend with: khukra-api");
    }
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getCatalog(): Promise<CatalogResponse> {
  return fetchJson("/catalog");
}

export function getVersioningSummary(): Promise<VersioningSummary> {
  return fetchJson("/versioning/summary");
}

export function getStats(): Promise<{
  runs: number;
  inferences?: number;
  sweeps: number;
  datasets: number;
  comparisons: number;
  synthetic_datasets?: number;
  artifacts?: number;
  evaluations?: number;
  domains?: number;
  subdomains?: number;
}> {
  return fetchJson("/stats");
}

export function runMLOpsPipeline(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs?: Record<string, unknown>;
}): Promise<Record<string, unknown>> {
  return fetchJson("/synthetic/pipeline", { method: "POST", body: JSON.stringify(body) });
}

export function generateSynthetic(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs?: Record<string, unknown>;
}): Promise<Record<string, unknown>> {
  return fetchJson("/synthetic/generate", { method: "POST", body: JSON.stringify(body) });
}

export function listArtifacts(domain?: string): Promise<{ artifacts: Array<Record<string, unknown>> }> {
  const q = domain ? `?domain=${encodeURIComponent(domain)}` : "";
  return fetchJson(`/registry/artifacts${q}`);
}

export function listEvaluations(): Promise<{ evaluations: Array<Record<string, unknown>> }> {
  return fetchJson("/evaluations");
}

export function getLineage(entityId: string): Promise<{ entity_id: string; edges: Array<Record<string, unknown>> }> {
  return fetchJson(`/lineage/${encodeURIComponent(entityId)}`);
}

export interface QueryResult {
  sql: string;
  columns: string[];
  rows: Array<Record<string, unknown>>;
  row_count: number;
  limited_to: number;
  duration_ms: number;
}

export interface QueryCatalog {
  tables: Array<{
    table: string;
    row_count: number;
    columns: Array<{ name: string; type: string }>;
  }>;
  examples: Array<{ title: string; sql: string }>;
  example_groups?: Array<{
    group: string;
    examples: Array<{ title: string; sql: string }>;
  }>;
}

export function runDuckDBQuery(sql: string, limit = 100): Promise<QueryResult> {
  return fetchJson("/query", {
    method: "POST",
    body: JSON.stringify({ sql, limit }),
  });
}

export function getQueryCatalog(): Promise<QueryCatalog> {
  return fetchJson("/query/catalog");
}

export function createRun(body: {
  domain: string;
  subdomain: string;
  model: string;
  parameters: Record<string, unknown>;
}): Promise<RunResponse> {
  return fetchJson("/runs", { method: "POST", body: JSON.stringify(body) });
}

export function createInference(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs: Record<string, unknown>;
}): Promise<RunResponse> {
  return fetchJson<InferenceResponse>("/inference", {
    method: "POST",
    body: JSON.stringify(body),
  }).then(mapInferenceToRun);
}

export function getInferenceModels(): Promise<{
  models: Array<{
    key: string;
    domain: string;
    subdomain: string;
    model_id: string;
    version: string;
    predictor_type: string;
    supports_uncertainty: boolean;
  }>;
}> {
  return fetchJson("/inference/models");
}

function mapInferenceToRun(inference: InferenceResponse): RunResponse {
  return {
    run_id: inference.run_id,
    domain: inference.domain,
    subdomain: inference.subdomain,
    model_name: inference.model_name,
    parameters: inference.inputs,
    metrics: inference.outputs,
    series: inference.traces,
    metadata: inference.metadata,
    predictions: inference.predictions,
    confidence: inference.confidence,
    explanation: inference.explanation,
    model_version: inference.model_version,
    predictor_type: inference.predictor_type,
    latency_ms: inference.latency_ms,
  };
}

export function listRuns(domain?: string, sweepId?: string): Promise<RunSummary[]> {
  const params = new URLSearchParams();
  if (domain) params.set("domain", domain);
  if (sweepId) params.set("sweep_id", sweepId);
  const q = params.toString() ? `?${params}` : "";
  return fetchJson(`/runs${q}`);
}

export function createSweep(body: {
  domain: string;
  subdomain: string;
  model: string;
  sweep: Record<string, (number | string)[]>;
  base_parameters?: Record<string, unknown>;
}): Promise<SweepResponse> {
  return fetchJson("/sweeps", { method: "POST", body: JSON.stringify(body) });
}

export function listSweeps(): Promise<Array<Record<string, unknown>>> {
  return fetchJson("/sweeps");
}

export function createComparison(name: string, run_ids: string[]): Promise<ComparisonResponse> {
  return fetchJson("/comparisons", {
    method: "POST",
    body: JSON.stringify({ name, run_ids }),
  });
}

export function listComparisons(): Promise<Array<Record<string, unknown>>> {
  return fetchJson("/comparisons");
}

export function getComparison(id: string): Promise<ComparisonResponse> {
  return fetchJson(`/comparisons/${id}`);
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return fetchJson("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(
  email: string,
  password: string,
  display_name: string
): Promise<TokenResponse> {
  return fetchJson("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name }),
  });
}

export function listDatasets(domainTag?: string): Promise<DatasetInfo[]> {
  const q = domainTag ? `?domain_tag=${encodeURIComponent(domainTag)}` : "";
  return fetchJson(`/datasets${q}`);
}

export async function ingestDataset(
  file: File,
  name?: string,
  domainTag?: string
): Promise<{ dataset_id: string; rows: number }> {
  const token = getStoredToken();
  const form = new FormData();
  form.append("file", file);
  if (name) form.append("name", name);
  if (domainTag) form.append("domain_tag", domainTag);

  const res = await fetch(`${API_BASE}/datasets/ingest`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function exportUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export interface InsightCard {
  title: string;
  value: string;
  detail: string;
  tone: string;
}

export interface PlatformSummary {
  headline: string;
  cards: InsightCard[];
  modules: Array<{ id: string; label: string; status: string }>;
}

export function getPlatformSummary(): Promise<PlatformSummary> {
  return fetchJson("/platform/summary");
}

export interface PlatformModuleManifest {
  id: string;
  label: string;
  description: string;
  route_id: string;
  icon: string;
  order: number;
  capabilities: string[];
  actions: Array<{ id: string; label: string; endpoint?: string }>;
  required_roles: string[];
  enabled: boolean;
}

export interface PlatformDomainManifest {
  id: string;
  label: string;
  color: string;
  icon: string;
  order: number;
}

export interface PlatformManifest {
  version: string;
  workspace: string;
  feature_flags: Record<string, boolean>;
  domains: PlatformDomainManifest[];
  modules: PlatformModuleManifest[];
}

export function getPlatformManifest(): Promise<PlatformManifest> {
  return fetchJson("/platform/manifest");
}

export interface PipelineTemplate {
  id: string;
  label: string;
  description: string;
  endpoint: string;
  required_inputs: string[];
  optional_inputs: string[];
  expected_outputs: string[];
}

export function getPipelineTemplates(): Promise<{ templates: PipelineTemplate[] }> {
  return fetchJson("/platform/mlops/templates");
}

export interface DatasetCatalogItem {
  dataset_id: string;
  scenario_id?: string | null;
  domain?: string | null;
  subdomain?: string | null;
  model_id?: string | null;
  file_uri?: string | null;
  row_count?: number | null;
  created_at?: string | null;
  column_schema?: Record<string, unknown> | null;
  profile?: Record<string, unknown> | null;
  contract_result?: Record<string, unknown> | null;
  actions?: Array<Record<string, string>>;
}

export function listSyntheticDatasets(): Promise<{ datasets: DatasetCatalogItem[] }> {
  return fetchJson("/platform/data-generation/catalog");
}

export function platformGenerate(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs?: Record<string, unknown>;
}): Promise<Record<string, unknown>> {
  return fetchJson("/platform/data-generation", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function platformMLOpsPipeline(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs?: Record<string, unknown>;
}): Promise<Record<string, unknown>> {
  return fetchJson("/platform/mlops/pipeline", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getPlatformMLModels(): Promise<{
  models: Array<{
    key: string;
    domain: string;
    subdomain: string;
    model_id: string;
    label: string;
    version: string;
    predictor_type: string;
    description: string;
    supports_uncertainty: boolean;
    feature_schema: Array<{
      name: string;
      type: string;
      default: string | number | boolean;
      label: string;
      required: boolean;
      description: string;
    }>;
    output_schema: Array<{
      name: string;
      label: string;
      unit: string;
      description: string;
    }>;
  }>;
}> {
  return fetchJson("/platform/ml-inference/models");
}

export function platformMLInference(body: {
  domain: string;
  subdomain: string;
  model: string;
  inputs?: Record<string, unknown>;
}): Promise<InferenceResponse> {
  return fetchJson("/platform/ml-inference", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function platformInsights(): Promise<{ headline: string; cards: InsightCard[] }> {
  return fetchJson("/platform/insights");
}

export function platformExplain(target: string): Promise<{
  answer: string;
  cards: InsightCard[];
}> {
  return fetchJson("/platform/insights/explain", {
    method: "POST",
    body: JSON.stringify({ target }),
  });
}

export function platformAnalyticsQuery(sql: string, limit = 100): Promise<QueryResult> {
  return fetchJson("/platform/analytics", {
    method: "POST",
    body: JSON.stringify({ sql, limit }),
  });
}

export function getPlatformAnalyticsCatalog(): Promise<QueryCatalog> {
  return fetchJson("/platform/analytics/catalog");
}

