import { getStoredToken } from "../auth";
import type { QueryResult } from "@/lib/api";
import type { DataProductDetail, DataProductInfo, KnowledgeAssetInfo } from "../types";

const V1 = "/api/v1";

async function v1Fetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const res = await fetch(`${V1}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

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

export function zonePath(domainId: string, zone: AppZone, extra?: Record<string, string>) {
  const params = new URLSearchParams(extra);
  const q = params.toString() ? `?${params}` : "";
  return `/d/${domainId}/${zone}${q}`;
}
