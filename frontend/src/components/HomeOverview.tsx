"use client";

import type React from "react";
import {
  ArrowRight,
  Box,
  Brain,
  Cpu,
  Database,
  GitBranch,
  LineChart,
  Loader2,
  Network,
  ShieldCheck,
  Truck,
  Zap,
} from "lucide-react";
import type { CatalogResponse, RunResponse, Selection } from "@/lib/types";

const DOMAIN_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

interface HomeOverviewProps {
  catalog: CatalogResponse;
  accentColor: string;
  totalRuns: number;
  onSelect: (s: Selection) => void;
  onRunDemo: () => Promise<void>;
  onOpenResults: (result: RunResponse) => void;
  demoLoading: boolean;
  lastDemo?: RunResponse | null;
}

export function HomeOverview({
  catalog,
  accentColor,
  totalRuns,
  onSelect,
  onRunDemo,
  onOpenResults,
  demoLoading,
  lastDemo,
}: HomeOverviewProps) {
  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.08] via-white/[0.03] to-transparent p-8 shadow-2xl shadow-black/30">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full opacity-25 blur-3xl"
          style={{ backgroundColor: accentColor }}
        />
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="max-w-2xl">
            <p className="text-xs font-medium uppercase tracking-[0.3em] text-zinc-500">
              Khukra research command center
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white">
              Stochastic computational modeling, inference, and optimization-ready evidence.
            </h2>
            <p className="mt-4 text-sm leading-7 text-zinc-400">
              Generate synthetic scenarios from mathematical processes, forecast uncertainty, register artifacts,
              inspect lineage, and prepare research decisions for optimization studies.
            </p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <Capability icon={<Network className="h-4 w-4" />} title="Stochastic DGPs" text="Jump diffusion, Hawkes, regime switching, queueing, and belief-state systems." />
              <Capability icon={<Database className="h-4 w-4" />} title="Queryable lakehouse" text="DuckDB + Parquet persistence, contracts, profiling, synthetic IDs, and in-app SQL." />
              <Capability icon={<GitBranch className="h-4 w-4" />} title="Traceable MLOps" text="Scenario → dataset → inference → artifact → evaluation lineage." />
              <Capability icon={<ShieldCheck className="h-4 w-4" />} title="Research governance" text="Versioned model metadata, evaluations, exports, and reproducible seeds." />
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <button
              type="button"
              onClick={onRunDemo}
              disabled={demoLoading}
              className="inline-flex items-center justify-center gap-2 rounded-2xl px-6 py-3 text-sm font-semibold text-black disabled:opacity-60"
              style={{ backgroundColor: accentColor }}
            >
              {demoLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Zap className="h-4 w-4" />
              )}
              Run stochastic demo
            </button>
            <p className="text-center text-xs text-zinc-600">
              {totalRuns} inferences in warehouse
            </p>
          </div>
        </div>

        <div className="relative mt-8 grid gap-4 sm:grid-cols-3">
          <QuickStat label="Domains" value={String(catalog.domains.length)} />
          <QuickStat
            label="Subdomains"
            value={String(
              catalog.domains.reduce((n, d) => n + d.subdomains.length, 0)
            )}
          />
          <QuickStat label="Inferences" value={String(totalRuns)} />
        </div>
      </section>

      {lastDemo && (
        <section className="rounded-2xl border border-sky-400/20 bg-sky-400/5 p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-sky-300/80">Latest demo</p>
              <p className="mt-1 text-lg font-medium text-white">
                {lastDemo.model_name.replace(/_/g, " ")} — {lastDemo.run_id}
              </p>
            </div>
            <button
              type="button"
              onClick={() => onOpenResults(lastDemo)}
              className="inline-flex items-center gap-2 text-sm text-sky-300 hover:text-sky-200"
            >
              View results <ArrowRight className="h-4 w-4" />
            </button>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            {Object.entries(lastDemo.metrics)
              .slice(0, 4)
              .map(([k, v]) => (
                <span
                  key={k}
                  className="rounded-lg bg-black/30 px-3 py-2 font-mono text-xs text-zinc-300"
                >
                  {k}: {v.toFixed(4)}
                </span>
              ))}
          </div>
        </section>
      )}

      <section>
        <h3 className="mb-4 text-sm font-medium uppercase tracking-wide text-zinc-500">
          Explore domains
        </h3>
        <div className="grid gap-4 lg:grid-cols-3">
          {catalog.domains.map((domain) => {
            const Icon = DOMAIN_ICONS[domain.id] ?? Box;
            const first = domain.subdomains[0];
            const model = first?.models[0];
            return (
              <button
                key={domain.id}
                type="button"
                onClick={() =>
                  model &&
                  onSelect({
                    domainId: domain.id,
                    subdomainId: first.id,
                    modelId: model.id,
                  })
                }
                className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-left transition hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.06] hover:shadow-glow"
              >
                <div
                  className="absolute inset-x-0 top-0 h-1 opacity-80"
                  style={{ backgroundColor: domain.color }}
                />
                <div
                  className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl"
                  style={{ backgroundColor: `${domain.color}22`, color: domain.color }}
                >
                  <Icon className="h-5 w-5" />
                </div>
                <h4 className="text-lg font-semibold text-white">{domain.label}</h4>
                <p className="mt-2 text-sm text-zinc-500">
                  {domain.subdomains.length} subdomains ·{" "}
                  {domain.subdomains.reduce((n, s) => n + s.models.length, 0)} models
                </p>
                <div className="mt-4 space-y-2">
                  {domain.subdomains.slice(0, 3).map((sub) => (
                    <div key={sub.id} className="rounded-xl bg-black/20 px-3 py-2">
                      <p className="truncate text-xs text-zinc-400">{sub.label}</p>
                    </div>
                  ))}
                </div>
                <p className="mt-4 flex items-center gap-1 text-xs font-medium text-zinc-400 group-hover:text-white">
                  Open {model?.label ?? "workspace"}
                  <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
                </p>
              </button>
            );
          })}
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 p-6">
        <h3 className="text-sm font-medium text-zinc-300">What to try first</h3>
        <ol className="mt-4 space-y-3 text-sm text-zinc-400">
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs text-white">1</span>
            Click <strong className="text-zinc-200">Run demo inference</strong> above to generate outputs and traces instantly.
          </li>
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs text-white">2</span>
            Open a domain card, tweak inputs, and press <strong className="text-zinc-200">Infer</strong>.
          </li>
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs text-white">3</span>
            Use tabs: <strong className="text-zinc-200">Sweeps</strong>, <strong className="text-zinc-200">Compare</strong>, <strong className="text-zinc-200">Data</strong>, <strong className="text-zinc-200">History</strong>.
          </li>
        </ol>
      </section>
    </div>
  );
}

function Capability({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold text-white">
        <span className="text-[var(--accent)]">{icon}</span>
        {title}
      </div>
      <p className="mt-2 text-xs leading-5 text-zinc-500">{text}</p>
    </div>
  );
}

function QuickStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/25 px-4 py-5">
      <p className="text-2xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-xs text-zinc-500">{label}</p>
    </div>
  );
}
