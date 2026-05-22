"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Activity,
  BookOpen,
  ChevronRight,
  Gauge,
  GitBranch,
  History,
  Layers,
  Loader2,
  Play,
  Radio,
  SlidersHorizontal,
} from "lucide-react";
import { createInference, getCatalog, listRuns } from "@/lib/api";
import { zonePath } from "@/lib/api/v1";
import type { CatalogResponse, DomainInfo, RunResponse, RunSummary, Selection } from "@/lib/types";
import { ComparePanel } from "../ComparePanel";
import { DynamicParameterForm } from "../DynamicParameterForm";
import { ExportBar } from "../ExportBar";
import { ForecastChart } from "../ForecastChart";
import { PredictionsGrid } from "../PredictionsGrid";
import { ResearchRunSummary } from "../ResearchRunSummary";
import { RunHistory } from "../RunHistory";
import { SeriesChart } from "../SeriesChart";
import { SmartDocumentationPanel } from "../SmartDocumentationPanel";
import { SweepPanel } from "../SweepPanel";
import { AnalyticsWorkbench } from "../platform/AnalyticsWorkbench";
import { DataGenerationStudio } from "../platform/DataGenerationStudio";
import { PlatformMLOpsPanel } from "../platform/PlatformMLOpsPanel";

type CockpitView = "console" | "sweeps" | "compare" | "docs" | "data_plane" | "analytics" | "lifecycle";

const LIFECYCLE_STAGES = ["develop", "validate", "package", "operate"] as const;

const DOMAIN_VERBS: Record<string, string> = {
  physical: "Solve",
  finance: "Infer",
  supply_chain: "Simulate",
  intelligence: "Infer",
  computing: "Simulate",
};

const DOMAIN_TAGLINES: Record<string, string> = {
  physical:
    "Simulation-first cockpit: mechanics, thermofluid, and dynamics solvers with traces, sweeps, and surrogate-ready outputs.",
  finance:
    "Quant inference cockpit: market scenarios, signals, backtests, execution simulation, risk, and paper-trading gates.",
  supply_chain:
    "Resilience simulation cockpit: quality drift, disruption risk, and recovery policy workloads.",
  intelligence: "Fusion inference cockpit: signal fusion, influence diffusion, and warning simulations.",
  computing: "Reliability simulation cockpit: latency, throughput, and edge-degradation workloads.",
};

type SolverSpecView = {
  title?: string;
  model_kind?: string;
  governing_equations?: string;
  equations?: Array<{ name: string; form: string }>;
};

export interface DomainCockpitProps {
  domain: DomainInfo;
  accentColor: string;
  initialSubdomain?: string;
  initialModel?: string;
}

export function DomainCockpit({
  domain,
  accentColor,
  initialSubdomain,
  initialModel,
}: DomainCockpitProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const verb = DOMAIN_VERBS[domain.id] ?? "Run";
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string | number | boolean>>({});
  const [result, setResult] = useState<RunResponse | null>(null);
  const [history, setHistory] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bootError, setBootError] = useState<string | null>(null);
  const [view, setView] = useState<CockpitView>("console");
  const [lifecycleStage, setLifecycleStage] = useState<(typeof LIFECYCLE_STAGES)[number]>("develop");

  const subdomainFromUrl = searchParams.get("subdomain") ?? initialSubdomain;
  const modelFromUrl = searchParams.get("model") ?? initialModel;

  const syncUrl = useCallback(
    (sel: Selection) => {
      const params = new URLSearchParams();
      params.set("subdomain", sel.subdomainId);
      params.set("model", sel.modelId);
      router.replace(zonePath(domain.id, "workflows", Object.fromEntries(params)));
    },
    [domain.id, router]
  );

  useEffect(() => {
    getCatalog()
      .then((data) => {
        setCatalog(data);
        const d = data.domains.find((x) => x.id === domain.id) ?? domain;
        const sub = d.subdomains.find((s) => s.id === subdomainFromUrl) ?? d.subdomains[0];
        const model = sub?.models.find((m) => m.id === modelFromUrl) ?? sub?.models[0];
        if (sub && model) {
          setSelection({ domainId: d.id, subdomainId: sub.id, modelId: model.id });
        }
      })
      .catch((e) => setBootError(e instanceof Error ? e.message : "Failed to load catalog"));
    listRuns(domain.id).then(setHistory).catch(() => setHistory([]));
  }, [domain, subdomainFromUrl, modelFromUrl]);

  const ctx = useMemo(() => {
    if (!catalog || !selection) return null;
    const d = catalog.domains.find((x) => x.id === selection.domainId);
    const subdomain = d?.subdomains.find((s) => s.id === selection.subdomainId);
    const model = subdomain?.models.find((m) => m.id === selection.modelId);
    if (!d || !subdomain || !model) return null;
    return { domain: d, subdomain, model };
  }, [catalog, selection]);

  useEffect(() => {
    if (!ctx) return;
    const defaults: Record<string, string | number | boolean> = {};
    for (const p of ctx.model.parameters) {
      defaults[p.name] = p.default as string | number | boolean;
    }
    setParamValues(defaults);
  }, [ctx?.subdomain.id, ctx?.model.id]);

  const handleSelect = (sel: Selection) => {
    setSelection(sel);
    syncUrl(sel);
    setLifecycleStage("develop");
  };

  const handleRun = async () => {
    if (!selection || !ctx) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createInference({
        domain: selection.domainId,
        subdomain: selection.subdomainId,
        model: selection.modelId,
        inputs: paramValues,
      });
      setResult(res);
      setLifecycleStage("validate");
      setView("console");
      listRuns(domain.id).then(setHistory).catch(() => {});
    } catch (e) {
      setError(e instanceof Error ? e.message : `${verb} failed`);
    } finally {
      setLoading(false);
    }
  };

  if (bootError) {
    return (
      <div className="rounded-2xl border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
        {bootError}
      </div>
    );
  }

  if (!catalog || !selection || !ctx) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  const solverSpec = (ctx.model.solver_spec ?? {}) as SolverSpecView;
  const numericalStatus = result?.metadata?.numerical_status as
    | { integration_success?: boolean; n_steps?: number; notes?: string }
    | undefined;
  const workloadKind = ctx.model.model_kind?.replace(/_/g, " ") ?? "inference";

  const secondaryViews: Array<{ id: CockpitView; label: string }> = [
    { id: "console", label: "Console" },
    { id: "sweeps", label: "Sweeps" },
    { id: "compare", label: "Compare" },
    { id: "docs", label: domain.id === "physical" ? "Equations" : "Docs" },
    { id: "data_plane", label: "Data plane" },
    { id: "analytics", label: "Analytics" },
    { id: "lifecycle", label: "Lifecycle" },
  ];

  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col gap-4">
      {/* Cockpit header */}
      <header
        className="shrink-0 rounded-2xl border border-white/10 bg-gradient-to-r from-white/[0.05] to-transparent p-5"
        style={{ borderColor: `${accentColor}33` }}
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-zinc-600">
              <Radio className="h-3.5 w-3.5" style={{ color: accentColor }} />
              Domain cockpit
            </p>
            <h2 className="mt-1 text-xl font-semibold text-white">
              {solverSpec.title ?? ctx.model.label}
            </h2>
            <p className="mt-1 max-w-2xl text-sm text-zinc-500">
              {DOMAIN_TAGLINES[domain.id] ??
                "Operate inference and simulation workloads through develop → validate → package → operate."}
            </p>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {LIFECYCLE_STAGES.map((stage) => (
              <button
                key={stage}
                type="button"
                onClick={() => setLifecycleStage(stage)}
                className={`rounded-full px-3 py-1 text-[10px] uppercase tracking-wider transition ${
                  lifecycleStage === stage
                    ? "font-semibold text-black"
                    : "border border-white/10 text-zinc-500 hover:text-zinc-300"
                }`}
                style={
                  lifecycleStage === stage ? { backgroundColor: accentColor } : undefined
                }
              >
                {stage}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <CockpitBadge label={ctx.subdomain.label} />
          <CockpitBadge label={workloadKind} />
          <CockpitBadge label={ctx.model.predictor_type ?? "inference_runtime"} mono />
          {result && (
            <CockpitBadge
              label={`Run ${result.run_id.slice(0, 8)}`}
              mono
            />
          )}
        </div>
      </header>

      {/* View switcher */}
      <div className="flex flex-wrap gap-2">
        {secondaryViews.map((v) => (
          <button
            key={v.id}
            type="button"
            onClick={() => setView(v.id)}
            className={`rounded-lg px-3 py-1.5 text-xs transition ${
              view === v.id ? "font-medium text-black" : "text-zinc-500 hover:bg-white/5"
            }`}
            style={view === v.id ? { backgroundColor: accentColor } : undefined}
          >
            {v.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {view === "console" && (
        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[220px_1fr_260px] lg:grid-rows-[1fr_auto]">
          {/* Left: workload instruments */}
          <aside className="rounded-2xl border border-white/10 bg-black/40 p-3 lg:row-span-1">
            <p className="mb-2 flex items-center gap-2 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
              <Layers className="h-3.5 w-3.5" />
              Workloads
            </p>
            <nav className="max-h-[420px] space-y-1 overflow-y-auto pr-1">
              {ctx.domain.subdomains.map((sub) => (
                <div key={sub.id}>
                  <button
                    type="button"
                    onClick={() =>
                      handleSelect({
                        domainId: domain.id,
                        subdomainId: sub.id,
                        modelId: sub.models[0]?.id ?? "",
                      })
                    }
                    className="flex w-full items-center gap-1 rounded-lg px-2 py-1 text-left text-xs text-zinc-400 hover:bg-white/5"
                  >
                    <ChevronRight
                      className={`h-3 w-3 shrink-0 ${
                        selection.subdomainId === sub.id ? "rotate-90 text-white" : ""
                      }`}
                    />
                    {sub.label}
                  </button>
                  {selection.subdomainId === sub.id && (
                    <div className="ml-3 border-l border-white/10 pl-2">
                      {sub.models.map((m) => (
                        <button
                          key={m.id}
                          type="button"
                          onClick={() =>
                            handleSelect({
                              domainId: domain.id,
                              subdomainId: sub.id,
                              modelId: m.id,
                            })
                          }
                          className={`block w-full rounded px-2 py-1 text-left text-[11px] ${
                            selection.modelId === m.id
                              ? "font-medium text-white"
                              : "text-zinc-500 hover:text-zinc-300"
                          }`}
                          style={
                            selection.modelId === m.id
                              ? { backgroundColor: `${accentColor}22` }
                              : undefined
                          }
                        >
                          {m.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
          </aside>

          {/* Center: active console */}
          <section className="flex min-h-0 flex-col gap-4 overflow-y-auto rounded-2xl border border-white/10 bg-white/[0.02] p-4">
            <div className="grid gap-4 xl:grid-cols-2">
              <div className="space-y-3 rounded-xl border border-white/10 bg-black/25 p-4">
                <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
                  <SlidersHorizontal className="h-4 w-4" />
                  {lifecycleStage === "develop" ? "Develop — inputs & scenario" : `${lifecycleStage} — review`}
                </p>
                {lifecycleStage === "develop" ? (
                  <>
                    <DynamicParameterForm
                      parameters={ctx.model.parameters}
                      values={paramValues}
                      onChange={(name, value) =>
                        setParamValues((p) => ({ ...p, [name]: value }))
                      }
                      accentColor={accentColor}
                    />
                    <button
                      type="button"
                      onClick={handleRun}
                      disabled={loading}
                      className="inline-flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-black disabled:opacity-50"
                      style={{ backgroundColor: accentColor }}
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 fill-current" />
                      )}
                      {verb} workload
                    </button>
                  </>
                ) : (
                  <p className="text-sm text-zinc-500">
                    {result
                      ? `Latest inference run ready for ${lifecycleStage}. Open Lifecycle tab to package or operate.`
                      : `Run a simulation or inference in Develop to advance to ${lifecycleStage}.`}
                  </p>
                )}
              </div>
              <ReadinessPanel
                accentColor={accentColor}
                lifecycleStage={lifecycleStage}
                predictorType={ctx.model.predictor_type}
                solverSpec={solverSpec}
                hasResult={!!result}
              />
            </div>

            {result && (
              <div className="space-y-4 border-t border-white/10 pt-4">
                <ExportBar runId={result.run_id} runIds={[result.run_id]} accentColor={accentColor} />
                <ResearchRunSummary result={result} accentColor={accentColor} />
                {numericalStatus && (
                  <div className="rounded-xl border border-white/10 bg-black/25 p-3 text-sm text-zinc-400">
                    <Activity className="mb-1 inline h-4 w-4" style={{ color: accentColor }} />{" "}
                    {numericalStatus.integration_success ? "Integration OK" : "Integration failed"} ·{" "}
                    {numericalStatus.n_steps ?? 0} steps
                  </div>
                )}
                {result.predictions && Object.keys(result.predictions).length > 0 ? (
                  <PredictionsGrid predictions={result.predictions} accentColor={accentColor} />
                ) : (
                  <PredictionsGrid
                    predictions={Object.fromEntries(
                      Object.entries(result.metrics).map(([k, v]) => [k, { value: v }])
                    )}
                    accentColor={accentColor}
                  />
                )}
                {result.series.forecast && result.series.observed ? (
                  <ForecastChart series={result.series} accentColor={accentColor} />
                ) : (
                  Object.keys(result.series).length > 0 && (
                    <SeriesChart series={result.series} accentColor={accentColor} />
                  )
                )}
              </div>
            )}
            {!result && lifecycleStage === "develop" && (
              <p className="text-sm text-zinc-600">
                Configure inputs and execute the selected inference or simulation workload.
              </p>
            )}
          </section>

          {/* Right: readiness rail */}
          <aside className="hidden rounded-2xl border border-white/10 bg-black/40 p-4 lg:block">
            <p className="mb-3 flex items-center gap-2 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
              <Gauge className="h-3.5 w-3.5" style={{ color: accentColor }} />
              Readiness
            </p>
            <ReadinessPanel
              accentColor={accentColor}
              lifecycleStage={lifecycleStage}
              predictorType={ctx.model.predictor_type}
              solverSpec={solverSpec}
              hasResult={!!result}
              compact
            />
          </aside>

          {/* Bottom: operating timeline */}
          <section className="rounded-2xl border border-white/10 bg-black/30 p-4 lg:col-span-3">
            <p className="mb-3 flex items-center gap-2 text-[10px] font-medium uppercase tracking-wider text-zinc-600">
              <History className="h-3.5 w-3.5" />
              Operating timeline
            </p>
            <RunHistory
              runs={history.slice(0, 8)}
              accentColor={accentColor}
              activeRunId={result?.run_id}
            />
          </section>
        </div>
      )}

      {view === "sweeps" && (
        <SweepPanel
          selection={selection}
          accentColor={accentColor}
          onComplete={() => {
            listRuns(domain.id).then(setHistory).catch(() => {});
            setView("console");
          }}
        />
      )}

      {view === "compare" && (
        <ComparePanel history={history} accentColor={accentColor} />
      )}

      {view === "docs" && (
        <SmartDocumentationPanel
          catalog={catalog}
          selection={selection}
          result={result}
          accentColor={accentColor}
        />
      )}

      {view === "data_plane" && (
        <DataGenerationStudio accentColor={accentColor} domainId={domain.id} />
      )}

      {view === "analytics" && (
        <AnalyticsWorkbench accentColor={accentColor} domainId={domain.id} />
      )}

      {view === "lifecycle" && (
        <PlatformMLOpsPanel accentColor={accentColor} domainId={domain.id} />
      )}
    </div>
  );
}

function CockpitBadge({ label, mono }: { label: string; mono?: boolean }) {
  return (
    <span
      className={`rounded-full border border-white/10 bg-black/30 px-2.5 py-1 text-xs text-zinc-400 ${
        mono ? "font-mono text-[10px]" : ""
      }`}
    >
      {label}
    </span>
  );
}

function ReadinessPanel({
  accentColor,
  lifecycleStage,
  predictorType,
  solverSpec,
  hasResult,
  compact,
}: {
  accentColor: string;
  lifecycleStage: string;
  predictorType?: string;
  solverSpec: SolverSpecView;
  hasResult: boolean;
  compact?: boolean;
}) {
  const gates = [
    { id: "develop", label: "Inputs configured", ok: true },
    { id: "validate", label: "Inference / simulation complete", ok: hasResult },
    { id: "package", label: "Validation gates passed", ok: false },
    { id: "operate", label: "Candidate packaged", ok: false },
  ];

  return (
    <div className={`space-y-3 ${compact ? "" : "rounded-xl border border-white/10 bg-white/[0.03] p-4"}`}>
      {!compact && (
        <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
          <GitBranch className="h-4 w-4" style={{ color: accentColor }} />
          Inference contract
        </p>
      )}
      <div className="rounded-lg border border-white/10 bg-black/25 p-3">
        <p className="text-[10px] uppercase text-zinc-600">Runtime</p>
        <p className="mt-1 font-mono text-xs text-zinc-300">{predictorType ?? "inference_runtime"}</p>
      </div>
      <div className="space-y-1.5">
        {gates.map((g) => (
          <div
            key={g.id}
            className={`flex items-center justify-between rounded-lg px-2 py-1.5 text-xs ${
              lifecycleStage === g.id ? "bg-white/[0.06]" : ""
            }`}
          >
            <span className={g.ok ? "text-zinc-300" : "text-zinc-600"}>{g.label}</span>
            <span
              className={`h-2 w-2 rounded-full ${
                g.ok ? "bg-emerald-500" : "bg-zinc-700"
              }`}
            />
          </div>
        ))}
      </div>
      {solverSpec.governing_equations && !compact && (
        <p className="font-mono text-[10px] leading-5 text-zinc-500">{solverSpec.governing_equations}</p>
      )}
    </div>
  );
}
