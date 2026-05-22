import { getStoredToken } from "../auth";
import { resolveApiRoot } from "../apiBase";
import type { QueryResult } from "@/lib/api";
import type {
  DataProductDetail,
  DataProductInfo,
  DomainLakeDetail,
  DomainLakeSummary,
  KnowledgeAssetInfo,
  LakeAssetInfo,
} from "../types";

const V1 = () => `${resolveApiRoot()}/v1`;

async function v1Fetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const res = await fetch(`${V1()}${path}`, {
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
      throw new Error(
        "API route not found. Restart the backend: khukra-api (port 8000 must include /api/v1 routes)."
      );
    }
    throw new Error(text || `Request failed: ${res.status}`);
  }
  const body = await res.text();
  const trimmed = body.trim();
  if (!trimmed) throw new Error("Empty response from API.");
  try {
    return JSON.parse(trimmed) as T;
  } catch {
    throw new Error(
      `API returned non-JSON (HTTP ${res.status}). Check NEXT_PUBLIC_API_URL and that khukra-api is running.`
    );
  }
}

export function v1GetDomainLake(domain: string): Promise<DomainLakeSummary> {
  return v1Fetch(`/domains/${encodeURIComponent(domain)}/lake`);
}

export function v1SyncDomainLake(domain: string): Promise<{ domain: string; synced: number }> {
  return v1Fetch(`/domains/${encodeURIComponent(domain)}/lake/sync`, { method: "POST" });
}

export function v1ListLakeAssets(
  domain: string,
  lakeSpace?: "research" | "development"
): Promise<{ domain: string; assets: LakeAssetInfo[]; total: number }> {
  const params = new URLSearchParams();
  if (lakeSpace) params.set("lake_space", lakeSpace);
  const q = params.toString() ? `?${params}` : "";
  return v1Fetch(`/domains/${encodeURIComponent(domain)}/lake/assets${q}`);
}

export function v1GetLakeAsset(domain: string, lakeAssetId: string): Promise<DomainLakeDetail> {
  return v1Fetch(
    `/domains/${encodeURIComponent(domain)}/lake/assets/${encodeURIComponent(lakeAssetId)}`
  );
}

/** @deprecated Prefer v1ListLakeAssets */
export function v1ListProducts(domain?: string): Promise<{ products: DataProductInfo[]; total: number }> {
  const q = domain ? `?domain=${encodeURIComponent(domain)}` : "";
  return v1Fetch(`/products${q}`);
}

export function v1GetProduct(productId: string): Promise<DataProductDetail> {
  return v1Fetch(`/products/${encodeURIComponent(productId)}`);
}

export function v1SyncProducts(): Promise<{ synced: number }> {
  return v1Fetch("/products/sync", { method: "POST" });
}

export function v1ListKnowledge(domain?: string, productId?: string): Promise<KnowledgeAssetInfo[]> {
  const params = new URLSearchParams();
  if (domain) params.set("domain", domain);
  if (productId) params.set("product_id", productId);
  const q = params.toString() ? `?${params}` : "";
  return v1Fetch(`/knowledge/assets${q}`);
}

export function v1WorkflowQuery(body: {
  sql: string;
  limit?: number;
  domain?: string;
  product_id?: string;
}): Promise<QueryResult & { workflow_run_id: string; saved_query_id?: string }> {
  return v1Fetch("/workflows/query", { method: "POST", body: JSON.stringify(body) });
}

export function v1Lineage(entityType: string, entityId: string, depth = 2): Promise<{
  root: { entity_type: string; entity_id: string };
  nodes: Array<{ entity_type: string; entity_id: string }>;
  edges: Array<Record<string, unknown>>;
}> {
  return v1Fetch(`/lineage/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}?depth=${depth}`);
}

export type AppZone = "discover" | "data" | "knowledge" | "workflows" | "operations";

export type WorkloadInfo = {
  workload_id: string;
  domain: string;
  subdomain: string;
  model_id: string;
  label: string;
  workload_kind: string;
  lifecycle_stage: string;
  operation_verb: string;
};

export function v1ListWorkloads(
  domain: string,
  opts?: { lifecycle_stage?: string; workload_kind?: string }
): Promise<{ domain: string; workloads: WorkloadInfo[]; total: number }> {
  const params = new URLSearchParams();
  if (opts?.lifecycle_stage) params.set("lifecycle_stage", opts.lifecycle_stage);
  if (opts?.workload_kind) params.set("workload_kind", opts.workload_kind);
  const q = params.toString() ? `?${params}` : "";
  return v1Fetch(`/domains/${encodeURIComponent(domain)}/workloads${q}`);
}

export function v1GetDomainEnvironment(domain: string): Promise<Record<string, unknown>> {
  return v1Fetch(`/domains/${encodeURIComponent(domain)}/environment`);
}

export function zonePath(domainId: string, zone: AppZone, extra?: Record<string, string>) {
  const params = new URLSearchParams(extra);
  const q = params.toString() ? `?${params}` : "";
  return `/d/${domainId}/${zone}${q}`;
}
