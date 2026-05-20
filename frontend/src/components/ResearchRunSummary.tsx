"use client";

import type React from "react";
import { Activity, Clock3, Database, GitBranch, Sparkles } from "lucide-react";
import type { RunResponse } from "@/lib/types";

interface ResearchRunSummaryProps {
  result: RunResponse;
  accentColor: string;
}

export function ResearchRunSummary({ result, accentColor }: ResearchRunSummaryProps) {
  const bestMetric = Object.entries(result.metrics).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))[0];
  const datasetId = result.metadata?.synthetic_dataset_id;
  const scenarioId = result.metadata?.scenario_id;

  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.02] p-6 shadow-glow">
      <div
        className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-25 blur-3xl"
        style={{ backgroundColor: accentColor }}
      />
      <div className="relative grid gap-6 lg:grid-cols-[1fr_360px]">
        <div>
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            <Sparkles className="h-4 w-4" style={{ color: accentColor }} />
            Inference dossier
          </p>
          <h3 className="mt-3 text-2xl font-semibold tracking-tight text-white">
            {result.model_name.replace(/_/g, " ")}
          </h3>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-zinc-400">
            {result.explanation ||
              "Forecast inference completed with synthetic scenario generation and persisted prediction evidence."}
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <Badge icon={<Activity className="h-3.5 w-3.5" />} label={result.predictor_type?.replace(/_/g, " ") ?? "stochastic predictor"} />
            <Badge icon={<Clock3 className="h-3.5 w-3.5" />} label={`${result.latency_ms ?? 0} ms`} />
            <Badge icon={<Database className="h-3.5 w-3.5" />} label={datasetId != null ? String(datasetId) : "dataset pending"} />
            <Badge icon={<GitBranch className="h-3.5 w-3.5" />} label={scenarioId != null ? String(scenarioId) : "scenario pending"} />
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-black/25 p-5">
          <p className="text-xs uppercase tracking-wide text-zinc-600">Decision signal</p>
          <p className="mt-3 text-sm text-zinc-400">
            Primary output magnitude
          </p>
          <p className="mt-2 font-mono text-3xl font-semibold tabular-nums" style={{ color: accentColor }}>
            {bestMetric ? formatMetric(bestMetric[1]) : "n/a"}
          </p>
          <p className="mt-2 truncate text-xs text-zinc-500">
            {bestMetric?.[0].replace(/_/g, " ") ?? "no metric"}
          </p>
        </div>
      </div>
    </section>
  );
}

function Badge({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-black/25 px-3 py-1.5 text-xs text-zinc-400">
      {icon}
      {label}
    </span>
  );
}

function formatMetric(value: number): string {
  if (Math.abs(value) >= 1e6) return value.toExponential(2);
  if (Math.abs(value) < 0.01 && value !== 0) return value.toExponential(3);
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}
