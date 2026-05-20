"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import { getPlatformManifest, getPlatformSummary, type PlatformSummary } from "@/lib/api";
import type { PlatformModule } from "./PlatformShell";

interface PlatformOverviewProps {
  accentColor: string;
  onNavigate: (module: PlatformModule) => void;
}

export function PlatformOverview({ accentColor, onNavigate }: PlatformOverviewProps) {
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getPlatformSummary(), getPlatformManifest().catch(() => null)])
      .then(([s]) => setSummary(s))
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-sky-500/10 to-transparent p-8">
        <h3 className="text-2xl font-semibold text-white">
          {summary?.headline ?? "Platform health snapshot"}
        </h3>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
          Separate workspace for synthetic data generation, MLOps orchestration, ML
          inferencing, DuckDB analytics, and insights engineering — without the research model UI.
        </p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(summary?.cards ?? []).map((card) => (
          <div
            key={card.title}
            className="glass rounded-2xl border border-white/10 p-5"
          >
            <p className="text-xs uppercase tracking-wider text-zinc-500">{card.title}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
            <p className="mt-2 text-xs leading-5 text-zinc-600">{card.detail}</p>
          </div>
        ))}
      </div>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(summary?.modules ?? []).map((mod) => (
          <button
            key={mod.id}
            type="button"
            onClick={() => onNavigate(mod.id as PlatformModule)}
            className="group flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-left transition hover:border-sky-500/30 hover:bg-sky-500/5"
          >
            <div>
              <p className="font-medium text-zinc-200">{mod.label}</p>
              <p className="mt-1 text-xs capitalize text-zinc-600">{mod.status}</p>
            </div>
            <ArrowRight
              className="h-4 w-4 text-zinc-600 transition group-hover:text-sky-400"
              style={{ color: accentColor }}
            />
          </button>
        ))}
      </section>
    </div>
  );
}
