"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BrainCircuit, Loader2, Play, ShieldCheck } from "lucide-react";
import { getPlatformMLModels, platformMLInference } from "@/lib/api";
import type { InferenceResponse } from "@/lib/types";
import { DynamicParameterForm, defaultParamValues, type DynamicParameterField } from "../DynamicParameterForm";
import { PredictionsGrid } from "../PredictionsGrid";
import { CatalogSelectors } from "./CatalogSelectors";
import { useCatalogSelection } from "@/hooks/useCatalogSelection";

interface MLInferencingPanelProps {
  accentColor: string;
  domainId: string;
}

export function MLInferencingPanel({ accentColor, domainId }: MLInferencingPanelProps) {
  const searchParams = useSearchParams();
  const initial = {
    domainId: searchParams.get("domain") ?? domainId,
    subdomainId: searchParams.get("subdomain") ?? undefined,
    modelId: searchParams.get("model") ?? undefined,
  };
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
  } = useCatalogSelection(
    initial.domainId && initial.subdomainId && initial.modelId ? initial : undefined,
    domainId
  );
  const [modelCount, setModelCount] = useState(0);
  const [mlSchema, setMlSchema] = useState<DynamicParameterField[] | null>(null);
  const [result, setResult] = useState<InferenceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPlatformMLModels()
      .then((r) => setModelCount(r.models.filter((m) => m.domain === domainId).length))
      .catch(() => setModelCount(0));
  }, [domainId]);

  useEffect(() => {
    if (!selection) return;
    getPlatformMLModels().then((r) => {
      const m = r.models.find(
        (x) =>
          x.domain === selection.domainId &&
          x.subdomain === selection.subdomainId &&
          x.model_id === selection.modelId
      );
      if (m) {
        const fields: DynamicParameterField[] = m.feature_schema.map((f) => ({
          name: f.name,
          type: f.type,
          default: f.default,
          label: f.label,
          description: f.description,
        }));
        setMlSchema(fields);
        setParamValues(defaultParamValues(fields));
      } else {
        setMlSchema(null);
      }
    });
  }, [selection?.domainId, selection?.subdomainId, selection?.modelId, setParamValues]);

  const formParams = mlSchema ?? parameters;

  const runInference = async () => {
    if (!selection) return;
    setLoading(true);
    setError(null);
    try {
      setResult(
        await platformMLInference({
          domain: selection.domainId,
          subdomain: selection.subdomainId,
          model: selection.modelId,
          inputs: paramValues,
        })
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "ML inference failed");
    } finally {
      setLoading(false);
    }
  };

  if (catalogLoading || !catalog || !selection || !ctx) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-zinc-500">
          <BrainCircuit className="h-4 w-4" style={{ color: accentColor }} />
          ML inferencing
        </p>
        <CatalogSelectors
          catalog={catalog}
          selection={selection}
          onSelectionChange={setSelection}
          lockDomain={domainId}
        />
        <div className="mt-6">
          <DynamicParameterForm
            parameters={formParams}
            values={paramValues}
            onChange={(name, value) => setParamValues((p) => ({ ...p, [name]: value }))}
            accentColor={accentColor}
          />
        </div>
        <p className="mt-2 flex items-center gap-2 text-xs text-emerald-400/90">
          <ShieldCheck className="h-3.5 w-3.5" />
          Inputs validated against inference feature schema from API metadata.
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={runInference}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
            style={{ backgroundColor: accentColor }}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            Run ML inference
          </button>
          <span className="text-xs text-zinc-600">{modelCount} models in registry</span>
        </div>
        {(error || catalogError) && (
          <p className="mt-3 text-sm text-red-400">{error ?? catalogError}</p>
        )}
      </section>

      {result && (
        <div className="space-y-6">
          <section className="glass rounded-2xl p-5">
            <p className="text-xs uppercase text-zinc-600">Inference result</p>
            <h4 className="mt-1 font-mono text-sm text-zinc-200">{result.inference_id}</h4>
            <p className="mt-2 text-xs text-zinc-500">
              v{result.model_version} · {result.predictor_type} · {result.latency_ms} ms
            </p>
          </section>
          <PredictionsGrid predictions={result.predictions} accentColor={accentColor} />
        </div>
      )}
    </div>
  );
}
