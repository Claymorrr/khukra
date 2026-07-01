"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DisruptionSignal, ExploreResult } from "@/lib/api/disruption";
import { CHART_GRID, CHART_TOOLTIP } from "@/lib/chartTheme";

const EXPLORE_METHODS: Array<{ key: keyof ExploreResult; label: string }> = [
  { key: "correlation_matrices", label: "Correlation" },
  { key: "mutual_information", label: "Mutual information" },
  { key: "pca", label: "PCA" },
  { key: "rolling_correlation", label: "Rolling corr" },
  { key: "changepoints", label: "Changepoints" },
  { key: "clustering", label: "Clustering" },
  { key: "bayesian_predictive", label: "Bayesian predictive" },
];

function MethodsStatusBar({ explore }: { explore: ExploreResult }) {
  const ran = new Set(explore.methods_run);
  return (
    <div className="flex flex-wrap gap-2">
      {EXPLORE_METHODS.map(({ key, label }) => {
        const ok = ran.has(key);
        return (
          <span
            key={key}
            className={`rounded-full border px-2.5 py-1 text-[10px] font-medium ${
              ok
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                : "border-red-500/30 bg-red-500/5 text-red-300/80"
            }`}
          >
            {ok ? "✓" : "✗"} {label}
          </span>
        );
      })}
      <span className="self-center text-[10px] text-zinc-600">
        {explore.methods_run.length} / {EXPLORE_METHODS.length} methods
      </span>
    </div>
  );
}

interface AdvancedExplorationProps {
  explore: ExploreResult | null;
  catalogById: Record<string, DisruptionSignal>;
  loading?: boolean;
}

export function AdvancedExploration({ explore, catalogById, loading }: AdvancedExplorationProps) {
  const heatmapGrid = useMemo(() => {
    if (!explore?.correlation_matrices) return null;
    const { signals, pearson } = explore.correlation_matrices;
    const lookup = new Map(pearson.map((c) => [`${c.signal_a}:${c.signal_b}`, c.value]));
    return signals.map((row) => signals.map((col) => lookup.get(`${row}:${col}`) ?? 0));
  }, [explore]);

  const pcaChartData = useMemo(() => {
    const pca = explore?.pca;
    if (!pca?.components[0]?.series) return [];
    const pc1 = pca.components[0].series;
    const pc2 = pca.components[1]?.series;
    return pc1.dates.map((date, i) => ({
      date,
      PC1: pc1.values[i],
      PC2: pc2?.values[i] ?? null,
    }));
  }, [explore]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-zinc-500">
        Running advanced exploration…
      </div>
    );
  }

  if (!explore) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-white/10 text-sm text-zinc-600">
        Click Explore to run all 7 methods: correlation, mutual information, PCA, rolling
        correlation, changepoints, clustering, and Bayesian predictive comparison.
      </div>
    );
  }

  const heatmap = explore.correlation_matrices;
  const pca = explore.pca;
  const rolling = explore.rolling_correlation;
  const changepoints = explore.changepoints;
  const rollingPair = rolling?.pairs[0];

  return (
    <div className="space-y-4">
      <MethodsStatusBar explore={explore} />
      {explore.methods_expected != null && explore.methods_run.length < explore.methods_expected && (
        <p className="text-xs text-amber-300/90">
          Only {explore.methods_run.length}/{explore.methods_expected} methods ran — refresh macro
          signals (VIX, oil, shipping) then click Explore again.
        </p>
      )}
      <p className="text-[11px] text-zinc-500">
        {explore.signal_scope === "all_cached"
          ? "Advanced exploration uses all cached macro + news signals (sidebar selection applies to charts only)."
          : explore.methodology}
      </p>

      <div className="grid gap-4 xl:grid-cols-2">
        {heatmap && heatmapGrid && (
          <ChartCard title="Correlation heatmap (Pearson)" subtitle={heatmap.interpretation}>
            <div className="overflow-x-auto">
              <table className="mx-auto text-xs">
                <thead>
                  <tr>
                    <th />
                    {heatmap.signals.map((s) => (
                      <th key={s} className="px-1 py-1 text-[10px] text-zinc-600">
                        {(catalogById[s]?.label ?? s).slice(0, 8)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {heatmap.signals.map((row, i) => (
                    <tr key={row}>
                      <td className="pr-2 text-[10px] text-zinc-600">
                        {(catalogById[row]?.label ?? row).slice(0, 10)}
                      </td>
                      {heatmapGrid[i].map((val, j) => (
                        <td key={`${row}-${j}`} className="p-0.5">
                          <div
                            className="flex h-8 w-10 items-center justify-center rounded text-[9px] font-mono text-white/90"
                            style={{ background: corrColor(val) }}
                            title={`r=${val.toFixed(3)}`}
                          >
                            {val.toFixed(2)}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>
        )}

        {pca && (
          <ChartCard title="PCA latent factors" subtitle={pca.interpretation}>
            <div className="mb-2 flex flex-wrap gap-2">
              {pca.components.map((pc) => (
                <span
                  key={pc.component}
                  className="rounded-md border border-white/10 bg-black/30 px-2 py-0.5 text-[10px] text-zinc-400"
                >
                  {pc.component}: {pc.explained_pct}% variance
                </span>
              ))}
            </div>
            {pcaChartData.length > 0 && (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={pcaChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                  <XAxis dataKey="date" tick={{ fontSize: 9 }} stroke="#555" minTickGap={50} />
                  <YAxis tick={{ fontSize: 9 }} stroke="#555" width={32} />
                  <Tooltip contentStyle={CHART_TOOLTIP} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  <Line type="monotone" dataKey="PC1" stroke="#f59e0b" dot={false} strokeWidth={2} />
                  {pca.components.length > 1 && (
                    <Line type="monotone" dataKey="PC2" stroke="#38bdf8" dot={false} strokeWidth={1.5} />
                  )}
                </LineChart>
              </ResponsiveContainer>
            )}
          </ChartCard>
        )}

        {rollingPair && (
          <ChartCard
            title={`Rolling correlation · ${rollingPair.signal_a} ↔ ${rollingPair.signal_b}`}
            subtitle={rolling?.interpretation ?? ""}
          >
            <ResponsiveContainer width="100%" height={240}>
              <LineChart
                data={rollingPair.series.dates.map((date, i) => ({
                  date,
                  correlation: rollingPair.series.correlation[i],
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                <XAxis dataKey="date" tick={{ fontSize: 9 }} stroke="#555" minTickGap={40} />
                <YAxis domain={[-1, 1]} tick={{ fontSize: 9 }} stroke="#555" width={28} />
                <Tooltip contentStyle={CHART_TOOLTIP} />
                <ReferenceLine y={0} stroke="#444" />
                <Line type="monotone" dataKey="correlation" stroke="#a855f7" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        )}

        {explore.mutual_information && (
          <ChartCard title="Mutual information" subtitle={explore.mutual_information.interpretation}>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart
                data={explore.mutual_information.cells
                  .filter((c) => c.signal_a !== c.signal_b)
                  .sort((a, b) => b.mutual_information - a.mutual_information)
                  .slice(0, 8)
                  .map((c) => ({
                    pair: `${c.signal_a}↔${c.signal_b}`,
                    mi: c.mutual_information,
                  }))}
                layout="vertical"
                margin={{ left: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                <XAxis type="number" tick={{ fontSize: 9 }} stroke="#555" />
                <YAxis type="category" dataKey="pair" tick={{ fontSize: 8 }} stroke="#555" width={78} />
                <Tooltip contentStyle={CHART_TOOLTIP} />
                <Bar dataKey="mi" fill="#22c55e" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {explore.clustering && (
          <div className="rounded-xl border border-white/10 bg-black/25 p-4">
            <h3 className="text-sm font-medium text-zinc-200">Signal clusters</h3>
            <p className="mt-1 text-[11px] text-zinc-500">{explore.clustering.interpretation}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {explore.clustering.clusters.map((cl) => (
                <div
                  key={cl.cluster_id}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-zinc-400"
                >
                  <span className="text-[10px] uppercase text-zinc-600">Cluster {cl.cluster_id}</span>
                  <p className="mt-1 text-zinc-300">
                    {cl.signals.map((s) => catalogById[s]?.label ?? s).join(" · ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {explore.bayesian_predictive && explore.bayesian_predictive.tests.length > 0 && (
          <div className="rounded-xl border border-white/10 bg-black/25 p-4">
            <h3 className="text-sm font-medium text-zinc-200">Bayesian predictive comparison</h3>
            <p className="mt-1 text-[11px] text-zinc-500">{explore.bayesian_predictive.interpretation}</p>
            <ul className="mt-3 space-y-2">
              {explore.bayesian_predictive.tests.map((t) => (
                <li key={`${t.cause}-${t.effect}`} className="text-xs text-zinc-400">
                  <span className={t.posterior_prob >= 0.8 ? "text-emerald-400" : "text-zinc-300"}>
                    {t.cause} → {t.effect}
                  </span>
                  <span className="ml-2 font-mono text-[10px] text-zinc-600">
                    P={t.posterior_prob.toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {changepoints && changepoints.composite.changepoints.length > 0 && (
          <div className="rounded-xl border border-white/10 bg-black/25 p-4 md:col-span-2">
            <h3 className="text-sm font-medium text-zinc-200">Composite changepoints</h3>
            <p className="mt-1 text-[11px] text-zinc-500">{changepoints.interpretation}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {changepoints.composite.changepoints.map((cp) => (
                <span
                  key={cp.date}
                  className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-100"
                >
                  {cp.date} · z={cp.composite_z}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-black/40 p-4">
      <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
      <p className="mb-3 text-[11px] leading-4 text-zinc-500">{subtitle}</p>
      {children}
    </div>
  );
}

function corrColor(r: number): string {
  const t = (r + 1) / 2;
  if (r >= 0) {
    const g = Math.round(80 + t * 120);
    return `rgb(${Math.round(180 - t * 100)}, ${g}, 80)`;
  }
  const intensity = Math.round(Math.abs(r) * 180);
  return `rgb(80, 80, ${120 + intensity})`;
}
