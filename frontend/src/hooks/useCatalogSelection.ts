"use client";

import { useEffect, useMemo, useState } from "react";
import { getCatalog } from "@/lib/api";
import type { CatalogResponse, ParameterSchema, Selection } from "@/lib/types";
import { defaultParamValues, type DynamicParameterField } from "@/components/DynamicParameterForm";

function pickSelection(
  domains: CatalogResponse["domains"],
  initial?: Partial<Selection>,
  lockDomain?: string
): Selection | null {
  const pool = lockDomain ? domains.filter((d) => d.id === lockDomain) : domains;
  if (!pool.length) return null;

  if (initial?.domainId && initial.subdomainId && initial.modelId) {
    const domain = pool.find((d) => d.id === initial.domainId) ?? pool[0];
    const subdomain =
      domain.subdomains.find((s) => s.id === initial.subdomainId) ?? domain.subdomains[0];
    const model =
      subdomain?.models.find((m) => m.id === initial.modelId) ?? subdomain?.models[0];
    if (subdomain && model) {
      return { domainId: domain.id, subdomainId: subdomain.id, modelId: model.id };
    }
  }

  const d = pool[0];
  const s = d.subdomains[0];
  const m = s?.models[0];
  if (!s || !m) return null;
  return { domainId: d.id, subdomainId: s.id, modelId: m.id };
}

export function useCatalogSelection(initial?: Partial<Selection>, lockDomain?: string) {
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string | number | boolean>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCatalog()
      .then((data) => {
        setCatalog(data);
        setSelection(pickSelection(data.domains, initial, lockDomain));
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load catalog"))
      .finally(() => setLoading(false));
  }, [initial?.domainId, initial?.modelId, initial?.subdomainId, lockDomain]);

  useEffect(() => {
    if (!catalog || !lockDomain) return;
    setSelection((prev) => {
      if (prev?.domainId === lockDomain) return prev;
      return pickSelection(catalog.domains, { domainId: lockDomain }, lockDomain);
    });
  }, [catalog, lockDomain]);

  const ctx = useMemo(() => {
    if (!catalog || !selection) return null;
    const domain = catalog.domains.find((d) => d.id === selection.domainId);
    const subdomain = domain?.subdomains.find((s) => s.id === selection.subdomainId);
    const model = subdomain?.models.find((m) => m.id === selection.modelId);
    if (!domain || !subdomain || !model) return null;
    return { domain, subdomain, model };
  }, [catalog, selection]);

  const parameters: DynamicParameterField[] = useMemo(
    () => (ctx?.model.parameters ?? []) as DynamicParameterField[],
    [ctx?.model.parameters]
  );

  useEffect(() => {
    if (!ctx) return;
    setParamValues(defaultParamValues(ctx.model.parameters as DynamicParameterField[]));
  }, [ctx?.domain.id, ctx?.subdomain.id, ctx?.model.id]);

  return {
    catalog,
    selection,
    setSelection,
    paramValues,
    setParamValues,
    ctx,
    parameters,
    loading,
    error,
  };
}

export function catalogSelectors(
  catalog: CatalogResponse,
  selection: Selection,
  setSelection: (s: Selection) => void
) {
  const domain = catalog.domains.find((d) => d.id === selection.domainId);
  const subdomain = domain?.subdomains.find((s) => s.id === selection.subdomainId);
  return { domain, subdomain };
}
