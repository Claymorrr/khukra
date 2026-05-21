"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Play, Workflow } from "lucide-react";
import {
  getPipelineTemplates,
  getStats,
  listArtifacts,
  listEvaluations,
  platformGenerate,
  platformMLInference,
  platformMLOpsPipeline,
  type PipelineTemplate,
} from "@/lib/api";
import { DynamicParameterForm } from "../DynamicParameterForm";
import { CatalogSelectors } from "./CatalogSelectors";
import { useCatalogSelection } from "@/hooks/useCatalogSelection";

interface PlatformMLOpsPanelProps {
  accentColor: string;
  domainId: string;
}

export function PlatformMLOpsPanel({ accentColor, domainId }: PlatformMLOpsPanelProps) {
  const {
    catalog,
    selection,
    setSelection,
    paramValues,
    setParamValues,
    ctx,
    parameters,
    loading: catalogLoading,
  } = useCatalogSelection(undefined, domainId);
  const [templates, setTemplates] = useState<PipelineTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("full_pipeline");
  const [stats, setStats] = useState<Record<string, number>>({});
  const [artifacts, setArtifacts] = useState<Array<Record<string, unknown>>>([]);
  const [evaluations, setEvaluations] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastJob, setLastJob] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    getPipelineTemplates().then((r) => {
      setTemplates(r.templates);
      if (r.templates.length) setSelectedTemplate(r.templates[0].id);
    });
  }, []);

  const refresh = useCallback(() => {
    getStats().then(setStats).catch(() => {});
    if (selection?.domainId) {
      listArtifacts(selection.domainId).then((r) => setArtifacts(r.artifacts)).catch(() => {});
    }
    listEvaluations().then((r) => setEvaluations(r.evaluations.slice(0, 8))).catch(() => {});
  }, [selection?.domainId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const activeTemplate = templates.find((t) => t.id === selectedTemplate);

  const runTemplate = async () => {
    if (!selection) return;
    setLoading(true);
    setError(null);
    const body = {
      domain: selection.domainId,
      subdomain: selection.subdomainId,
      model: selection.modelId,
      inputs: paramValues,
    };
    try {
      let res: Record<string, unknown>;
      if (selectedTemplate === "generate_only") {
        res = await platformGenerate(body);
      } else if (selectedTemplate === "inference_only") {
        const inf = await platformMLInference(body);
        res = { inference_id: inf.inference_id, outputs: inf.outputs };
      } else {
        res = await platformMLOpsPipeline(body);
      }
      setLastJob(res);
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Pipeline failed");
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
          <Workflow className="h-4 w-4" style={{ color: accentColor }} />
          MLOps control plane
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {templates.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setSelectedTemplate(t.id)}
              className={`rounded-xl border p-4 text-left transition ${
                selectedTemplate === t.id
                  ? "border-sky-500/40 bg-sky-500/10"
                  : "border-white/10 hover:bg-white/5"
              }`}
            >
              <p className="text-sm font-medium text-zinc-200">{t.label}</p>
              <p className="mt-1 text-xs text-zinc-600">{t.description}</p>
              <p className="mt-2 font-mono text-[10px] text-zinc-700">{t.endpoint}</p>
            </button>
          ))}
        </div>
        {activeTemplate && (
          <p className="mt-3 text-xs text-zinc-600">
            Expected outputs: {activeTemplate.expected_outputs.join(", ")}
          </p>
        )}
        <div className="mt-4">
          <CatalogSelectors
            catalog={catalog}
            selection={selection}
            onSelectionChange={setSelection}
            lockDomain={domainId}
          />
        </div>
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
          onClick={runTemplate}
          disabled={loading}
          className="mt-4 inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black"
          style={{ backgroundColor: accentColor }}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run {activeTemplate?.label ?? "pipeline"}
        </button>
        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      </section>

      <div className="grid gap-3 sm:grid-cols-4">
        <Stat label="Synthetic" value={stats.synthetic_datasets ?? 0} />
        <Stat label="Artifacts" value={stats.artifacts ?? 0} />
        <Stat label="Evaluations" value={stats.evaluations ?? 0} />
        <Stat label="Inferences" value={stats.inferences ?? 0} />
      </div>

      {lastJob && (
        <pre className="glass overflow-x-auto rounded-2xl p-4 text-xs text-zinc-500">
          {JSON.stringify(lastJob, null, 2)}
        </pre>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
      <p className="text-xs text-zinc-600">{label}</p>
      <p className="text-xl font-semibold text-white">{value}</p>
    </div>
  );
}
