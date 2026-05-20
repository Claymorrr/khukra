"use client";

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ForecastChartProps {
  series: Record<string, number[]>;
  accentColor: string;
}

export function ForecastChart({ series, accentColor }: ForecastChartProps) {
  const hasForecast =
    series.forecast_time?.length &&
    series.forecast?.length &&
    series.observed?.length &&
    series.time?.length;

  if (!hasForecast) return null;

  const hist = series.time.map((t, i) => ({
    time: t,
    observed: series.observed[i],
    forecast: null as number | null,
    lower: null as number | null,
    upper: null as number | null,
  }));

  const fc = series.forecast_time.map((t, i) => ({
    time: t,
    observed: null as number | null,
    forecast: series.forecast[i],
    lower: series.forecast_lower?.[i] ?? null,
    upper: series.forecast_upper?.[i] ?? null,
  }));

  const data = [...hist, ...fc];
  const latest = series.observed[series.observed.length - 1];
  const terminal = series.forecast[series.forecast.length - 1];
  const drift =
    latest != null && terminal != null ? ((terminal - latest) / Math.max(Math.abs(latest), 1e-6)) * 100 : null;

  return (
    <div className="glass rounded-3xl p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            Forecast with 95% interval
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            Observed synthetic history followed by stochastic forecast path.
          </p>
        </div>
        {drift != null && (
          <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-2 text-right">
            <p className="text-[10px] uppercase tracking-wide text-zinc-600">Terminal drift</p>
            <p className="font-mono text-sm font-semibold" style={{ color: accentColor }}>
              {drift >= 0 ? "+" : ""}
              {drift.toFixed(2)}%
            </p>
          </div>
        )}
      </div>
      <div className="h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis dataKey="time" tick={{ fill: "#8b949e", fontSize: 11 }} />
          <YAxis tick={{ fill: "#8b949e", fontSize: 11 }} width={56} />
          <Tooltip
            contentStyle={{
              background: "#161b22",
              border: "1px solid #30363d",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill={accentColor}
            fillOpacity={0.12}
            connectNulls
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="none"
            fill="#0d1117"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="observed"
            stroke={accentColor}
            strokeWidth={2}
            dot={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#a78bfa"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}
