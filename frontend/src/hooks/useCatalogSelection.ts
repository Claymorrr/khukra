"use client";

import { useEffect, useMemo, useState } from "react";
import { getCatalog } from "@/lib/api";
import type { CatalogResponse, ParameterSchema, Selection } from "@/lib/types";
import { defaultParamValues, type DynamicParameterField } from "@/components/DynamicParameterForm";

export function useCatalogSelection(initial?: Partial<Selection>) {
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string | number | boolean>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCatalog()
      .then((data) => {
        setCatalog(data);
        if (initial?.domainId && initial.subdomainId && initial.modelId) {
          setSelection({
            domainId: initial.domainId,
            subdomainId: initial.subdomainId,
            modelId: initial.modelId,
          });
        } else {
          const d = data.domains[0];
          const s = d.subdomains[0];
          const m = s.models[0];
          setSelection({ domainId: d.id, subdomainId: s.id, modelId: m.id });
        }
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load catalog"))
      .finally(() => setLoading(false));
  }, [initial?.domainId, initial?.modelId, initial?.subdomainId]);

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
