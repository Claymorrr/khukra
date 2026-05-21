"use client";

import type { ComponentType } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box,
  Brain,
  Cpu,
  Home,
  LineChart,
  Loader2,
  LogOut,
  Play,
  Sparkles,
  Truck,
} from "lucide-react";
import { createInference, getCatalog, getStats, listRuns } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { CatalogResponse, RunResponse, RunSummary, Selection } from "@/lib/types";
import { ComparePanel } from "../ComparePanel";
import { DatasetsPanel } from "../DatasetsPanel";
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
import { InsightsEngineering } from "../platform/InsightsEngineering";
import { MLInferencingPanel } from "../platform/MLInferencingPanel";
import { DevOpsPanel, InfraOpsPanel } from "../platform/OpsReadinessPanel";
import { PlatformMLOpsPanel } from "../platform/PlatformMLOpsPanel";
import { DomainOverview } from "./DomainOverview";
import { DomainSidebar } from "./DomainSidebar";
import { normalizeDomainManifest } from "@/lib/domainManifest";
import { DOMAIN_MODULES, type DomainModule } from "./types";

const DOMAIN_NAV_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

type PanelProps = { accentColor: string; domainId: string };

const PLATFORM_PANELS: Partial<Record<DomainModule, ComponentType<PanelProps>>> = {
  data_generation: DataGenerationStudio,
  mlops: PlatformMLOpsPanel,
  infraops: InfraOpsPanel,
  devops: DevOpsPanel,
  ml_inference: MLInferencingPanel,
  analytics: AnalyticsWorkbench,
  insights: InsightsEngineering,
};

interface DomainShellProps {
  domainId: string;
  initialModule?: string;
  initialSubdomain?: string;
  initialModel?: string;
}

export function DomainShell({
  domainId,
  initialModule,
  initialSubdomain,
  initialModel,
}: DomainShellProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, string | number | boolean>>({});
  const [result, setResult] = useState<RunResponse | null>(null);
  const [history, setHistory] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bootError, setBootError] = useState<string | null>(null);
  const [totalRuns, setTotalRuns] = useState(0);
  const [catalogLoading, setCatalogLoading] = useState(true);

  const moduleFromUrl = (searchParams.get("module") ?? initialModule ?? "overview") as DomainModule;

  const setModule = useCallback(
    (mod: DomainModule) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("module", mod);
      router.replace(`/domain/${domainId}?${params.toString()}`);
    },
    [domainId, router, searchParams]
  );

  const setDomain = useCallback(
    (id: string) => {
      router.replace(`/domain/${id}?module=${moduleFromUrl}`);
    },
    [moduleFromUrl, router]
  );

  useEffect(() => {
    setCatalogLoading(true);
    getCatalog()
      .then((data) => {
        setCatalog(data);
        const domain = data.domains.find((d) => d.id === domainId) ?? data.domains[0];
        if (!domain) return;
        const sub =
          domain.subdomains.find((s) => s.id === initialSubdomain) ?? domain.subdomains[0];
        const model = sub?.models.find((m) => m.id === initialModel) ?? sub?.models[0];
        if (sub && model) {
          setSelection({ domainId: domain.id, subdomainId: sub.id, modelId: model.id });
        }
      })
      .catch((e) => setBootError(e instanceof Error ? e.message : "Failed to load catalog"))
      .finally(() => setCatalogLoading(false));
    getStats().then((s) => setTotalRuns(s.inferences ?? s.runs)).catch(() => {});
  }, [domainId, initialModel, initialSubdomain]);

  const ctx = useMemo(() => {
    if (!catalog || !selection) return null;
    const domain = catalog.domains.find((d) => d.id === selection.domainId);
    const subdomain = domain?.subdomains.find((s) => s.id === selection.subdomainId);
    const model = subdomain?.models.find((m) => m.id === selection.modelId);
    if (!domain || !subdomain || !model) return null;
    return { domain, subdomain, model };
  }, [catalog, selection]);

  const refreshHistory = useCallback(() => {
    getStats().then((s) => setTotalRuns(s.inferences ?? s.runs)).catch(() => {});
    listRuns(domainId).then(setHistory).catch(() => setHistory([]));
  }, [domainId]);

  useEffect(() => {
    if (!ctx) return;
    const defaults: Record<string, string | number | boolean> = {};
    for (const p of ctx.model.parameters) {
      defaults[p.name] = p.default as string | number | boolean;
    }
    setParamValues(defaults);
    refreshHistory();
  }, [ctx?.domain.id, ctx?.subdomain.id, ctx?.model.id, refreshHistory]);

  useEffect(() => {
    if (ctx?.domain.color) {
      document.documentElement.style.setProperty("--accent", ctx.domain.color);
      document.documentElement.style.setProperty("--accent-glow", `${ctx.domain.color}40`);
    }
  }, [ctx?.domain.color]);

  useEffect(() => {
    if (!catalog) return;
    const exists = catalog.domains.some((d) => d.id === domainId);
    if (!exists && catalog.domains[0]) {
      router.replace(`/domain/${catalog.domains[0].id}?module=${moduleFromUrl}`);
    }
  }, [catalog, domainId, moduleFromUrl, router]);

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
      setModule("results");
      refreshHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Inference failed");
    } finally {
      setLoading(false);
    }
  }, [selection, ctx, paramValues, refreshHistory, setModule]);

  if (bootError) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <div className="glass max-w-md rounded-xl p-8 text-center">
          <p className="text-red-400">Cannot connect to API</p>
          <p className="mt-2 text-sm text-zinc-500">{bootError}</p>
        </div>
      </div>
    );
  }

  if (catalogLoading || !catalog || !selection || !ctx) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  const accent = ctx.domain.color;
  const manifest = normalizeDomainManifest(ctx.domain.id, ctx.domain.manifest);
  const moduleOrder = manifest.module_order;
  const orderedModules = [
    ...moduleOrder
      .map((id) => DOMAIN_MODULES.find((mod) => mod.id === id))
      .filter((mod): mod is (typeof DOMAIN_MODULES)[number] => Boolean(mod)),
    ...DOMAIN_MODULES.filter((mod) => !moduleOrder.includes(mod.id)),
  ];
  const ActivePlatformPanel = PLATFORM_PANELS[moduleFromUrl];
  const showScenarioControls = ![
    "overview",
    "data_generation",
    "mlops",
    "infraops",
    "devops",
    "ml_inference",
    "analytics",
    "insights",
  ].includes(moduleFromUrl);

  return (
    <div className="flex h-screen overflow-hidden bg-[#07090d]">
      <aside className="flex w-56 shrink-0 flex-col border-r border-white/10 bg-black/40">
        <div className="border-b border-white/10 px-4 py-5">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            <Sparkles className="h-4 w-4" style={{ color: accent }} />
            Khukra
          </p>
          <button
            type="button"
            onClick={() => router.push("/")}
            className="mt-3 flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <Home className="h-3.5 w-3.5" />
            All domains
          </button>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          {catalog.domains.map((d) => {
            const Icon = DOMAIN_NAV_ICONS[d.id] ?? Box;
            const active = d.id === domainId;
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => setDomain(d.id)}
                className={`flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm transition ${
                  active ? "bg-white/10 font-medium text-white" : "text-zinc-500 hover:bg-white/5"
                }`}
                style={active ? { boxShadow: `inset 3px 0 0 ${d.color}` } : undefined}
              >
                <Icon className="h-4 w-4 shrink-0" style={{ color: d.color }} />
                <span className="truncate text-left text-xs">{d.label.split(" — ")[0]}</span>
              </button>
            );
          })}
        </nav>
        <div className="border-t border-white/10 p-3">
          {user && <p className="truncate px-1 text-xs text-zinc-600">{user.display_name}</p>}
          <button
            type="button"
            onClick={logout}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      </aside>

      <DomainSidebar domain={ctx.domain} selection={selection} onSelect={setSelection} />

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="shrink-0 border-b border-white/10 bg-[#07090d]/90 px-6 py-4 backdrop-blur-xl">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-xs uppercase tracking-[0.28em] text-zinc-500">{ctx.domain.label}</p>
              <h2 className="mt-1 truncate text-2xl font-semibold text-white">{ctx.model.label}</h2>
              <p className="mt-1 max-w-3xl text-sm text-zinc-600">{ctx.subdomain.description}</p>
            </div>
            {(moduleFromUrl === "inference" || moduleFromUrl === "results") && (
              <button
                type="button"
                onClick={handleRun}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
                style={{ backgroundColor: accent }}
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
                Infer
              </button>
            )}
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {orderedModules.map((mod) => (
              <button
                key={mod.id}
                type="button"
                onClick={() => setModule(mod.id)}
                className={`rounded-lg px-2.5 py-1.5 text-xs transition ${
                  moduleFromUrl === mod.id
                    ? "font-medium text-black"
                    : "text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                }`}
                style={moduleFromUrl === mod.id ? { backgroundColor: accent } : undefined}
              >
                {mod.label}
              </button>
            ))}
          </div>
        </header>

        <div className="scrollbar-thin flex flex-1 overflow-y-auto">
          <div className="min-w-0 flex-1 px-6 py-5">
            {error && (
              <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            {showScenarioControls && (
              <section className="mb-6 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <DynamicParameterForm
                  parameters={ctx.model.parameters}
                  values={paramValues}
                  onChange={(name, value) => setParamValues((p) => ({ ...p, [name]: value }))}
                  accentColor={accent}
                />
              </section>
            )}

            {moduleFromUrl === "overview" && (
              <DomainOverview
                domain={ctx.domain}
                accentColor={accent}
                totalRuns={totalRuns}
                onNavigate={setModule}
              />
            )}

            {moduleFromUrl === "inference" && (
              <p className="text-sm text-zinc-500">
                Configure parameters above, then press <strong className="text-zinc-300">Infer</strong> to run the
                selected model. Results appear in the Results tab.
              </p>
            )}

            {moduleFromUrl === "results" && (
              <div className="space-y-6">
                {result ? (
                  <>
                    <ExportBar runId={result.run_id} runIds={[result.run_id]} accentColor={accent} />
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
                  <p className="text-sm text-zinc-500">No inference yet. Run Infer from the Models & Inference tab.</p>
                )}
              </div>
            )}

            {moduleFromUrl === "docs" && (
              <SmartDocumentationPanel
                catalog={catalog}
                selection={selection}
                result={result}
                accentColor={accent}
              />
            )}

            {moduleFromUrl === "sweeps" && (
              <SweepPanel
                selection={selection}
                accentColor={accent}
                onComplete={() => {
                  refreshHistory();
                  setModule("history");
                }}
              />
            )}

            {moduleFromUrl === "compare" && <ComparePanel history={history} accentColor={accent} />}

            {moduleFromUrl === "data" && (
              <DatasetsPanel domainTag={domainId} accentColor={accent} />
            )}

            {moduleFromUrl === "history" && (
              <>
                <ExportBar runIds={history.map((h) => h.run_id)} accentColor={accent} />
                <RunHistory runs={history} accentColor={accent} activeRunId={result?.run_id} />
              </>
            )}

            {ActivePlatformPanel && <ActivePlatformPanel accentColor={accent} domainId={domainId} />}

            {!["overview", "inference", "results", "docs", "sweeps", "compare", "data", "history"].includes(
              moduleFromUrl
            ) &&
              !ActivePlatformPanel && (
                <p className="text-sm text-zinc-500">Unknown capability: {moduleFromUrl}</p>
              )}
          </div>
        </div>
      </main>
    </div>
  );
}
