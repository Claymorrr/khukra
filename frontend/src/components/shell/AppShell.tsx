"use client";

import type { ComponentType, ReactNode } from "react";
import { useCallback, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  BookOpen,
  Box,
  Brain,
  Cpu,
  Database,
  Home,
  Layers,
  LineChart,
  Loader2,
  LogOut,
  Play,
  Truck,
  Wrench,
} from "lucide-react";
import { getCatalog } from "@/lib/api";
import { zonePath, type AppZone } from "@/lib/api/v1";
import { useAuth } from "@/lib/auth";
import type { CatalogResponse, DomainInfo } from "@/lib/types";
import { DomainLakePanel } from "../platform/DomainLakePanel";
import { DataOpsPanel } from "../platform/DataOpsPanel";
import { KnowledgePanel } from "../platform/KnowledgePanel";
import { DevOpsPanel, InfraOpsPanel } from "../platform/OpsReadinessPanel";
import { DomainOverview } from "../domain/DomainOverview";
import { DomainAssistant } from "../assistant/DomainAssistant";
import { DomainCockpit } from "../cockpit/DomainCockpit";
import { normalizeDomainManifest } from "@/lib/domainManifest";
import { KhukraLogo } from "@/components/brand/KhukraLogo";

const DOMAIN_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

const ZONES: Array<{ id: AppZone; label: string; icon: typeof Layers }> = [
  { id: "discover", label: "Discover", icon: Layers },
  { id: "data", label: "Data plane", icon: Database },
  { id: "knowledge", label: "Knowledge", icon: BookOpen },
  { id: "workflows", label: "Cockpit", icon: Play },
  { id: "operations", label: "Operations", icon: Wrench },
];

interface AppShellProps {
  domainId: string;
  zone: AppZone;
  productId?: string;
  children?: ReactNode;
  /** Deep-link solver context for physical workbench */
  workflowSubdomain?: string;
  workflowModel?: string;
}

export function AppShell({
  domainId,
  zone,
  productId,
  children,
  workflowSubdomain,
  workflowModel,
}: AppShellProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCatalog()
      .then(setCatalog)
      .catch(() => setCatalog(null))
      .finally(() => setLoading(false));
  }, []);

  const domain = catalog?.domains.find((d) => d.id === domainId);
  const accent = domain?.color ?? "#38bdf8";
  const manifest = normalizeDomainManifest(domainId, domain?.manifest);
  const displayLabel = domain?.label ?? domainId;
  const displayTagline =
    manifest.tagline ||
    "Develop → validate → package → operate inference and simulation workloads.";

  const setZone = useCallback(
    (z: AppZone) => {
      router.push(zonePath(domainId, z));
    },
    [domainId, router]
  );

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#07090d] text-white">
      <aside className="flex w-52 shrink-0 flex-col border-r border-white/10 bg-black/50">
        <div className="border-b border-white/10 px-4 py-4">
          <KhukraLogo accentColor={accent} subtitle="Inference & Simulation Cockpit" />
          <button
            type="button"
            onClick={() => router.push("/")}
            className="mt-3 flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300"
          >
            <Home className="h-3.5 w-3.5" />
            Home
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          {catalog?.domains.map((d) => {
            const Icon = DOMAIN_ICONS[d.id] ?? Box;
            const active = d.id === domainId;
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => router.push(zonePath(d.id, "workflows"))}
                className={`flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs transition ${
                  active ? "bg-white/10 text-white" : "text-zinc-500 hover:bg-white/5"
                }`}
              >
                <Icon className="h-4 w-4" style={{ color: d.color }} />
                <span className="truncate">{d.label.split(" — ")[0]}</span>
              </button>
            );
          })}
        </nav>

        <div className="border-t border-white/10 p-2">
          {ZONES.map((z) => {
            const Icon = z.icon;
            const active = zone === z.id && pathname?.includes(`/d/${domainId}`);
            return (
              <button
                key={z.id}
                type="button"
                onClick={() => setZone(z.id)}
                className={`mb-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs ${
                  active ? "bg-white/10 font-medium text-white" : "text-zinc-500 hover:bg-white/5"
                }`}
                style={active ? { boxShadow: `inset 3px 0 0 ${accent}` } : undefined}
              >
                <Icon className="h-3.5 w-3.5" />
                {z.label}
              </button>
            );
          })}
        </div>

        <div className="border-t border-white/10 p-3">
          {user && <p className="truncate text-xs text-zinc-600">{user.display_name}</p>}
          <button
            type="button"
            onClick={logout}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2 text-xs text-zinc-500"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="shrink-0 border-b border-white/10 px-6 py-4">
          <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">
            {displayLabel}
          </p>
          <h1 className="mt-1 text-2xl font-semibold">{displayTagline}</h1>
          {productId && (
            <p className="mt-1 font-mono text-xs text-zinc-500">Product: {productId}</p>
          )}
        </header>
        <div className="scrollbar-thin flex-1 overflow-y-auto px-6 py-5">
          {children ?? (
            <ZoneContent
              zone={zone}
              domainId={domainId}
              domain={domain}
              accentColor={accent}
              productId={productId}
              workflowSubdomain={workflowSubdomain}
              workflowModel={workflowModel}
            />
          )}
        </div>
      </main>
      <DomainAssistant
        domain={domain}
        domainId={domainId}
        zone={zone}
        accentColor={accent}
      />
    </div>
  );
}

function ZoneContent({
  zone,
  domainId,
  domain,
  accentColor,
  productId,
  workflowSubdomain,
  workflowModel,
}: {
  zone: AppZone;
  domainId: string;
  domain?: DomainInfo;
  accentColor: string;
  productId?: string;
  workflowSubdomain?: string;
  workflowModel?: string;
}) {
  if (zone === "discover" && domain) {
    return (
      <DomainOverview
        domain={domain}
        accentColor={accentColor}
        totalRuns={0}
        onNavigate={(mod) => {
          const map: Partial<Record<string, AppZone>> = {
            data_hub: "data",
            data: "data",
            knowledge: "knowledge",
            inference: "workflows",
            results: "workflows",
            sweeps: "workflows",
            data_generation: "data",
            mlops: "workflows",
            infraops: "operations",
            devops: "operations",
            analytics: "workflows",
          };
          window.location.href = zonePath(domainId, map[mod] ?? "discover");
        }}
      />
    );
  }
  if (zone === "data") {
    return (
      <div className="space-y-8">
        {domainId === "physical" && (
          <section
            className="rounded-3xl border border-white/10 bg-white/[0.035] p-6"
            style={{ borderColor: `${accentColor}33` }}
          >
            <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">Domain data plane</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Traces, artifacts, sweeps, and validation evidence from workload runs.
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-zinc-500">
              Supporting layer for inference and simulation execution — persisted outputs,
              lineage, and knowledge assets behind the cockpit.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {["mechanics", "thermofluid", "dynamics", "solver outputs", "surrogate datasets"].map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-xs text-zinc-400"
                >
                  {item}
                </span>
              ))}
            </div>
            <button
              type="button"
              onClick={() => {
                window.location.href = zonePath(domainId, "workflows");
              }}
              className="mt-5 rounded-xl border border-white/10 px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
            >
              Open cockpit
            </button>
          </section>
        )}
        <DomainLakePanel domainId={domainId} accentColor={accentColor} />
        <DataOpsPanel domainId={domainId} accentColor={accentColor} />
      </div>
    );
  }
  if (zone === "knowledge") {
    return <KnowledgePanel domainId={domainId} accentColor={accentColor} />;
  }
  if (zone === "workflows" && domain) {
    return (
      <DomainCockpit
        domain={domain}
        accentColor={accentColor}
        initialSubdomain={workflowSubdomain}
        initialModel={workflowModel}
      />
    );
  }
  if (zone === "operations") {
    return (
      <div className="space-y-6">
        <InfraOpsPanel accentColor={accentColor} domainId={domainId} />
        <DevOpsPanel accentColor={accentColor} domainId={domainId} />
      </div>
    );
  }
  return <p className="text-sm text-zinc-500">Select a zone.</p>;
}
