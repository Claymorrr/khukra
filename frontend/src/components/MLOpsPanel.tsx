"use client";

import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { BadgeCheck, Database, GitBranch, Loader2, PackageCheck, Play, Workflow } from "lucide-react";
import { getStats, listArtifacts, listEvaluations, runMLOpsPipeline } from "@/lib/api";
import type { Selection } from "@/lib/types";

interface MLOpsPanelProps {
  selection: Selection;
  accentColor: string;
  onPipelineComplete?: (inferenceId: string) => void;
}

export function MLOpsPanel({ selection, accentColor, onPipelineComplete }: MLOpsPanelProps) {
  const [stats, setStats] = useState<Record<string, number>>({});
  const [artifacts, setArtifacts] = useState<Array<Record<string, unknown>>>([]);
  const [evaluations, setEvaluations] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastJob, setLastJob] = useState<Record<string, unknown> | null>(null);

  const refresh = useCallback(() => {
    getStats().then(setStats).catch(() => {});
    listArtifacts(selection.domainId).then((r) => setArtifacts(r.artifacts)).catch(() => {});
    listEvaluations().then((r) => setEvaluations(r.evaluations.slice(0, 5))).catch(() => {});
  }, [selection.domainId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handlePipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runMLOpsPipeline({
        domain: selection.domainId,
        subdomain: selection.subdomainId,
        model: selection.modelId,
        inputs: {},
      });
      setLastJob(res);
      if (res.inference_id && onPipelineComplete) {
        onPipelineComplete(String(res.inference_id));
      }
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Pipeline failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-4">
        <StatCard label="Synthetic datasets" value={stats.synthetic_datasets ?? 0} />
        <StatCard label="Artifacts" value={stats.artifacts ?? 0} />
        <StatCard label="Evaluations" value={stats.evaluations ?? 0} />
        <StatCard label="Inferences" value={stats.inferences ?? 0} />
      </div>

      <div className="glass relative overflow-hidden rounded-3xl p-6">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-20 blur-3xl"
          style={{ backgroundColor: accentColor }}
        />
        <div className="relative">
        <h3 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
          <Workflow className="h-4 w-4" style={{ color: accentColor }} />
          End-to-end MLOps pipeline
        </h3>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-500">
          Launch a local-first research pipeline: generate a stochastic synthetic dataset, validate it,
          run inference, register an artifact, evaluate it, and persist lineage.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-5">
          <FlowStep icon={<Database className="h-4 w-4" />} title="Synthetic" />
          <FlowStep icon={<BadgeCheck className="h-4 w-4" />} title="Validate" />
          <FlowStep icon={<Play className="h-4 w-4" />} title="Infer" />
          <FlowStep icon={<PackageCheck className="h-4 w-4" />} title="Register" />
          <FlowStep icon={<GitBranch className="h-4 w-4" />} title="Lineage" />
        </div>
        <button
          type="button"
          onClick={handlePipeline}
          disabled={loading}
          className="mt-4 inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold text-black disabled:opacity-50"
          style={{ backgroundColor: accentColor }}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run pipeline
        </button>
        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        {lastJob && (
          <pre className="mt-4 overflow-x-auto rounded-2xl border border-white/10 bg-black/30 p-4 text-xs text-zinc-400">
            {JSON.stringify(lastJob, null, 2)}
          </pre>
        )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section>
          <h4 className="mb-2 text-xs font-medium uppercase text-zinc-500">Model registry</h4>
          <ul className="space-y-2">
            {artifacts.length === 0 && (
              <li className="text-sm text-zinc-600">No artifacts yet.</li>
            )}
            {artifacts.map((a) => (
              <li key={String(a.artifact_id)} className="glass rounded-lg px-3 py-2 text-sm">
                <span className="font-mono text-zinc-400">{String(a.model_id)}</span>
                <span className="ml-2 text-xs text-zinc-500">v{String(a.version)} · {String(a.stage)}</span>
              </li>
            ))}
          </ul>
        </section>
        <section>
          <h4 className="mb-2 text-xs font-medium uppercase text-zinc-500">Evaluations</h4>
          <ul className="space-y-2">
            {evaluations.map((e) => (
              <li key={String(e.evaluation_run_id)} className="glass rounded-lg px-3 py-2 text-sm">
                {String(e.benchmark_name)}
                <span
                  className={`ml-2 text-xs ${e.passed ? "text-emerald-400" : "text-amber-400"}`}
                >
                  {e.passed ? "PASS" : "REVIEW"}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

function FlowStep({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4 text-center">
      <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-zinc-300">
        {icon}
      </div>
      <p className="mt-3 text-xs font-medium text-zinc-400">{title}</p>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="glass rounded-2xl p-4">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 font-mono text-2xl font-semibold">{value}</p>
    </div>
  );
}
