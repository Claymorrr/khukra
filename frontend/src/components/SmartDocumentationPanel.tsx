"use client";

import type React from "react";
import {
  BookOpen,
  Brain,
  Database,
  GitBranch,
  Network,
  Route,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { CatalogResponse, RunResponse, Selection } from "@/lib/types";

interface SmartDocumentationPanelProps {
  catalog: CatalogResponse;
  selection: Selection;
  result: RunResponse | null;
  accentColor: string;
}

const DOMAIN_GUIDES: Record<string, {
  intent: string;
  stochasticCore: string[];
  researchQuestions: string[];
  optimizationLens: string;
}> = {
  physical: {
    intent: "Propulsion-system computational modeling for degradation, combustion instability, and hybrid mission control.",
    stochasticCore: ["jump diffusion", "compound shocks", "regime switching", "stochastic volatility"],
    researchQuestions: [
      "Which operating regimes create maintenance risk?",
      "How early can instability be forecast before threshold breach?",
      "What control policy preserves thrust while protecting thermal margin?",
    ],
    optimizationLens: "Optimize operating envelopes, power split, inspection timing, and robustness under rare shocks.",
  },
  finance: {
    intent: "Quantitative research environment for stochastic signals, market microstructure, stat-arb spreads, and execution risk.",
    stochasticCore: ["Hawkes arrivals", "stochastic volatility", "mean reversion", "jump shocks"],
    researchQuestions: [
      "How persistent is liquidity under self-exciting order flow?",
      "Which spread regimes are exploitable after costs?",
      "What execution schedule minimizes tail slippage?",
    ],
    optimizationLens: "Optimize signal weighting, risk budgets, execution participation, and stress-aware allocation.",
  },
  supply_chain: {
    intent: "Product-quality and global-disruption modeling for defect drift, shock propagation, and recovery planning.",
    stochasticCore: ["compound Poisson disruptions", "Hawkes event cascades", "quality drift", "shock processes"],
    researchQuestions: [
      "Which process drift predicts defect acceleration?",
      "How do correlated disruptions propagate through suppliers?",
      "What buffers reduce recovery time under severe scenarios?",
    ],
    optimizationLens: "Optimize buffers, supplier substitution, inspection cadence, and disruption response policies.",
  },
  intelligence: {
    intent: "Intelligence computational modeling systems for stochastic signal fusion, influence diffusion, and adversarial warning.",
    stochasticCore: ["Bayesian belief state", "Hawkes cascades", "regime switching", "jump anomalies"],
    researchQuestions: [
      "Which source mix raises confidence before false alarms rise?",
      "How does narrative diffusion accelerate after trigger events?",
      "What anomaly signatures indicate adversarial preparation?",
    ],
    optimizationLens: "Optimize collection allocation, alert thresholds, fusion weights, and response prioritization.",
  },
  computing: {
    intent: "Computing computational modeling systems for reliability, accelerator workloads, and edge cyber-physical behavior.",
    stochasticCore: ["queueing load", "stochastic volatility", "compound incidents", "latent belief states"],
    researchQuestions: [
      "When does latency saturation become an incident?",
      "How do accelerator workloads degrade under memory pressure?",
      "Which edge bottlenecks threaten autonomy under sensor bursts?",
    ],
    optimizationLens: "Optimize scheduling, autoscaling, workload placement, latency budgets, and reliability reserves.",
  },
};

const PIPELINE_STEPS = [
  ["Synthetic scenario", "Mathematical stochastic process generates reproducible observations."],
  ["Data contract", "Schema and quality checks profile the synthetic dataset."],
  ["Forecast inference", "The model estimates point forecasts and uncertainty intervals."],
  ["Registry event", "Predictions can be promoted into artifact/evaluation records."],
  ["Lineage graph", "Scenario, dataset, inference, artifact, and evaluation IDs stay linked."],
];

export function SmartDocumentationPanel({
  catalog,
  selection,
  result,
  accentColor,
}: SmartDocumentationPanelProps) {
  const domain = catalog.domains.find((d) => d.id === selection.domainId);
  const subdomain = domain?.subdomains.find((s) => s.id === selection.subdomainId);
  const model = subdomain?.models.find((m) => m.id === selection.modelId);
  const guide = DOMAIN_GUIDES[selection.domainId] ?? DOMAIN_GUIDES.physical;
  const metadata = result?.metadata ?? {};

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.035] p-7">
        <div
          className="pointer-events-none absolute inset-y-0 right-0 w-1/2 opacity-30 blur-3xl"
          style={{ background: `radial-gradient(circle at 50% 20%, ${accentColor}, transparent 55%)` }}
        />
        <div className="relative">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            <BookOpen className="h-4 w-4" style={{ color: accentColor }} />
            Smart research documentation
          </p>
          <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight text-white">
            {domain?.label ?? "Research domain"} knowledge card
          </h2>
          <p className="mt-3 max-w-4xl text-sm leading-7 text-zinc-400">{guide.intent}</p>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<Brain className="h-4 w-4" />} title="Selected model brief" accentColor={accentColor} />
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <InfoTile label="Subdomain" value={subdomain?.description ?? selection.subdomainId} />
            <InfoTile label="Model" value={model?.label ?? selection.modelId} />
            <InfoTile label="Parameters" value={`${model?.parameters.length ?? 0} configurable inputs`} />
            <InfoTile
              label="Scenario"
              value={metadata.scenario_id != null ? String(metadata.scenario_id) : "Generated at inference time"}
            />
          </div>
          <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">How to read it</p>
            <p className="mt-2 text-sm leading-6 text-zinc-400">
              Inputs control the stochastic data-generating process. Inference produces forecast error metrics,
              a final forecast level, trend slope, a forecast trace, and uncertainty bands. Use sweeps to test
              sensitivity and MLOps to create lineage-backed artifacts.
            </p>
          </div>
        </section>

        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<Network className="h-4 w-4" />} title="Stochastic process stack" accentColor={accentColor} />
          <div className="mt-4 flex flex-wrap gap-2">
            {guide.stochasticCore.map((item) => (
              <span
                key={item}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-zinc-300"
              >
                {item}
              </span>
            ))}
          </div>
          <div className="mt-5 space-y-3">
            {guide.researchQuestions.map((q) => (
              <div key={q} className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-zinc-400">
                {q}
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="glass rounded-2xl p-6">
        <SectionTitle icon={<Route className="h-4 w-4" />} title="Synthetic-data MLOps flow" accentColor={accentColor} />
        <div className="mt-5 grid gap-3 lg:grid-cols-5">
          {PIPELINE_STEPS.map(([title, text], index) => (
            <div key={title} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <div
                className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold text-black"
                style={{ backgroundColor: accentColor }}
              >
                {index + 1}
              </div>
              <p className="mt-4 text-sm font-semibold text-white">{title}</p>
              <p className="mt-2 text-xs leading-5 text-zinc-500">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<ShieldCheck className="h-4 w-4" />} title="Optimization orientation" accentColor={accentColor} />
          <p className="mt-3 text-sm leading-7 text-zinc-400">{guide.optimizationLens}</p>
        </section>
        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<GitBranch className="h-4 w-4" />} title="Current lineage anchors" accentColor={accentColor} />
          <div className="mt-4 grid gap-2 font-mono text-xs">
            <LineageAnchor label="Synthetic dataset" value={metadata.synthetic_dataset_id} />
            <LineageAnchor label="Inference run" value={result?.run_id} />
            <LineageAnchor label="Model version" value={result?.model_version} />
          </div>
        </section>
      </div>
    </div>
  );
}

function SectionTitle({
  icon,
  title,
  accentColor,
}: {
  icon: React.ReactNode;
  title: string;
  accentColor: string;
}) {
  return (
    <h3 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
      <span style={{ color: accentColor }}>{icon}</span>
      {title}
    </h3>
  );
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <p className="text-xs uppercase tracking-wide text-zinc-600">{label}</p>
      <p className="mt-2 text-sm leading-6 text-zinc-300">{value}</p>
    </div>
  );
}

function LineageAnchor({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-black/20 px-3 py-2">
      <span className="text-zinc-600">{label}</span>
      <span className="truncate text-zinc-300">{value != null ? String(value) : "pending"}</span>
    </div>
  );
}
