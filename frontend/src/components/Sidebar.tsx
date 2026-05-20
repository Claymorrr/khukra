"use client";

import clsx from "clsx";
import { Box, Brain, ChevronRight, Cpu, Layers, LineChart, Truck } from "lucide-react";
import type { CatalogResponse, Selection } from "@/lib/types";

const DOMAIN_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

interface SidebarProps {
  catalog: CatalogResponse;
  selection: Selection;
  onSelect: (s: Selection) => void;
}

export function Sidebar({ catalog, selection, onSelect }: SidebarProps) {
  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-r border-border bg-surface-raised/85 backdrop-blur-xl">
      <div className="border-b border-border px-5 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10">
            <Layers className="h-6 w-6 text-[var(--accent)]" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-wide">Khukra</h1>
            <p className="text-xs text-zinc-500">Research MLOps cockpit</p>
          </div>
        </div>
        <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-3">
          <p className="text-[10px] uppercase tracking-[0.22em] text-zinc-600">Workflow</p>
          <p className="mt-1 text-xs leading-5 text-zinc-400">
            Synthetic data → stochastic inference → optimization-ready evidence.
          </p>
        </div>
      </div>

      <nav className="scrollbar-thin flex-1 overflow-y-auto px-3 py-4">
        {catalog.domains.map((domain) => {
          const Icon = DOMAIN_ICONS[domain.id] ?? Box;
          const isDomainActive = selection.domainId === domain.id;

          return (
            <div key={domain.id} className="mb-4">
              <div
                className="mb-2 flex items-center gap-2 rounded-xl px-2 py-1.5 text-xs font-medium uppercase tracking-wider text-zinc-500"
                style={{ color: isDomainActive ? domain.color : undefined }}
              >
                <Icon className="h-3.5 w-3.5" style={{ color: domain.color }} />
                {domain.label}
              </div>

              {domain.subdomains.map((sub) => (
                <div key={sub.id} className="mb-1">
                  <button
                    type="button"
                    onClick={() =>
                      onSelect({
                        domainId: domain.id,
                        subdomainId: sub.id,
                        modelId: sub.models[0]?.id ?? "",
                      })
                    }
                    className={clsx(
                      "flex w-full items-center gap-1 rounded-xl px-2 py-2 text-left text-sm transition-colors",
                      selection.subdomainId === sub.id && isDomainActive
                        ? "bg-white/[0.07] text-white"
                        : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                    )}
                  >
                    <ChevronRight
                      className={clsx(
                        "h-3.5 w-3.5 shrink-0 transition-transform",
                        selection.subdomainId === sub.id && isDomainActive && "rotate-90"
                      )}
                    />
                    <span className="truncate">{sub.label}</span>
                  </button>

                  {selection.subdomainId === sub.id && isDomainActive && (
                    <div className="ml-5 mt-1 space-y-1 border-l border-border pl-2">
                      {sub.models.map((model) => (
                        <button
                          key={model.id}
                          type="button"
                          onClick={() =>
                            onSelect({
                              domainId: domain.id,
                              subdomainId: sub.id,
                              modelId: model.id,
                            })
                          }
                          className={clsx(
                            "block w-full rounded-lg px-2 py-1.5 text-left text-xs transition-colors",
                            selection.modelId === model.id
                              ? "font-medium text-white"
                              : "text-zinc-500 hover:text-zinc-300"
                          )}
                          style={
                            selection.modelId === model.id
                              ? { color: domain.color }
                              : undefined
                          }
                        >
                          {model.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          );
        })}
      </nav>
      <div className="border-t border-border px-5 py-4">
        <p className="text-xs leading-5 text-zinc-600">
          Use Docs for model context, MLOps for registry/evaluation, Query for DuckDB SQL, and Lineage for evidence provenance.
        </p>
      </div>
    </aside>
  );
}
