"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Loader2, Server, GitBranch } from "lucide-react";
import { getPlatformOpsSummary, type OpsSummary } from "@/lib/api";

interface OpsReadinessPanelProps {
  accentColor: string;
  domainId: string;
  mode: "infraops" | "devops";
}

export function InfraOpsPanel(props: Omit<OpsReadinessPanelProps, "mode">) {
  return <OpsReadinessPanel {...props} mode="infraops" />;
}

export function DevOpsPanel(props: Omit<OpsReadinessPanelProps, "mode">) {
  return <OpsReadinessPanel {...props} mode="devops" />;
}

function OpsReadinessPanel({ accentColor, domainId, mode }: OpsReadinessPanelProps) {
  const [summary, setSummary] = useState<OpsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getPlatformOpsSummary(domainId)
      .then((data) => {
        setSummary(data);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load ops summary"))
      .finally(() => setLoading(false));
  }, [domainId]);

  const active = useMemo(
    () => summary?.readiness.find((item) => item.id === mode),
    [mode, summary]
  );
  const Icon = mode === "infraops" ? Server : GitBranch;

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  if (error || !summary || !active) {
    return <p className="text-sm text-red-400">{error ?? "Ops summary unavailable."}</p>;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-zinc-500">
          <Icon className="h-4 w-4" style={{ color: accentColor }} />
          {active.label} readiness
        </p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h3 className="text-3xl font-semibold text-white">{active.score}%</h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">{active.description}</p>
          </div>
          <StatusBadge status={active.status} accentColor={accentColor} />
        </div>
      </section>

      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {Object.entries(summary.signals).map(([key, value]) => (
          <Stat key={key} label={key.replaceAll("_", " ")} value={value} />
        ))}
      </div>

      <section className="rounded-2xl border border-white/10 bg-black/20 p-5">
        <h4 className="text-sm font-medium text-zinc-300">Readiness Checks</h4>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {active.checks.map((check) => (
            <div key={check.label} className="flex items-center gap-2 rounded-xl border border-white/10 p-3">
              <CheckCircle2
                className="h-4 w-4"
                style={{ color: check.passed ? accentColor : "#71717a" }}
              />
              <span className={check.passed ? "text-sm text-zinc-300" : "text-sm text-zinc-600"}>
                {check.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <h4 className="text-sm font-medium text-zinc-300">Release Gate</h4>
          <dl className="mt-4 space-y-2 text-sm">
            {Object.entries(summary.release).map(([key, value]) => (
              <div key={key} className="flex justify-between gap-4">
                <dt className="capitalize text-zinc-600">{key.replaceAll("_", " ")}</dt>
                <dd className="text-right font-mono text-xs text-zinc-300">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <h4 className="text-sm font-medium text-zinc-300">Recent Jobs</h4>
          {summary.recent_jobs.length ? (
            <div className="mt-4 space-y-2">
              {summary.recent_jobs.slice(0, 4).map((job) => (
                <div key={String(job.job_id)} className="rounded-xl border border-white/10 p-3">
                  <p className="text-sm text-zinc-300">{String(job.job_type)}</p>
                  <p className="mt-1 text-xs text-zinc-600">{String(job.status)}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-zinc-600">No recent jobs for this domain yet.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function StatusBadge({ status, accentColor }: { status: string; accentColor: string }) {
  return (
    <span
      className="rounded-full border px-3 py-1.5 text-xs font-medium uppercase tracking-wide text-zinc-300"
      style={{ borderColor: `${accentColor}55` }}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
      <p className="text-xs capitalize text-zinc-600">{label}</p>
      <p className="text-xl font-semibold text-white">{value}</p>
    </div>
  );
}
