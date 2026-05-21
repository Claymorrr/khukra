"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import { getPlatformSummary, type PlatformSummary } from "@/lib/api";
import type { DomainInfo } from "@/lib/types";
import type { DomainModule } from "./types";
import { DOMAIN_MODULES } from "./types";

interface DomainOverviewProps {
  domain: DomainInfo;
  accentColor: string;
  totalRuns: number;
  onNavigate: (module: DomainModule) => void;
}

const QUICK_MODULES: DomainModule[] = [
  "inference",
  "data_generation",
  "mlops",
  "ml_inference",
  "analytics",
  "insights",
];

export function DomainOverview({
  domain,
  accentColor,
  totalRuns,
  onNavigate,
}: DomainOverviewProps) {
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPlatformSummary()
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  const modelCount = domain.subdomains.reduce((n, s) => n + s.models.length, 0);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section
        className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-transparent p-8"
        style={{ borderColor: `${accentColor}33` }}
      >
        <h3 className="text-2xl font-semibold text-white">{domain.label}</h3>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
          One domain workspace for stochastic modeling, inference, sweeps, data generation, MLOps,
          analytics, and insights — no separate research/platform split.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <Stat label="Subdomains" value={String(domain.subdomains.length)} />
          <Stat label="Models" value={String(modelCount)} />
          <Stat label="Inferences" value={String(totalRuns)} />
        </div>
      </section>

      {(summary?.cards ?? []).length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(summary?.cards ?? []).map((card) => (
            <div key={card.title} className="glass rounded-2xl border border-white/10 p-5">
              <p className="text-xs uppercase tracking-wider text-zinc-500">{card.title}</p>
              <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
              <p className="mt-2 text-xs leading-5 text-zinc-600">{card.detail}</p>
            </div>
          ))}
        </div>
      )}

      <section>
        <h4 className="mb-4 text-sm font-medium uppercase tracking-wide text-zinc-500">
          Capabilities
        </h4>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {DOMAIN_MODULES.filter((m) => m.id !== "overview").map((mod) => (
            <button
              key={mod.id}
              type="button"
              onClick={() => onNavigate(mod.id)}
              className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-white/20"
            >
              <span className="text-sm font-medium text-zinc-200">{mod.label}</span>
              <ArrowRight
                className="h-4 w-4 text-zinc-600 group-hover:text-white"
                style={{ color: accentColor }}
              />
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 p-6">
        <h4 className="text-sm font-medium text-zinc-300">Suggested flow</h4>
        <ol className="mt-4 space-y-2 text-sm text-zinc-500">
          {QUICK_MODULES.map((id, i) => {
            const label = DOMAIN_MODULES.find((m) => m.id === id)?.label ?? id;
            return (
              <li key={id}>
                {i + 1}. Open <button type="button" onClick={() => onNavigate(id)} className="text-zinc-200 hover:underline">{label}</button>
              </li>
            );
          })}
        </ol>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/25 px-4 py-4">
      <p className="text-xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-xs text-zinc-500">{label}</p>
    </div>
  );
}
