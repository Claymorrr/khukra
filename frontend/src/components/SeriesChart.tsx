"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RunResponse } from "@/lib/types";

interface SeriesChartProps {
  series: RunResponse["series"];
  accentColor: string;
}

export function SeriesChart({ series, accentColor }: SeriesChartProps) {
  const keys = Object.keys(series);
  if (keys.length < 2) return null;

  const xKey = keys[0];
  const yKeys = keys.slice(1);
  const length = series[xKey]?.length ?? 0;

  const data = Array.from({ length }, (_, i) => {
    const row: Record<string, number | string> = { [xKey]: series[xKey][i] };
    for (const yKey of yKeys) {
      const v = series[yKey][i];
      row[yKey] = typeof v === "number" && !Number.isNaN(v) ? v : (null as unknown as number);
    }
    return row;
  }).filter((row) => yKeys.some((k) => row[k] != null));

  if (data.length === 0) return null;

  const colors = [
    accentColor,
    "#a78bfa",
    "#fb7185",
    "#4ade80",
    "#fbbf24",
  ];

  const useArea = yKeys.length <= 2;

  return (
    <div className="glass h-[380px] rounded-xl p-4">
      <ResponsiveContainer width="100%" height="100%">
        {useArea ? (
          <AreaChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="fillPrimary" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={accentColor} stopOpacity={0.35} />
                <stop offset="100%" stopColor={accentColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis
              dataKey={xKey}
              tick={{ fill: "#8b949e", fontSize: 11 }}
              axisLine={{ stroke: "#30363d" }}
            />
            <YAxis
              tick={{ fill: "#8b949e", fontSize: 11 }}
              axisLine={{ stroke: "#30363d" }}
              width={56}
            />
            <Tooltip
              contentStyle={{
                background: "#161b22",
                border: "1px solid #30363d",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: "#8b949e" }} />
            {yKeys.map((key, i) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stroke={colors[i % colors.length]}
                fill={i === 0 ? "url(#fillPrimary)" : "none"}
                strokeWidth={2}
                dot={false}
                connectNulls
              />
            ))}
          </AreaChart>
        ) : (
          <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis dataKey={xKey} tick={{ fill: "#8b949e", fontSize: 11 }} />
            <YAxis tick={{ fill: "#8b949e", fontSize: 11 }} width={56} />
            <Tooltip
              contentStyle={{
                background: "#161b22",
                border: "1px solid #30363d",
                borderRadius: 8,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {yKeys.map((key, i) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={colors[i % colors.length]}
                strokeWidth={2}
                dot={false}
                connectNulls
              />
            ))}
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
