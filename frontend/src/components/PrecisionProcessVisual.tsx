"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvaluationResult } from "@/lib/api/disruption";
import { CHART_GRID, CHART_TOOLTIP, FORECAST_COLOR, PRODUCTION_COLOR } from "@/lib/chartTheme";

const METHOD_LABEL: Record<string, string> = {
  mean_reversion: "Mean reversion",
  holt: "Holt linear",
  bayesian_linear: "Bayesian linear",
  naive: "Naive",
};

const PIPELINE_STEPS = [
  { key: "signals", label: "9 hybrid signals", detail: "macro · market · news" },
  { key: "zscore", label: "Rolling z-scores", detail: "60-day window per signal" },
  { key: "channels", label: "Channel combine", detail: "inverse-variance weights" },
  { key: "smooth", label: "9-day smooth", detail: "production input series" },
  { key: "walkforward", label: "Walk-forward", detail: "1-step predict on 2y tail" },
  { key: "score", label: "Precision score", detail: "MAE + direction + bonuses" },
];

interface PrecisionProcessVisualProps {
  evaluation: EvaluationResult;
}

export function PrecisionProcessVisual({ evaluation }: PrecisionProcessVisualProps) {
  const trace = evaluation.walk_forward.trace;
  const breakdown = evaluation.precision_breakdown;
  const ablation = evaluation.channel_ablation;
  const smoothDays = evaluation.hybrid_composite?.smooth_days ?? 9;
  const channelWeights =
    evaluation.hybrid_composite?.channel_weights ?? evaluation.hybrid.channel_weights;

  const traceChart = useMemo(
    () =>
      trace?.series.map((p) => ({
        date: p.date,
        actual: p.actual,
        predicted: p.predicted,
        error: p.abs_error,
      })) ?? [],
    [trace],
  );

  const scoreParts = useMemo(() => {
    if (!breakdown) return [];
    return [
      { name: "MAE quality (50%)", value: breakdown.mae_weighted, fill: "#a78bfa" },
      { name: "Direction (30%)", value: breakdown.direction_weighted, fill: "#38bdf8" },
      ...(breakdown.beat_holt_bonus > 0
        ? [{ name: "Beats Holt (+12)", value: breakdown.beat_holt_bonus, fill: "#34d399" }]
        : []),
      ...(breakdown.mae_target_bonus > 0
        ? [{ name: "MAE target (+8)", value: breakdown.mae_target_bonus, fill: "#fbbf24" }]
        : []),
    ];
  }, [breakdown]);

  const methodRows = useMemo(() => {
    const methods = evaluation.walk_forward.methods ?? {};
    return Object.entries(methods)
      .filter(([name]) => name !== "naive")
      .map(([name, stats]) => ({
        name: METHOD_LABEL[name] ?? name,
        mae: stats.walk_forward_mae,
        direction: Math.round(stats.direction_hit_rate * 100),
        isBest: name === evaluation.walk_forward.best_method,
      }))
      .sort((a, b) => a.mae - b.mae);
  }, [evaluation]);

  const ablationRows = useMemo(() => {
    if (!ablation) return [];
    return (["macro", "market", "news"] as const)
      .filter((ch) => ablation[`${ch}_lift`] != null)
      .map((ch) => ({
        channel: ch,
        lift: ablation[`${ch}_lift`] as number,
        withoutMae: ablation[`without_${ch}_mae`] as number,
      }))
      .sort((a, b) => b.lift - a.lift);
  }, [ablation]);

  const directionHits = trace?.series.filter((p) => p.direction_correct === true).length ?? 0;
  const directionTotal = trace?.series.filter((p) => p.direction_correct != null).length ?? 0;

  return (
    <div className="mt-4 space-y-4 border-t border-violet-500/20 pt-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-violet-300/80">
          How precision is measured
        </p>
        <p className="mt-1 text-xs text-zinc-500">
          Walk-forward backtest on the last {trace?.eval_window_days ?? 504} trading days (stride{" "}
          {trace?.stride ?? 2}) — train up to day t, predict t+1, compare to actual.
        </p>
      </div>

      {/* Pipeline flow */}
      <div className="flex flex-wrap items-center gap-1">
        {PIPELINE_STEPS.map((step, i) => (
          <div key={step.key} className="flex items-center gap-1">
            <div className="rounded-lg border border-white/10 bg-black/30 px-2.5 py-2">
              <p className="text-[10px] font-medium text-zinc-200">{step.label}</p>
              <p className="text-[9px] text-zinc-500">{step.detail}</p>
            </div>
            {i < PIPELINE_STEPS.length - 1 && (
              <span className="text-zinc-600" aria-hidden>
                →
              </span>
            )}
          </div>
        ))}
      </div>

      {channelWeights && (
        <p className="text-[11px] text-zinc-500">
          Channel weights: macro {(channelWeights.macro * 100).toFixed(0)}% · market{" "}
          {(channelWeights.market * 100).toFixed(0)}% · news {(channelWeights.news * 100).toFixed(0)}%
          {smoothDays ? ` · ${smoothDays}d smooth before scoring` : ""}
        </p>
      )}

      <div className="grid gap-4 xl:grid-cols-2">
        {/* Walk-forward actual vs predicted */}
        <div className="rounded-xl border border-white/10 bg-black/25 p-3">
          <p className="text-xs font-medium text-zinc-300">Walk-forward: actual vs predicted</p>
          <p className="text-[10px] text-zinc-500">
            {METHOD_LABEL[evaluation.walk_forward.best_method] ?? evaluation.walk_forward.best_method}
            {directionTotal > 0 &&
              ` · direction ${directionHits}/${directionTotal} correct (${Math.round((directionHits / directionTotal) * 100)}%)`}
          </p>
          {traceChart.length > 0 ? (
            <div className="mt-2 h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={traceChart}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                  <XAxis dataKey="date" tick={{ fontSize: 9 }} stroke="#555" minTickGap={32} />
                  <YAxis tick={{ fontSize: 9 }} stroke="#555" width={32} />
                  <Tooltip contentStyle={CHART_TOOLTIP} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  <ReferenceLine y={0} stroke="#444" />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual (smoothed)"
                    stroke={PRODUCTION_COLOR}
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="1-step prediction"
                    stroke={FORECAST_COLOR}
                    strokeWidth={1.5}
                    strokeDasharray="4 2"
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="mt-4 text-xs text-zinc-600">Run today&apos;s measure to generate walk-forward trace.</p>
          )}
        </div>

        {/* Score breakdown */}
        <div className="rounded-xl border border-white/10 bg-black/25 p-3">
          <p className="text-xs font-medium text-zinc-300">Score breakdown → {evaluation.precision_score}/100</p>
          <p className="text-[10px] text-zinc-500">
            MAE component uses 1 − MAE/0.65; target MAE ≤ {breakdown?.mae_target ?? 0.38}
          </p>
          {breakdown && scoreParts.length > 0 ? (
            <>
              <div className="mt-3 flex h-8 overflow-hidden rounded-lg">
                {scoreParts.map((part) => (
                  <div
                    key={part.name}
                    className="flex items-center justify-center text-[9px] font-medium text-black/80"
                    style={{
                      width: `${(part.value / Math.max(breakdown.raw_total, 0.01)) * 100}%`,
                      backgroundColor: part.fill,
                      minWidth: part.value > 0.04 ? "2rem" : 0,
                    }}
                    title={`${part.name}: +${(part.value * 100).toFixed(1)} pts`}
                  >
                    {part.value >= 0.08 ? `+${Math.round(part.value * 100)}` : ""}
                  </div>
                ))}
              </div>
              <ul className="mt-3 space-y-1.5 text-[11px]">
                {scoreParts.map((part) => (
                  <li key={part.name} className="flex justify-between text-zinc-400">
                    <span className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: part.fill }} />
                      {part.name}
                    </span>
                    <span className="text-zinc-300">+{(part.value * 100).toFixed(1)}</span>
                  </li>
                ))}
                <li className="flex justify-between border-t border-white/5 pt-1.5 font-medium text-zinc-200">
                  <span>Total (capped at 100)</span>
                  <span>{evaluation.precision_score}</span>
                </li>
              </ul>
            </>
          ) : (
            <p className="mt-4 text-xs text-zinc-600">Breakdown available after evaluation run.</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Model comparison */}
        <div className="rounded-xl border border-white/10 bg-black/25 p-3">
          <p className="text-xs font-medium text-zinc-300">Model comparison (walk-forward MAE)</p>
          <div className="mt-2 h-[140px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={methodRows} layout="vertical" margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 9 }} stroke="#555" domain={[0, "auto"]} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 9 }} stroke="#555" width={88} />
                <Tooltip contentStyle={CHART_TOOLTIP} />
                <Bar dataKey="mae" name="MAE" radius={[0, 4, 4, 0]}>
                  {methodRows.map((row) => (
                    <Cell key={row.name} fill={row.isBest ? "#34d399" : "#52525b"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel ablation */}
        <div className="rounded-xl border border-white/10 bg-black/25 p-3">
          <p className="text-xs font-medium text-zinc-300">Channel ablation (MAE lift)</p>
          <p className="text-[10px] text-zinc-500">
            Positive lift = channel helps full hybrid; negative = hurts
          </p>
          {ablationRows.length > 0 ? (
            <div className="mt-2 h-[140px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ablationRows} margin={{ left: 8, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                  <XAxis dataKey="channel" tick={{ fontSize: 10 }} stroke="#555" />
                  <YAxis tick={{ fontSize: 9 }} stroke="#555" width={36} />
                  <Tooltip
                    contentStyle={CHART_TOOLTIP}
                    formatter={(value: number, name: string) => [
                      name === "lift" ? value.toFixed(4) : value,
                      name === "lift" ? "MAE lift" : "MAE without channel",
                    ]}
                  />
                  <ReferenceLine y={0} stroke="#666" />
                  <Bar dataKey="lift" name="lift" radius={[4, 4, 0, 0]}>
                    {ablationRows.map((row) => (
                      <Cell key={row.channel} fill={row.lift > 0.01 ? "#34d399" : row.lift < -0.01 ? "#f87171" : "#71717a"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="mt-4 text-xs text-zinc-600">Ablation runs with full evaluation.</p>
          )}
        </div>
      </div>
    </div>
  );
}
