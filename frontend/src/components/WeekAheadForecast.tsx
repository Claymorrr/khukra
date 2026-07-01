"use client";

import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  CalendarRange,
  Loader2,
  Minus,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getProductionModel, type ProductionModelResult } from "@/lib/api/disruption";
import { CHART_GRID, CHART_TOOLTIP, FORECAST_COLOR, PRODUCTION_COLOR } from "@/lib/chartTheme";

export const WEEK_HORIZON = 7;
const HIST_CONTEXT_DAYS = 42;

function addDays(iso: string, n: number): string {
  const d = new Date(`${iso}T12:00:00`);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

function formatDayLabel(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function riskTone(z: number): { label: string; className: string; bar: string } {
  if (z >= 1.5) return { label: "Elevated", className: "text-red-400", bar: "bg-red-500" };
  if (z >= 0.5) return { label: "Watch", className: "text-amber-400", bar: "bg-amber-500" };
  if (z <= -0.5) return { label: "Calm", className: "text-emerald-400", bar: "bg-emerald-500" };
  return { label: "Neutral", className: "text-zinc-400", bar: "bg-zinc-500" };
}

export function WeekAheadForecast({ refreshKey = 0 }: { refreshKey?: number }) {
  const [model, setModel] = useState<ProductionModelResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const prod = await getProductionModel(WEEK_HORIZON);
      setModel(prod);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load week forecast";
      if (msg.includes("not found") || msg.includes("404")) {
        setError("Week forecast API not loaded — restart with .\\scripts\\setup.ps1 -Dev");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const week = useMemo(() => {
    if (!model?.production_series?.dates?.length || !model.forecast.length) return null;

    const { dates: histDates, values: histValues } = model.production_series;
    const lastDate = histDates[histDates.length - 1];
    const todayZ = histValues[histValues.length - 1];

    const days = model.forecast.map((value, i) => {
      const date = addDays(lastDate, i + 1);
      const lower = model.forecast_lower[i] ?? value;
      const upper = model.forecast_upper[i] ?? value;
      const prev = i === 0 ? todayZ : model.forecast[i - 1];
      const delta = value - prev;
      return { day: i + 1, date, value, lower, upper, delta, tone: riskTone(value) };
    });

    const histTail = Math.min(HIST_CONTEXT_DAYS, histDates.length);
    const histSlice = histValues.slice(-histTail);
    const chartHistFixed = histDates.slice(-histTail).map((date, i) => ({
      date,
      label: formatDayLabel(date),
      actual: histSlice[i],
      projected: null as number | null,
      lower: null as number | null,
      upper: null as number | null,
      phase: "history" as const,
    }));

    const bridge = {
      date: lastDate,
      label: formatDayLabel(lastDate),
      actual: todayZ,
      projected: todayZ,
      lower: null as number | null,
      upper: null as number | null,
      phase: "history" as const,
    };

    const chartProj = days.map((d) => ({
      date: d.date,
      label: formatDayLabel(d.date),
      actual: null as number | null,
      projected: d.value,
      lower: d.lower,
      upper: d.upper,
      phase: "forecast" as const,
    }));

    const chartData = [...chartHistFixed.slice(0, -1), bridge, ...chartProj];
    const forecastStart = chartProj[0]?.date;
    const forecastEnd = chartProj[chartProj.length - 1]?.date;

    const weekEnd = days[days.length - 1].value;
    const weekDelta = weekEnd - todayZ;
    const weekPeak = Math.max(...days.map((d) => d.upper));
    const weekTrough = Math.min(...days.map((d) => d.lower));

    return {
      todayZ,
      lastDate,
      days,
      chartData,
      forecastStart,
      forecastEnd,
      weekEnd,
      weekDelta,
      weekPeak,
      weekTrough,
      endTone: riskTone(weekEnd),
      trend:
        weekDelta > 0.08 ? "rising" : weekDelta < -0.08 ? "falling" : ("stable" as const),
    };
  }, [model]);

  return (
    <section className="rounded-2xl border border-amber-500/30 bg-gradient-to-br from-amber-950/40 via-black/50 to-sky-950/30 p-5 shadow-lg shadow-amber-950/20">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-amber-300">
            <CalendarRange className="h-4 w-4" />
            Next 7 days — disruption outlook
          </p>
          <p className="mt-1 max-w-xl text-sm text-zinc-400">
            Mean-reversion forecast on the smoothed hybrid index. Each point is one business day ahead.
          </p>
        </div>
        {loading && <Loader2 className="h-5 w-5 animate-spin text-amber-400/60" />}
      </div>

      {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

      {week && !error && (
        <>
          {/* Summary strip */}
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <SummaryCard
              label="Today"
              value={week.todayZ.toFixed(2)}
              suffix="σ"
              sub={riskTone(week.todayZ).label}
              subClass={riskTone(week.todayZ).className}
            />
            <SummaryCard
              label="Day 7"
              value={week.weekEnd.toFixed(2)}
              suffix="σ"
              sub={week.endTone.label}
              subClass={week.endTone.className}
            />
            <SummaryCard
              label="Week change"
              value={`${week.weekDelta >= 0 ? "+" : ""}${week.weekDelta.toFixed(2)}`}
              suffix="σ"
              sub={week.trend}
              icon={
                week.trend === "rising" ? (
                  <TrendingUp className="h-3.5 w-3.5 text-amber-400" />
                ) : week.trend === "falling" ? (
                  <TrendingDown className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <Minus className="h-3.5 w-3.5 text-zinc-500" />
                )
              }
            />
            <SummaryCard
              label="Week range"
              value={`${week.weekTrough.toFixed(2)} – ${week.weekPeak.toFixed(2)}`}
              suffix="σ"
              sub="uncertainty band"
            />
            <SummaryCard
              label="Model"
              value="MR"
              sub={`${model?.smooth_days ?? 9}d smooth · MAE ${model?.forecast_mae?.toFixed(3) ?? "—"}`}
            />
          </div>

          {/* Hero chart — zoomed to context + week */}
          <div className="mt-5 rounded-xl border border-amber-500/20 bg-black/40 p-4">
            <p className="mb-2 text-xs font-medium text-zinc-300">Week ahead (focused view)</p>
            <div className="h-[min(44vh,380px)]">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={week.chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="weekBand" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={FORECAST_COLOR} stopOpacity={0.22} />
                      <stop offset="100%" stopColor={FORECAST_COLOR} stopOpacity={0.04} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} />
                  <XAxis
                    dataKey="label"
                    tick={{ fontSize: 10, fill: "#888" }}
                    interval="preserveStartEnd"
                    minTickGap={20}
                  />
                  <YAxis tick={{ fontSize: 10, fill: "#888" }} width={36} domain={["auto", "auto"]} />
                  <Tooltip
                    contentStyle={CHART_TOOLTIP}
                    labelFormatter={(_, payload) => {
                      const row = payload?.[0]?.payload as { date?: string; phase?: string } | undefined;
                      return row?.date ? `${formatDayLabel(row.date)}${row.phase === "forecast" ? " (forecast)" : ""}` : "";
                    }}
                  />
                  {week.forecastStart && week.forecastEnd && (
                    <ReferenceArea
                      x1={formatDayLabel(week.forecastStart)}
                      x2={formatDayLabel(week.forecastEnd)}
                      fill="url(#weekBand)"
                      strokeOpacity={0}
                    />
                  )}
                  <ReferenceLine y={1.5} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.7} />
                  <ReferenceLine y={-1.5} stroke="#22c55e" strokeDasharray="4 4" strokeOpacity={0.7} />
                  <ReferenceLine y={0} stroke="#444" />
                  <Area
                    type="monotone"
                    dataKey="upper"
                    stroke="none"
                    fill={FORECAST_COLOR}
                    fillOpacity={0.1}
                    connectNulls
                    legendType="none"
                  />
                  <Area
                    type="monotone"
                    dataKey="lower"
                    stroke="none"
                    fill="#0c0f14"
                    fillOpacity={1}
                    connectNulls
                    legendType="none"
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Recent actual"
                    stroke={PRODUCTION_COLOR}
                    strokeWidth={3}
                    dot={false}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="projected"
                    name="7-day forecast"
                    stroke={FORECAST_COLOR}
                    strokeWidth={3}
                    strokeDasharray="8 4"
                    dot={{ r: 4, fill: FORECAST_COLOR, strokeWidth: 0 }}
                    connectNulls
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Day-by-day cards */}
          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">
            {week.days.map((d) => (
              <div
                key={d.date}
                className="rounded-xl border border-white/10 bg-black/35 p-3 transition hover:border-amber-500/30"
              >
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">Day {d.day}</p>
                <p className="mt-0.5 text-xs font-medium text-zinc-300">{formatDayLabel(d.date)}</p>
                <p className="mt-2 text-xl font-semibold tabular-nums text-zinc-100">
                  {d.value.toFixed(2)}
                  <span className="text-sm font-normal text-zinc-500">σ</span>
                </p>
                <div className="mt-1 flex items-center gap-1 text-[11px]">
                  {d.delta > 0.02 ? (
                    <ArrowUp className="h-3 w-3 text-amber-400" />
                  ) : d.delta < -0.02 ? (
                    <ArrowDown className="h-3 w-3 text-emerald-400" />
                  ) : (
                    <ArrowRight className="h-3 w-3 text-zinc-600" />
                  )}
                  <span className="text-zinc-500">
                    {d.delta >= 0 ? "+" : ""}
                    {d.delta.toFixed(2)}
                  </span>
                </div>
                <p className={`mt-1 text-[10px] font-medium ${d.tone.className}`}>{d.tone.label}</p>
                <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/5">
                  <div
                    className={`h-full ${d.tone.bar}`}
                    style={{ width: `${Math.min(100, ((d.value + 2) / 4) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {!error && !loading && !week && (
        <p className="mt-4 text-sm text-zinc-500">Refresh signals to generate the week-ahead forecast.</p>
      )}
    </section>
  );
}

function SummaryCard({
  label,
  value,
  suffix,
  sub,
  subClass,
  icon,
}: {
  label: string;
  value: string;
  suffix?: string;
  sub?: string;
  subClass?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/30 px-3 py-2.5">
      <p className="text-[10px] uppercase tracking-wider text-zinc-500">{label}</p>
      <p className="mt-1 flex items-baseline gap-1 text-xl font-semibold text-zinc-100">
        {value}
        {suffix && <span className="text-sm font-normal text-zinc-500">{suffix}</span>}
        {icon && <span className="ml-1">{icon}</span>}
      </p>
      {sub && <p className={`mt-0.5 text-xs capitalize ${subClass ?? "text-zinc-500"}`}>{sub}</p>}
    </div>
  );
}
