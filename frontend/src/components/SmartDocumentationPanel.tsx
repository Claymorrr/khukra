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
  methodCore: string[];
  researchQuestions: string[];
  optimizationLens: string;
}> = {
  physical: {
    intent: "Physics solver workspace for mechanics, thermofluid, and dynamics models with equations, state variables, traces, and validation metrics.",
    methodCore: ["governing equations", "state variables", "numerical status", "parameter sweeps", "solver traces"],
    researchQuestions: [
      "Which parameters dominate the output response?",
      "Does the numerical solution satisfy expected steady-state or conservation behavior?",
      "Which solver traces are good candidates for surrogate training?",
    ],
    optimizationLens: "Optimize physical parameters, stability margins, steady-state behavior, and solver-to-surrogate error.",
  },
  finance: {
    intent: "Automated trading R&D product: market research, signal development, backtest gates, execution simulation, portfolio risk, and paper-delivery readiness.",
    methodCore: [
      "market scenarios",
      "signal decay",
      "backtest Sharpe gates",
      "execution slippage sim",
      "paper delivery gates",
    ],
    researchQuestions: [
      "Which market regimes support deployable liquidity?",
      "Do signals pass backtest Sharpe and drawdown gates?",
      "Does paper execution simulation meet slippage and fill targets?",
      "Is the strategy release candidate ready for paper trading?",
    ],
    optimizationLens: "Optimize research throughput, validation gates, execution quality, risk limits, and paper-release readiness.",
  },
  supply_chain: {
    intent: "Product-quality and global-disruption simulation for defect drift, regional shock cascades, supplier contagion, and recovery planning.",
    methodCore: [
      "quality drift and Cpk",
      "regional correlated shocks",
      "Hawkes disruption cascades",
      "supplier contagion",
      "buffer and recovery trajectories",
    ],
    researchQuestions: [
      "Which process drift and inspection gaps drive defect escape and warranty exposure?",
      "How do geopolitical, weather, and logistics shocks combine into global risk?",
      "What buffer and alternate-supplier policies minimize recovery time and service-level risk?",
    ],
    optimizationLens: "Optimize inspection cadence, supplier substitution, buffer days, expedite capacity, and disruption response playbooks.",
  },
  intelligence: {
    intent: "Intelligence computational modeling systems for stochastic signal fusion, influence diffusion, and adversarial warning.",
    methodCore: ["Bayesian belief state", "Hawkes cascades", "regime switching", "jump anomalies"],
    researchQuestions: [
      "Which source mix raises confidence before false alarms rise?",
      "How does narrative diffusion accelerate after trigger events?",
      "What anomaly signatures indicate adversarial preparation?",
    ],
    optimizationLens: "Optimize collection allocation, alert thresholds, fusion weights, and response prioritization.",
  },
  computing: {
    intent: "Computing computational modeling systems for reliability, accelerator workloads, and edge cyber-physical behavior.",
    methodCore: ["queueing load", "stochastic volatility", "compound incidents", "latent belief states"],
    researchQuestions: [
      "When does latency saturation become an incident?",
      "How do accelerator workloads degrade under memory pressure?",
      "Which edge bottlenecks threaten autonomy under sensor bursts?",
    ],
    optimizationLens: "Optimize scheduling, autoscaling, workload placement, latency budgets, and reliability reserves.",
  },
};

const DEFAULT_PIPELINE_STEPS = [
  ["Synthetic scenario", "Mathematical stochastic process generates reproducible observations."],
  ["Data contract", "Schema and quality checks profile the synthetic dataset."],
  ["Forecast inference", "The model estimates point forecasts and uncertainty intervals."],
  ["Registry event", "Predictions can be promoted into artifact/evaluation records."],
  ["Lineage graph", "Scenario, dataset, inference, artifact, and evaluation IDs stay linked."],
];

const PHYSICAL_PIPELINE_STEPS = [
  ["Solver parameters", "Inputs define physical quantities, units, and boundary or initial conditions."],
  ["Equation run", "The registered solver evaluates analytic or numerical governing equations."],
  ["Scientific metrics", "Outputs summarize extrema, steady state, energy, stability, and numerical status."],
  ["Simulation traces", "Time or spatial series become sweep evidence and surrogate training data."],
  ["Lineage graph", "Solver run, metrics, traces, and artifacts stay linked for reproducible science."],
];

type SolverSpecMetadata = {
  title?: string;
  model_kind?: string;
  governing_equations?: string;
  assumptions?: string[];
  parameters?: Array<{ name: string; unit?: string; description?: string }>;
  state_variables?: Array<{ name: string; unit?: string; role?: string; description?: string }>;
  outputs?: Array<{ name: string; unit?: string; label?: string; description?: string }>;
  equations?: Array<{
    name: string;
    form: string;
    variables?: string[];
    parameters?: string[];
    equation_type?: string;
    residual?: string | null;
    description?: string;
  }>;
};

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
  const solverSpec =
    (metadata.solver_spec as SolverSpecMetadata | undefined) ??
    (model?.solver_spec as SolverSpecMetadata | undefined);
  const isPhysical = selection.domainId === "physical";
  const pipelineSteps = isPhysical ? PHYSICAL_PIPELINE_STEPS : DEFAULT_PIPELINE_STEPS;

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
              label={isPhysical ? "Model kind" : "Scenario"}
              value={
                isPhysical
                  ? solverSpec?.model_kind?.replace(/_/g, " ") ?? model?.model_kind?.replace(/_/g, " ") ?? "solver"
                  : metadata.scenario_id != null ? String(metadata.scenario_id) : "Generated at inference time"
              }
            />
          </div>
          <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">How to read it</p>
            <p className="mt-2 text-sm leading-6 text-zinc-400">
              {isPhysical
                ? "Inputs are physical parameters with units. A solver run returns scalar scientific metrics, simulation traces, governing-equation metadata, and numerical status. Use sweeps to test parameter sensitivity and build surrogate-ready datasets."
                : "Inputs control the stochastic data-generating process. Inference produces forecast error metrics, a final forecast level, trend slope, a forecast trace, and uncertainty bands. Use sweeps to test sensitivity and MLOps to create lineage-backed artifacts."}
            </p>
          </div>
          {solverSpec?.governing_equations && (
            <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Governing equations</p>
              <p className="mt-2 font-mono text-xs leading-6 text-zinc-300">{solverSpec.governing_equations}</p>
            </div>
          )}
          {solverSpec?.equations?.length ? (
            <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Structured equation specs</p>
              <div className="mt-3 space-y-3">
                {solverSpec.equations.map((equation) => (
                  <div key={equation.name} className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-medium text-zinc-200">{equation.name.replace(/_/g, " ")}</p>
                      <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-wide text-zinc-500">
                        {equation.equation_type ?? "equation"}
                      </span>
                    </div>
                    <p className="mt-2 font-mono text-xs leading-6 text-zinc-300">{equation.form}</p>
                    {equation.residual ? (
                      <p className="mt-1 font-mono text-[11px] leading-5 text-zinc-500">residual: {equation.residual}</p>
                    ) : null}
                    {(equation.variables?.length || equation.parameters?.length) ? (
                      <p className="mt-2 text-[11px] leading-5 text-zinc-500">
                        {equation.variables?.length ? `variables: ${equation.variables.join(", ")}` : ""}
                        {equation.variables?.length && equation.parameters?.length ? " | " : ""}
                        {equation.parameters?.length ? `parameters: ${equation.parameters.join(", ")}` : ""}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </section>

        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<Network className="h-4 w-4" />} title={isPhysical ? "Scientific method stack" : "Stochastic process stack"} accentColor={accentColor} />
          <div className="mt-4 flex flex-wrap gap-2">
            {guide.methodCore.map((item) => (
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
        <SectionTitle icon={<Route className="h-4 w-4" />} title={isPhysical ? "Solver analytics flow" : "Synthetic-data MLOps flow"} accentColor={accentColor} />
        <div className="mt-5 grid gap-3 lg:grid-cols-5">
          {pipelineSteps.map(([title, text], index) => (
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
            <LineageAnchor label={isPhysical ? "Solver artifact" : "Synthetic dataset"} value={metadata.synthetic_dataset_id ?? metadata.artifact_role} />
            <LineageAnchor label={isPhysical ? "Solver run" : "Inference run"} value={result?.run_id} />
            <LineageAnchor label="Model version" value={result?.model_version} />
          </div>
        </section>
      </div>
      {solverSpec?.assumptions?.length ? (
        <section className="glass rounded-2xl p-6">
          <SectionTitle icon={<Database className="h-4 w-4" />} title="Solver assumptions" accentColor={accentColor} />
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {solverSpec.assumptions.map((assumption) => (
              <div key={assumption} className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-zinc-400">
                {assumption}
              </div>
            ))}
          </div>
        </section>
      ) : null}
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
