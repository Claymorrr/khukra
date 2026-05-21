import type { DomainInfo, DomainManifestInfo } from "./types";

const DEFAULT_MODULE_ORDER = [
  "overview",
  "data_hub",
  "knowledge",
  "inference",
  "results",
  "sweeps",
  "compare",
  "docs",
  "history",
  "data",
  "data_generation",
  "mlops",
  "infraops",
  "devops",
  "ml_inference",
  "analytics",
  "insights",
];

const EMPTY_MANIFEST: DomainManifestInfo = {
  entity_id: "",
  version: "1.0.0",
  tagline: "",
  positioning: "",
  primary_focus: [],
  model_families: [],
  data_products: [],
  data_product_bindings: [],
  data_product_ids: [],
  recommended_workflows: [],
  ops_capabilities: [],
  module_order: DEFAULT_MODULE_ORDER,
  roadmap: [],
};

/** Ensure catalog domains always have a usable manifest (older API responses may omit it). */
export function normalizeDomainManifest(
  domainId: string,
  manifest?: Partial<DomainManifestInfo> | null
): DomainManifestInfo {
  const merged = { ...EMPTY_MANIFEST, ...(manifest ?? {}) };
  return {
    ...merged,
    entity_id: merged.entity_id || domainId,
    version: merged.version || "1.0.0",
    module_order:
      merged.module_order?.length > 0 ? merged.module_order : DEFAULT_MODULE_ORDER,
    primary_focus: merged.primary_focus ?? [],
    model_families: merged.model_families ?? [],
    data_products: merged.data_products ?? [],
    data_product_bindings: merged.data_product_bindings ?? [],
    data_product_ids: merged.data_product_ids ?? [],
    recommended_workflows: merged.recommended_workflows ?? [],
    ops_capabilities: merged.ops_capabilities ?? [],
    roadmap: merged.roadmap ?? [],
  };
}

export function normalizeDomain(domain: DomainInfo): DomainInfo {
  return {
    ...domain,
    manifest: normalizeDomainManifest(domain.id, domain.manifest),
  };
}
