"use client";

import type { ComponentType } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  BarChart3,
  Box,
  Brain,
  BrainCircuit,
  Cpu,
  Database,
  LayoutDashboard,
  LineChart,
  Loader2,
  LogOut,
  Truck,
  Workflow,
} from "lucide-react";
import {
  getPlatformManifest,
  type PlatformDomainManifest,
  type PlatformModuleManifest,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PlatformOverview } from "./PlatformOverview";
import { DataGenerationStudio } from "./DataGenerationStudio";
import { PlatformMLOpsPanel } from "./PlatformMLOpsPanel";
import { MLInferencingPanel } from "./MLInferencingPanel";
import { AnalyticsWorkbench } from "./AnalyticsWorkbench";
import { InsightsEngineering } from "./InsightsEngineering";
import { KhukraLogo } from "@/components/brand/KhukraLogo";

export type PlatformModule =
  | "overview"
  | "data_generation"
  | "mlops"
  | "ml_inference"
  | "analytics"
  | "insights";

const FALLBACK_DOMAINS: PlatformDomainManifest[] = [
  { id: "physical", label: "Physical Systems", color: "#38bdf8", icon: "box", order: 0 },
  { id: "finance", label: "Finance", color: "#34d399", icon: "line-chart", order: 1 },
  { id: "supply_chain", label: "Supply Chain", color: "#fbbf24", icon: "truck", order: 2 },
  { id: "intelligence", label: "Intelligence", color: "#a78bfa", icon: "brain", order: 3 },
  { id: "computing", label: "Computing", color: "#f472b6", icon: "cpu", order: 4 },
];

const FALLBACK_MODULES: PlatformModuleManifest[] = [
  { id: "overview", label: "Overview", description: "", route_id: "overview", icon: "layout-dashboard", order: 0, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "data_generation", label: "Data Generation", description: "", route_id: "data_generation", icon: "database", order: 1, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "mlops", label: "MLOps", description: "", route_id: "mlops", icon: "workflow", order: 2, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "ml_inference", label: "ML Inferencing", description: "", route_id: "ml_inference", icon: "brain-circuit", order: 3, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "analytics", label: "Analytics", description: "", route_id: "analytics", icon: "bar-chart", order: 4, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "insights", label: "Insights", description: "", route_id: "insights", icon: "brain", order: 5, capabilities: [], actions: [], required_roles: [], enabled: true },
];

const DOMAIN_ICON_MAP: Record<string, typeof Box> = {
  box: Box,
  "line-chart": LineChart,
  truck: Truck,
  brain: Brain,
  cpu: Cpu,
};

const MODULE_ICON_MAP: Record<string, typeof Database> = {
  "layout-dashboard": LayoutDashboard,
  database: Database,
  workflow: Workflow,
  "brain-circuit": BrainCircuit,
  "bar-chart": BarChart3,
  brain: Brain,
};

type ModulePanelProps = { accentColor: string; domainId: string };

const MODULE_COMPONENTS: Partial<Record<PlatformModule, ComponentType<ModulePanelProps>>> = {
  data_generation: DataGenerationStudio,
  mlops: PlatformMLOpsPanel,
  ml_inference: MLInferencingPanel,
  analytics: AnalyticsWorkbench,
  insights: InsightsEngineering,
};

interface PlatformShellProps {
  onSwitchToResearch: () => void;
  initialModule?: string;
  initialDomain?: string;
}

export function PlatformShell({
  onSwitchToResearch,
  initialModule,
  initialDomain,
}: PlatformShellProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [manifestDomains, setManifestDomains] = useState<PlatformDomainManifest[]>(FALLBACK_DOMAINS);
  const [manifestModules, setManifestModules] = useState<PlatformModuleManifest[]>(FALLBACK_MODULES);
  const [manifestLoading, setManifestLoading] = useState(true);

  const domainFromUrl =
    searchParams.get("domain") ?? initialDomain ?? manifestDomains[0]?.id ?? "physical";
  const moduleFromUrl = (searchParams.get("module") ?? initialModule ?? "overview") as PlatformModule;

  const updateUrl = useCallback(
    (domain: string, module: PlatformModule) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("domain", domain);
      params.set("module", module);
      router.replace(`/platform?${params.toString()}`);
    },
    [router, searchParams]
  );

  const setDomain = useCallback(
    (id: string) => updateUrl(id, moduleFromUrl),
    [moduleFromUrl, updateUrl]
  );

  const setModule = useCallback(
    (id: PlatformModule) => updateUrl(domainFromUrl, id),
    [domainFromUrl, updateUrl]
  );

  useEffect(() => {
    getPlatformManifest()
      .then((m) => {
        setManifestDomains(m.domains?.length ? m.domains : FALLBACK_DOMAINS);
        setManifestModules(m.modules.length ? m.modules : FALLBACK_MODULES);
      })
      .catch(() => {
        setManifestDomains(FALLBACK_DOMAINS);
        setManifestModules(FALLBACK_MODULES);
      })
      .finally(() => setManifestLoading(false));
  }, []);

  const domains = useMemo(
    () => [...manifestDomains].sort((a, b) => a.order - b.order),
    [manifestDomains]
  );

  const modules = useMemo(
    () => [...manifestModules].sort((a, b) => a.order - b.order),
    [manifestModules]
  );

  const activeDomain = domains.find((d) => d.id === domainFromUrl) ?? domains[0];
  const activeModule = modules.find((m) => m.id === moduleFromUrl) ?? modules[0];
  const accent = activeDomain?.color ?? "#38bdf8";
  const ActiveModule = MODULE_COMPONENTS[moduleFromUrl as PlatformModule];

  return (
    <div className="flex h-screen overflow-hidden bg-[#07090d]">
      <aside className="flex w-64 shrink-0 flex-col border-r border-white/10 bg-black/40">
        <div className="border-b border-white/10 px-5 py-6">
          <KhukraLogo accentColor={accent} subtitle="Platform" />
          <h1 className="mt-2 text-lg font-semibold text-white">By domain</h1>
          <p className="mt-1 text-xs leading-5 text-zinc-600">
            Data, MLOps, inference, analytics, and insights per domain.
          </p>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {manifestLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
            </div>
          ) : (
            domains.map((item) => {
              const Icon = DOMAIN_ICON_MAP[item.icon] ?? Box;
              const isActive = domainFromUrl === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setDomain(item.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                    isActive
                      ? "bg-white/10 font-medium text-white"
                      : "text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                  }`}
                  style={isActive ? { boxShadow: `inset 3px 0 0 ${item.color}` } : undefined}
                >
                  <Icon className="h-4 w-4 shrink-0" style={{ color: item.color }} />
                  <span className="truncate text-left">{item.label}</span>
                </button>
              );
            })
          )}
        </nav>
        <div className="space-y-2 border-t border-white/10 p-4">
          <button
            type="button"
            onClick={onSwitchToResearch}
            className="w-full rounded-xl border border-white/10 px-3 py-2 text-xs text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
          >
            ← Research workspace
          </button>
          {user && (
            <p className="truncate px-1 text-xs text-zinc-600">{user.display_name}</p>
          )}
          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="scrollbar-thin flex min-w-0 flex-1 flex-col overflow-y-auto">
        <header className="sticky top-0 z-10 border-b border-white/10 bg-[#07090d]/90 px-8 py-5 backdrop-blur-xl">
          <p className="text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            {activeDomain?.label ?? "Platform"}
          </p>
          <h2 className="mt-1 text-2xl font-semibold text-white">
            {activeModule?.label ?? "Overview"}
          </h2>
          {activeModule?.description && (
            <p className="mt-1 max-w-3xl text-sm text-zinc-600">{activeModule.description}</p>
          )}
          <div className="mt-4 flex flex-wrap gap-2">
            {modules.map((item) => {
              const Icon = MODULE_ICON_MAP[item.icon] ?? Database;
              const id = item.id as PlatformModule;
              const isActive = moduleFromUrl === id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setModule(id)}
                  className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs transition ${
                    isActive
                      ? "font-medium text-white"
                      : "border border-white/10 text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                  }`}
                  style={
                    isActive
                      ? { backgroundColor: `${accent}22`, borderColor: `${accent}55`, color: accent }
                      : undefined
                  }
                >
                  <Icon className="h-3.5 w-3.5 shrink-0" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </header>
        <div className="px-8 py-6">
          {moduleFromUrl === "overview" && activeDomain && (
            <PlatformOverview
              accentColor={accent}
              domainId={activeDomain.id}
              domainLabel={activeDomain.label}
              onNavigate={(m) => setModule(m as PlatformModule)}
            />
          )}
          {moduleFromUrl !== "overview" && ActiveModule && activeDomain && (
            <ActiveModule accentColor={accent} domainId={activeDomain.id} />
          )}
          {moduleFromUrl !== "overview" && !ActiveModule && (
            <p className="text-sm text-zinc-500">Unknown module: {moduleFromUrl}</p>
          )}
        </div>
      </main>
    </div>
  );
}
