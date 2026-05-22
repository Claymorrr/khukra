"use client";

import clsx from "clsx";
import { ChevronRight, Layers } from "lucide-react";
import type { DomainInfo, Selection } from "@/lib/types";

interface DomainSidebarProps {
  domain: DomainInfo;
  selection: Selection;
  onSelect: (s: Selection) => void;
}

export function DomainSidebar({ domain, selection, onSelect }: DomainSidebarProps) {
  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border bg-surface-raised/85 backdrop-blur-xl">
      <div className="border-b border-border px-5 py-6">
        <div className="flex items-center gap-2">
          <div
            className="flex h-11 w-11 items-center justify-center rounded-2xl"
            style={{ backgroundColor: `${domain.color}22` }}
          >
            <Layers className="h-6 w-6" style={{ color: domain.color }} />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-wide text-white">{domain.label}</h1>
            <p className="text-xs text-zinc-500">
              {domain.id === "physical" ? "Subdomains & solvers" : "Subdomains & models"}
            </p>
          </div>
        </div>
      </div>

      <nav className="scrollbar-thin flex-1 overflow-y-auto px-3 py-4">
        {domain.subdomains.map((sub) => {
          const isSubActive = selection.subdomainId === sub.id;
          return (
            <div key={sub.id} className="mb-3">
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
                  isSubActive ? "bg-white/[0.07] text-white" : "text-zinc-400 hover:bg-white/5"
                )}
              >
                <ChevronRight
                  className={clsx(
                    "h-3.5 w-3.5 shrink-0 transition-transform",
                    isSubActive && "rotate-90"
                  )}
                />
                <span className="truncate">{sub.label}</span>
              </button>

              {isSubActive && (
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
                        selection.modelId === model.id ? { color: domain.color } : undefined
                      }
                    >
                      <span className="block truncate">{model.label}</span>
                      {domain.id === "physical" && model.model_kind && (
                        <span className="mt-0.5 block text-[10px] font-normal uppercase tracking-wide text-zinc-600">
                          {model.model_kind.replace(/_/g, " ")}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
