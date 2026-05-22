"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { domainPath } from "@/components/domain/types";
import { Database, Loader2, Play, Rows3 } from "lucide-react";
import {
  listSyntheticDatasets,
  platformAnalyticsQuery,
  platformGenerate,
  type DatasetCatalogItem,
} from "@/lib/api";
import { DynamicParameterForm } from "../DynamicParameterForm";
import { CatalogSelectors } from "./CatalogSelectors";
import { useCatalogSelection } from "@/hooks/useCatalogSelection";

interface DataGenerationStudioProps {
  accentColor: string;
  domainId: string;
}

export function DataGenerationStudio({ accentColor, domainId }: DataGenerationStudioProps) {
  const router = useRouter();
  const {
    catalog,
    selection,
    setSelection,
    paramValues,
    setParamValues,
    ctx,
    parameters,
    loading: catalogLoading,
    error: catalogError,
  } = useCatalogSelection(undefined, domainId);
  const [datasets, setDatasets] = useState<DatasetCatalogItem[]>([]);
  const [lastResult, setLastResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewRows, setPreviewRows] = useState<Array<Record<string, unknown>>>([]);
  const [selectedDataset, setSelectedDataset] = useState<DatasetCatalogItem | null>(null);

  const refreshCatalog = useCallback(() => {
    listSyntheticDatasets().then((r) => setDatasets(r.datasets)).catch(() => setDatasets([]));
  }, []);

  useEffect(() => {
    refreshCatalog();
  }, [refreshCatalog]);

  const handleGenerate = async () => {
    if (!selection) return;
    setLoading(true);
    setError(null);
    try {
      const res = await platformGenerate({
        domain: selection.domainId,
        subdomain: selection.subdomainId,
        model: selection.modelId,
        inputs: paramValues,
      });
      setLastResult(res);
      refreshCatalog();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  const runDatasetAction = async (ds: DatasetCatalogItem, actionId: string) => {
    const action = ds.actions?.find((a) => a.id === actionId);
    if (!action) return;
    if (actionId === "send_to_ml_inference" && action.domain && action.subdomain && action.model) {
      router.push(
        domainPath(action.domain ?? domainId, "ml_inference", {
          subdomain: action.subdomain,
          model: action.model,
        })
      );
      return;
    }
    if (actionId === "preview_sql" && action.sql) {
      setLoading(true);
      try {
        const q = await platformAnalyticsQuery(action.sql, 20);
        setPreviewRows(q.rows);
        setSelectedDataset(ds);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Preview failed");
      } finally {
        setLoading(false);
      }
    }
  };

  if (catalogLoading || !catalog || !selection || !ctx) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  const domainDatasets = datasets.filter((row) => !row.domain || row.domain === domainId);
  const schemaCols = selectedDataset?.column_schema
    ? Object.entries(selectedDataset.column_schema)
    : [];
  const isPhysical = domainId === "physical";

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-zinc-500">
          <Database className="h-4 w-4" style={{ color: accentColor }} />
          Data Generation Studio
        </p>
        <CatalogSelectors
          catalog={catalog}
          selection={selection}
          onSelectionChange={setSelection}
          lockDomain={domainId}
        />
        <div className="mt-6">
          <DynamicParameterForm
            parameters={parameters}
            values={paramValues}
            onChange={(name, value) => setParamValues((p) => ({ ...p, [name]: value }))}
            accentColor={accentColor}
          />
        </div>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={loading}
          className="mt-4 inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
          style={{ backgroundColor: accentColor }}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {isPhysical ? "Generate solver dataset" : "Generate synthetic dataset"}
        </button>
        {(error || catalogError) && (
          <p className="mt-3 text-sm text-red-400">{error ?? catalogError}</p>
        )}
      </section>

      {lastResult && (
        <section className="glass rounded-2xl border border-white/10 p-5 text-sm">
          <p className="font-medium text-zinc-200">Last generation</p>
          <p className="mt-2 font-mono text-xs text-zinc-500">
            dataset: {String(lastResult.synthetic_dataset_id ?? lastResult.product_id ?? "—")}
          </p>
          {lastResult.validation != null && (
            <p className="mt-1 text-xs text-emerald-400/90">
              validation: {JSON.stringify(lastResult.validation)}
            </p>
          )}
        </section>
      )}

      <section className="glass rounded-2xl p-5">
        <h4 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
          <Rows3 className="h-4 w-4" style={{ color: accentColor }} />
          {isPhysical ? "Saved solver datasets" : "Saved synthetic datasets"}
        </h4>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs text-zinc-500">
            <thead>
              <tr className="border-b border-white/10 text-zinc-600">
                <th className="py-2 pr-4">Dataset</th>
                <th className="py-2 pr-4">Domain</th>
                <th className="py-2 pr-4">Rows</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {domainDatasets.map((row) => (
                <tr key={row.dataset_id} className="border-b border-white/5">
                  <td className="py-2 pr-4 font-mono text-zinc-400">{row.dataset_id}</td>
                  <td className="py-2 pr-4">{row.domain}</td>
                  <td className="py-2 pr-4">{row.row_count}</td>
                  <td className="py-2 space-x-2">
                    {(row.actions ?? []).map((a) => (
                      <button
                        key={a.id}
                        type="button"
                        onClick={() => runDatasetAction(row, a.id)}
                        className="text-sky-400 hover:underline"
                      >
                        {a.label}
                      </button>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selectedDataset && schemaCols.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-medium text-zinc-500">Schema — {selectedDataset.dataset_id}</p>
            <table className="mt-2 w-full text-left text-xs">
              <thead>
                <tr className="text-zinc-600">
                  <th className="py-1 pr-3">Column</th>
                  <th className="py-1">Type</th>
                </tr>
              </thead>
              <tbody>
                {schemaCols.map(([col, dtype]) => (
                  <tr key={col} className="border-t border-white/5 text-zinc-500">
                    <td className="py-1 pr-3 font-mono">{col}</td>
                    <td className="py-1">{String(dtype)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {previewRows.length > 0 && (
          <div className="mt-4 overflow-x-auto">
            <p className="mb-2 text-xs text-zinc-600">Preview rows</p>
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-zinc-600">
                  {Object.keys(previewRows[0] ?? {}).map((c) => (
                    <th key={c} className="py-1 pr-2">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.slice(0, 10).map((row, i) => (
                  <tr key={i} className="border-t border-white/5 text-zinc-500">
                    {Object.values(row).map((v, j) => (
                      <td key={j} className="py-1 pr-2 font-mono">
                        {String(v)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
