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
  const manifest = domain.manifest;

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
        <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">
          {manifest.tagline || "Domain operating environment"}
        </p>
        <h3 className="mt-3 text-3xl font-semibold tracking-tight text-white">{domain.label}</h3>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-zinc-500">
          {manifest.positioning ||
            "Domain-specific inference, data operations, MLOps, analytics, and insight workflows."}
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <Stat label="Subdomains" value={String(domain.subdomains.length)} />
          <Stat label="Models" value={String(modelCount)} />
          <Stat label="Inferences" value={String(totalRuns)} />
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <ManifestList title="Focus" items={manifest.primary_focus} accentColor={accentColor} />
        <ManifestList title="Model Families" items={manifest.model_families} accentColor={accentColor} />
        <ManifestList title="Data Products" items={manifest.data_products} accentColor={accentColor} />
      </div>

      {manifest.ops_capabilities.length > 0 && (
        <section className="rounded-2xl border border-white/10 bg-black/20 p-5">
          <h4 className="text-sm font-medium text-zinc-300">Ops Layer</h4>
          <div className="mt-4 flex flex-wrap gap-2">
            {manifest.ops_capabilities.map((item) => (
              <span
                key={item}
                className="rounded-full border border-white/10 px-3 py-1.5 text-xs text-zinc-400"
                style={{ borderColor: `${accentColor}44` }}
              >
                {item}
              </span>
            ))}
          </div>
        </section>
      )}

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
        <h4 className="text-sm font-medium text-zinc-300">Roadmap</h4>
        <ol className="mt-4 space-y-2 text-sm text-zinc-500">
          {(manifest.roadmap.length ? manifest.roadmap : QUICK_MODULES).map((item, i) => {
            if (typeof item === "string" && QUICK_MODULES.includes(item as DomainModule)) {
              const id = item as DomainModule;
              const label = DOMAIN_MODULES.find((m) => m.id === id)?.label ?? id;
              return (
                <li key={id}>
                  {i + 1}. Open{" "}
                  <button
                    type="button"
                    onClick={() => onNavigate(id)}
                    className="text-zinc-200 hover:underline"
                  >
                    {label}
                  </button>
                </li>
              );
            }
            return <li key={`${item}-${i}`}>{i + 1}. {item}</li>;
          })}
        </ol>
      </section>
    </div>
  );
}

function ManifestList({
  title,
  items,
  accentColor,
}: {
  title: string;
  items: string[];
  accentColor: string;
}) {
  if (!items.length) return null;
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <h4 className="text-sm font-medium text-zinc-300">{title}</h4>
      <div className="mt-4 space-y-2">
        {items.map((item) => (
          <div key={item} className="flex gap-2 text-sm text-zinc-500">
            <span
              className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full"
              style={{ backgroundColor: accentColor }}
            />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </section>
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
