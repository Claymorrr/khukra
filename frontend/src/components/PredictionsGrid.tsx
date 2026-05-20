"use client";

import type { PredictionField } from "@/lib/types";

interface PredictionsGridProps {
  predictions: Record<string, PredictionField>;
  accentColor: string;
}

export function PredictionsGrid({ predictions, accentColor }: PredictionsGridProps) {
  const entries = Object.entries(predictions);

  if (entries.length === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {entries.map(([key, pred]) => (
        <div
          key={key}
          className="glass group relative overflow-hidden rounded-2xl p-5 transition hover:-translate-y-0.5 hover:shadow-glow"
          style={{ ["--accent-glow" as string]: `${accentColor}33` }}
        >
          <div
            className="absolute inset-x-0 top-0 h-1 opacity-80"
            style={{ backgroundColor: accentColor }}
          />
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            {key.replace(/_/g, " ")}
            {pred.unit ? ` (${pred.unit})` : ""}
          </p>
          <p
            className="mt-1 font-mono text-2xl font-semibold tabular-nums"
            style={{ color: accentColor }}
          >
            {formatValue(pred.value)}
          </p>
          {pred.confidence != null && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-zinc-500">
                <span>Confidence</span>
                <span>{(pred.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${Math.min(100, pred.confidence * 100)}%`, backgroundColor: accentColor }}
                />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function formatValue(value: number): string {
  if (Math.abs(value) >= 1e6) return value.toExponential(2);
  if (Math.abs(value) < 0.01 && value !== 0) return value.toExponential(3);
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}
