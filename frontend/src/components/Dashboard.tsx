"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ExternalLink, Loader2, LogOut, Play, Sparkles } from "lucide-react";
import { createInference, getCatalog, getStats, listRuns } from "@/lib/api";
import { HomeOverview } from "./HomeOverview";
import { useAuth } from "@/lib/auth";
import type { CatalogResponse, RunResponse, RunSummary, Selection } from "@/lib/types";
import { ComparePanel } from "./ComparePanel";
import { DatasetsPanel } from "./DatasetsPanel";
import { ExportBar } from "./ExportBar";
import { PredictionsGrid } from "./PredictionsGrid";
import { DynamicParameterForm } from "./DynamicParameterForm";
import { ResearchRunSummary } from "./ResearchRunSummary";
import { RunHistory } from "./RunHistory";
import { ForecastChart } from "./ForecastChart";
import { SeriesChart } from "./SeriesChart";
import { Sidebar } from "./Sidebar";
import { SmartDocumentationPanel } from "./SmartDocumentationPanel";
import { SweepPanel } from "./SweepPanel";

type Tab =
  | "overview"
  | "results"
  | "docs"
  | "sweeps"
  | "compare"
  | "data"
  | "history";

interface DashboardProps {
  onSwitchToPlatform?: () => void;
}

export function Dashboard({ onSwitchToPlatform }: DashboardProps) {
  const { user, logout, isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string | number | boolean>>({});
  const [result, setResult] = useState<RunResponse | null>(null);
  const [history, setHistory] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("overview");
  const [bootError, setBootError] = useState<string | null>(null);
  const [comparisonId, setComparisonId] = useState<string | null>(null);
  const [totalRuns, setTotalRuns] = useState(0);
  const [demoLoading, setDemoLoading] = useState(false);
  const [lastDemo, setLastDemo] = useState<RunResponse | null>(null);

  useEffect(() => {
    getCatalog()
      .then((data) => {
        setCatalog(data);
        const d = data.domains[0];
        const s = d.subdomains[0];
        const m = s.models[0];
        setSelection({ domainId: d.id, subdomainId: s.id, modelId: m.id });
      })
      .catch((e) => setBootError(e instanceof Error ? e.message : "Failed to load catalog"));
    getStats().then((s) => setTotalRuns(s.inferences ?? s.runs)).catch(() => {});
  }, []);

  const ctx = useMemo(() => {
    if (!catalog || !selection) return null;
    const domain = catalog.domains.find((d) => d.id === selection.domainId);
    const subdomain = domain?.subdomains.find((s) => s.id === selection.subdomainId);
    const model = subdomain?.models.find((m) => m.id === selection.modelId);
    if (!domain || !subdomain || !model) return null;
    return { domain, subdomain, model };
  }, [catalog, selection]);

  const refreshHistory = useCallback((domainId?: string) => {
    getStats().then((s) => setTotalRuns(s.inferences ?? s.runs)).catch(() => {});
    const d = domainId ?? selection?.domainId;
    if (!d) return;
    listRuns(d).then(setHistory).catch(() => setHistory([]));
  }, [selection?.domainId]);

  const handleDemoRun = useCallback(async () => {
    if (!catalog) return;
    setDemoLoading(true);
    setError(null);
    try {
      const physical = catalog.domains.find((d) => d.id === "physical");
      const model = physical?.subdomains.find((s) => s.id === "turbomachinery_degradation")?.models[0];
      if (!physical || !model) throw new Error("Demo model not found");

      const res = await createInference({
        domain: "physical",
        subdomain: "turbomachinery_degradation",
        model: model.id,
        inputs: {},
      });
      setResult(res);
      setLastDemo(res);
      setSelection({
        domainId: "physical",
        subdomainId: "turbomachinery_degradation",
        modelId: model.id,
      });
      setTab("results");
      refreshHistory("physical");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Demo run failed");
    } finally {
      setDemoLoading(false);
    }
  }, [catalog, refreshHistory]);

  useEffect(() => {
    if (!ctx) return;
    const defaults: Record<string, string | number | boolean> = {};
    for (const p of ctx.model.parameters) {
      defaults[p.name] = p.default as string | number | boolean;
    }
    setParamValues(defaults);
    setResult(null);
    refreshHistory();
  }, [ctx?.domain.id, ctx?.subdomain.id, ctx?.model.id, refreshHistory]);

  useEffect(() => {
    if (ctx?.domain.color) {
      document.documentElement.style.setProperty("--accent", ctx.domain.color);
      document.documentElement.style.setProperty("--accent-glow", `${ctx.domain.color}40`);
    }
  }, [ctx?.domain.color]);

  const handleRun = useCallback(async () => {
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
      setTab("results");
      refreshHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Inference failed");
    } finally {
      setLoading(false);
    }
  }, [selection, ctx, paramValues, refreshHistory]);

  if (bootError) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <div className="glass max-w-md rounded-xl p-8 text-center">
          <p className="text-red-400">Cannot connect to API</p>
          <p className="mt-2 text-sm text-zinc-500">{bootError}</p>
          <p className="mt-4 text-xs text-zinc-600">Start backend: khukra-api</p>
        </div>
      </div>
    );
  }

  if (!catalog || !selection || !ctx) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  const accent = ctx.domain.color;
  const tabs: Tab[] = ["overview", "results", "docs", "sweeps", "compare", "data", "history"];
  const modelInputs = ctx.model.parameters.length;
  const totalModels = catalog.domains.reduce(
    (n, d) => n + d.subdomains.reduce((m, s) => m + s.models.length, 0),
    0
  );

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar catalog={catalog} selection={selection} onSelect={setSelection} />

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="shrink-0 border-b border-border bg-surface-raised/80 px-8 py-5 backdrop-blur-xl">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
                {ctx.domain.label}
              </p>
              <h2 className="mt-1 truncate text-3xl font-semibold tracking-tight text-white">
                {ctx.model.label}
              </h2>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-zinc-500">
                {ctx.subdomain.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <HeaderPill label={`${modelInputs} inputs`} />
                <HeaderPill label={`${totalModels} research models`} />
                <HeaderPill label={result ? `last run ${result.run_id}` : "ready for inference"} />
              </div>
            </div>
            <div className="flex items-center gap-3">
              {onSwitchToPlatform && (
                <button
                  type="button"
                  onClick={onSwitchToPlatform}
                  className="inline-flex items-center gap-2 rounded-xl border border-sky-500/30 bg-sky-500/10 px-3 py-2 text-xs text-sky-300 hover:bg-sky-500/20"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  Platform workspace
                </button>
              )}
              {isAuthenticated && user && (
                <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs text-zinc-500">
                  {user.display_name}
                </span>
              )}
              <button
                type="button"
                onClick={logout}
                className="rounded-xl border border-border bg-black/20 p-2 text-zinc-500 hover:text-zinc-300"
                title="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={handleRun}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black shadow-glow disabled:opacity-50"
                style={{ backgroundColor: accent }}
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
                Infer
              </button>
            </div>
          </div>
        </header>

        <div className="scrollbar-thin flex-1 overflow-y-auto px-8 py-6">
          {tab !== "overview" && (
            <section className="mb-6 rounded-3xl border border-white/10 bg-white/[0.025] p-5">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="flex items-center gap-2 text-sm font-medium text-zinc-300">
                    <Sparkles className="h-4 w-4" style={{ color: accent }} />
                    Scenario controls
                  </h3>
                  <p className="mt-1 text-xs text-zinc-600">
                    Adjust stochastic generator parameters before inference, sweeps, or MLOps pipeline runs.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setParamValues(Object.fromEntries(
                    ctx.model.parameters.map((p) => [p.name, p.default as string | number | boolean])
                  ))}
                  className="rounded-xl border border-white/10 px-3 py-2 text-xs text-zinc-400 hover:bg-white/5"
                >
                  Reset defaults
                </button>
              </div>
              <DynamicParameterForm
                parameters={ctx.model.parameters}
                values={paramValues}
                onChange={(name, value) => setParamValues((p) => ({ ...p, [name]: value }))}
                accentColor={accent}
              />
            </section>
          )}

          {error && (
            <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="mb-6 flex flex-wrap gap-2 rounded-2xl border border-white/10 bg-black/20 p-1.5">
            {tabs.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`rounded-xl px-4 py-2 text-sm capitalize transition ${
                  tab === t ? "font-medium text-black" : "text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                }`}
                style={tab === t ? { backgroundColor: accent } : undefined}
              >
                {t}
              </button>
            ))}
          </div>

          {tab === "overview" && (
            <>
            {onSwitchToPlatform && (
              <section className="mb-6 rounded-2xl border border-sky-500/20 bg-sky-500/5 px-5 py-4">
                <p className="text-sm text-zinc-400">
                  MLOps pipelines, DuckDB analytics, ML inferencing, and insights live in the{" "}
                  <button
                    type="button"
                    onClick={onSwitchToPlatform}
                    className="font-medium text-sky-400 hover:underline"
                  >
                    Platform workspace
                  </button>
                  .
                </p>
              </section>
            )}
            <HomeOverview
              catalog={catalog}
              accentColor={accent}
              totalRuns={totalRuns}
              onSelect={(s) => {
                setSelection(s);
                setTab("results");
              }}
              onRunDemo={handleDemoRun}
              onOpenResults={(r) => {
                setResult(r);
                setTab("results");
              }}
              demoLoading={demoLoading}
              lastDemo={lastDemo}
            />
            </>
          )}

          {tab === "results" && (
            <div className="space-y-6">
              {result ? (
                <>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <ExportBar runId={result.run_id} runIds={[result.run_id]} accentColor={accent} />
                    {(result.model_version || result.predictor_type) && (
                      <p className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs text-zinc-500">
                        Model v{result.model_version ?? "—"} · {result.predictor_type?.replace(/_/g, " ") ?? "predictor"}
                        {result.latency_ms != null && ` · ${result.latency_ms} ms`}
                      </p>
                    )}
                  </div>
                  <ResearchRunSummary result={result} accentColor={accent} />
                  {result.predictions && Object.keys(result.predictions).length > 0 ? (
                    <PredictionsGrid predictions={result.predictions} accentColor={accent} />
                  ) : (
                    <PredictionsGrid
                      predictions={Object.fromEntries(
                        Object.entries(result.metrics).map(([k, v]) => [k, { value: v }])
                      )}
                      accentColor={accent}
                    />
                  )}
                  {result.series.forecast && result.series.observed ? (
                    <ForecastChart series={result.series} accentColor={accent} />
                  ) : (
                    Object.keys(result.series).length > 0 && (
                      <SeriesChart series={result.series} accentColor={accent} />
                    )
                  )}
                </>
              ) : (
                <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-16 text-center">
                  <p className="text-lg font-medium text-zinc-300">No inference selected</p>
                  <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-zinc-600">
                    Press Infer to generate a stochastic synthetic scenario, forecasts, uncertainty intervals,
                    and lineage-ready metadata for this model.
                  </p>
                </div>
              )}
            </div>
          )}

          {tab === "docs" && (
            <SmartDocumentationPanel
              catalog={catalog}
              selection={selection}
              result={result}
              accentColor={accent}
            />
          )}

          {tab === "sweeps" && selection && (
            <SweepPanel
              selection={selection}
              accentColor={accent}
              onComplete={() => {
                refreshHistory();
                setTab("history");
              }}
            />
          )}

          {tab === "compare" && (
            <ComparePanel
              history={history}
              accentColor={accent}
            />
          )}

          {tab === "data" && (
            <DatasetsPanel domainTag={selection.domainId} accentColor={accent} />
          )}

          {tab === "history" && (
            <>
              <ExportBar
                runIds={history.map((h) => h.run_id)}
                comparisonId={comparisonId ?? undefined}
                accentColor={accent}
              />
              <RunHistory runs={history} accentColor={accent} activeRunId={result?.run_id} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function HeaderPill({ label }: { label: string }) {
  return (
    <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-zinc-500">
      {label}
    </span>
  );
}
