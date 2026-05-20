"use client";

interface MetricsGridProps {
  metrics: Record<string, number>;
  accentColor: string;
}

export function MetricsGrid({ metrics, accentColor }: MetricsGridProps) {
  const entries = Object.entries(metrics);

  if (entries.length === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="glass rounded-xl p-4 transition hover:shadow-glow"
          style={{ ["--accent-glow" as string]: `${accentColor}33` }}
        >
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            {key.replace(/_/g, " ")}
          </p>
          <p
            className="mt-1 font-mono text-2xl font-semibold tabular-nums"
            style={{ color: accentColor }}
          >
            {formatMetric(value)}
          </p>
        </div>
      ))}
    </div>
  );
}

function formatMetric(value: number): string {
  if (Math.abs(value) >= 1e6) return value.toExponential(2);
  if (Math.abs(value) < 0.01 && value !== 0) return value.toExponential(3);
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}
