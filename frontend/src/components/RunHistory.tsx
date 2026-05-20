"use client";

import clsx from "clsx";
import { Clock } from "lucide-react";
import type { RunSummary } from "@/lib/types";

interface RunHistoryProps {
  runs: RunSummary[];
  accentColor: string;
  activeRunId?: string;
}

export function RunHistory({ runs, accentColor, activeRunId }: RunHistoryProps) {
  if (runs.length === 0) {
    return (
      <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-12 text-center">
        <p className="text-sm text-zinc-500">No runs recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      {runs.slice(0, 12).map((run) => (
        <div
          key={run.run_id}
          className={clsx(
            "glass flex items-start justify-between gap-4 rounded-2xl px-4 py-4 transition hover:-translate-y-0.5 hover:shadow-glow",
            run.run_id === activeRunId && "border border-transparent"
          )}
          style={
            run.run_id === activeRunId
              ? {
                  borderColor: accentColor,
                  boxShadow: `0 0 20px -8px ${accentColor}`,
                }
              : undefined
          }
        >
          <div className="min-w-0">
            <p className="truncate text-sm font-medium capitalize text-zinc-200">
              {run.model_name.replace(/_/g, " ")}
            </p>
            <p className="flex items-center gap-1 text-xs text-zinc-500">
              <Clock className="h-3 w-3" />
              {new Date(run.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="shrink-0 text-right">
            {Object.entries(run.metrics)
              .slice(0, 2)
              .map(([k, v]) => (
                <p key={k} className="font-mono text-xs text-zinc-400">
                  {k.split("_")[0]}: {v.toFixed(3)}
                </p>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
