"use client";

import type { ComponentType } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  BarChart3,
  Brain,
  Database,
  LayoutDashboard,
  LogOut,
  BrainCircuit,
  Sparkles,
  Workflow,
  Loader2,
} from "lucide-react";
import { getPlatformManifest, type PlatformModuleManifest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PlatformOverview } from "./PlatformOverview";
import { DataGenerationStudio } from "./DataGenerationStudio";
import { PlatformMLOpsPanel } from "./PlatformMLOpsPanel";
import { MLInferencingPanel } from "./MLInferencingPanel";
import { AnalyticsWorkbench } from "./AnalyticsWorkbench";
import { InsightsEngineering } from "./InsightsEngineering";

export type PlatformModule =
  | "overview"
  | "data_generation"
  | "mlops"
  | "ml_inference"
  | "analytics"
  | "insights";

const FALLBACK_NAV: PlatformModuleManifest[] = [
  { id: "overview", label: "Overview", description: "", route_id: "overview", icon: "layout-dashboard", order: 0, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "data_generation", label: "Data Generation", description: "", route_id: "data_generation", icon: "database", order: 1, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "mlops", label: "MLOps", description: "", route_id: "mlops", icon: "workflow", order: 2, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "ml_inference", label: "ML Inferencing", description: "", route_id: "ml_inference", icon: "brain-circuit", order: 3, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "analytics", label: "Analytics", description: "", route_id: "analytics", icon: "bar-chart", order: 4, capabilities: [], actions: [], required_roles: [], enabled: true },
  { id: "insights", label: "Insights", description: "", route_id: "insights", icon: "brain", order: 5, capabilities: [], actions: [], required_roles: [], enabled: true },
];

const ICON_MAP: Record<string, typeof Database> = {
  "layout-dashboard": LayoutDashboard,
  database: Database,
  workflow: Workflow,
  "brain-circuit": BrainCircuit,
  "bar-chart": BarChart3,
  brain: Brain,
};

const MODULE_COMPONENTS: Partial<Record<PlatformModule, ComponentType<{ accentColor: string }>>> = {
  data_generation: DataGenerationStudio,
  mlops: PlatformMLOpsPanel,
  ml_inference: MLInferencingPanel,
  analytics: AnalyticsWorkbench,
  insights: InsightsEngineering,
};

const ACCENT = "#38bdf8";

interface PlatformShellProps {
  onSwitchToResearch: () => void;
  initialModule?: string;
}

export function PlatformShell({ onSwitchToResearch, initialModule }: PlatformShellProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [manifestModules, setManifestModules] = useState<PlatformModuleManifest[]>(FALLBACK_NAV);
  const [manifestLoading, setManifestLoading] = useState(true);

  const moduleFromUrl = (searchParams.get("module") ?? initialModule ?? "overview") as PlatformModule;

  const setModule = useCallback(
    (id: PlatformModule) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("module", id);
      router.replace(`/platform?${params.toString()}`);
    },
    [router, searchParams]
  );

  useEffect(() => {
    getPlatformManifest()
      .then((m) => setManifestModules(m.modules.length ? m.modules : FALLBACK_NAV))
      .catch(() => setManifestModules(FALLBACK_NAV))
      .finally(() => setManifestLoading(false));
  }, []);

  const nav = useMemo(
    () => [...manifestModules].sort((a, b) => a.order - b.order),
    [manifestModules]
  );

  const active = nav.find((n) => n.id === moduleFromUrl) ?? nav[0];
  const ActiveModule = MODULE_COMPONENTS[moduleFromUrl as PlatformModule];

  return (
    <div className="flex h-screen overflow-hidden bg-[#07090d]">
      <aside className="flex w-64 shrink-0 flex-col border-r border-white/10 bg-black/40">
        <div className="border-b border-white/10 px-5 py-6">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            <Sparkles className="h-4 w-4 text-sky-400" />
            Khukra Platform
          </p>
          <h1 className="mt-2 text-lg font-semibold text-white">Data & MLOps</h1>
          <p className="mt-1 text-xs leading-5 text-zinc-600">
            Metadata-driven modules from platform manifest.
          </p>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {manifestLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
            </div>
          ) : (
            nav.map((item) => {
              const Icon = ICON_MAP[item.icon] ?? Database;
              const id = item.id as PlatformModule;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setModule(id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                    moduleFromUrl === id
                      ? "bg-sky-500/15 font-medium text-sky-200"
                      : "text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                  }`}
                  title={item.description}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {item.label}
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
            Platform workspace
          </p>
          <h2 className="mt-1 text-2xl font-semibold text-white">{active?.label}</h2>
          {active?.description && (
            <p className="mt-1 max-w-3xl text-sm text-zinc-600">{active.description}</p>
          )}
        </header>
        <div className="px-8 py-6">
          {moduleFromUrl === "overview" && (
            <PlatformOverview accentColor={ACCENT} onNavigate={setModule} />
          )}
          {moduleFromUrl !== "overview" && ActiveModule && <ActiveModule accentColor={ACCENT} />}
          {moduleFromUrl !== "overview" && !ActiveModule && (
            <p className="text-sm text-zinc-500">Unknown module: {moduleFromUrl}</p>
          )}
        </div>
      </main>
    </div>
  );
}
