"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { FunctionSquare, Loader2 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getIndexDecomposition, type IndexDecomposition } from "@/lib/api/disruption";
import { CHART_GRID, CHART_TOOLTIP } from "@/lib/chartTheme";

const CHANNEL_COLORS: Record<string, string> = {
  macro: "#a78bfa",
  market: "#38bdf8",
  news: "#22d3ee",
};

function fmt(n: number | null | undefined, d = 3): string {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toFixed(d);
}

function FormulaBlock({ title, latex, substitution }: { title: string; latex: string; substitution?: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/35 p-4">
      <p className="text-[10px] font-medium uppercase tracking-wider text-sky-400/90">{title}</p>
      <p className="mt-2 font-mono text-sm leading-relaxed text-zinc-100">{latex}</p>
      {substitution && (
        <p className="mt-2 border-t border-white/5 pt-2 font-mono text-xs leading-relaxed text-amber-200/90">
          {substitution}
        </p>
      )}
    </div>
  );
}

export function IndexMathVisual({ refreshKey = 0 }: { refreshKey?: number }) {
  const [data, setData] = useState<IndexDecomposition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getIndexDecomposition());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load index decomposition");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const byChannel = useMemo(() => {
    if (!data) return { macro: [], market: [], news: [] };
    const buckets: Record<string, typeof data.signals> = { macro: [], market: [], news: [] };
    for (const s of data.signals) {
      buckets[s.channel]?.push(s);
    }
    return buckets;
  }, [data]);

  const contribChart = useMemo(() => {
    if (!data) return [];
    return Object.entries(data.channel_contributions).map(([ch, v]) => ({
      channel: ch,
      value: v,
      fill: CHANNEL_COLORS[ch] ?? "#888",
    }));
  }, [data]);

  const channelSub = useMemo(() => {
    if (!data) return "";
    const parts = Object.entries(data.channels)
      .filter(([, ch]) => ch.value != null)
      .map(([name, ch]) => {
        const inner = ch.signal_ids
          .map((id) => {
            const w = ch.inverse_variance_weights[id];
            const sig = data.signals.find((s) => s.signal_id === id);
            return `${fmt(w, 2)}·z(${id})=${fmt(sig?.z_score, 2)}`;
          })
          .join(" + ");
        return `Z_${name} = ${inner} = ${fmt(ch.value, 3)}`;
      });
    return parts.join("  |  ");
  }, [data]);

  const compositeSub = useMemo(() => {
    if (!data) return "";
    const α = data.parameters.channel_weights;
    const terms = Object.entries(data.channels)
      .filter(([, ch]) => ch.value != null)
      .map(([name, ch]) => `${fmt(α[name], 2)}·Z_${name}(${fmt(ch.value, 3)})`);
    const sum = terms.join(" + ");
    return `C_t = ${sum} = ${fmt(data.composite_raw, 3)}σ  →  C̃_t (smooth) = ${fmt(data.composite_smoothed, 3)}σ`;
  }, [data]);

  return (
    <section className="rounded-2xl border border-sky-500/25 bg-gradient-to-br from-sky-950/30 via-black/40 to-violet-950/20 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-sky-300">
            <FunctionSquare className="h-4 w-4" />
            Index — mathematical decomposition
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            Live substitution at {data?.date ?? "…"} using the same formulas as production.
          </p>
        </div>
        {loading && <Loader2 className="h-5 w-5 animate-spin text-sky-400/60" />}
      </div>

      {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

      {data && !error && (
        <div className="mt-5 space-y-5">
          {/* Pipeline */}
          <div className="flex flex-wrap items-center justify-center gap-2 text-center font-mono text-xs text-zinc-400">
            <span className="rounded-lg border border-white/10 bg-black/40 px-3 py-2">x_t(i) raw</span>
            <span>→</span>
            <span className="rounded-lg border border-violet-500/30 bg-violet-950/30 px-3 py-2">z_t(i)</span>
            <span>→</span>
            <span className="rounded-lg border border-sky-500/30 bg-sky-950/30 px-3 py-2">Z_t(c)</span>
            <span>→</span>
            <span className="rounded-lg border border-amber-500/30 bg-amber-950/30 px-3 py-2">C_t</span>
            <span>→</span>
            <span className="rounded-lg border border-emerald-500/30 bg-emerald-950/30 px-3 py-2">C̃_t</span>
          </div>

          {/* Formulas with live numbers */}
          <div className="grid gap-3 lg:grid-cols-2">
            <FormulaBlock
              title="Step 1 — Rolling z-score (per signal i)"
              latex={data.formulas.z_score}
              substitution={
                data.signals[0]
                  ? `e.g. vix: (${fmt(data.signals.find((s) => s.signal_id === "vix")?.raw_value, 2)} − ${fmt(data.signals.find((s) => s.signal_id === "vix")?.rolling_mean_60, 2)}) / ${fmt(data.signals.find((s) => s.signal_id === "vix")?.rolling_std_60, 2)} = ${fmt(data.signals.find((s) => s.signal_id === "vix")?.z_score, 3)}`
                  : undefined
              }
            />
            <FormulaBlock
              title="Step 2 — Inverse-variance within channel"
              latex={data.formulas.channel}
              substitution={channelSub || undefined}
            />
            <FormulaBlock
              title="Step 3 — Channel-weighted composite"
              latex={data.formulas.composite}
              substitution={compositeSub}
            />
            <FormulaBlock
              title="Step 4 — Production smoothing"
              latex={data.formulas.smooth}
              substitution={`C̃_t = ${fmt(data.composite_smoothed, 3)}σ (used for 7-day forecast)`}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
            {/* Signal z-score matrix */}
            <div className="overflow-x-auto rounded-xl border border-white/10 bg-black/30 p-3">
              <p className="mb-2 text-xs font-medium text-zinc-300">Signal z-scores & channel weights</p>
              <table className="w-full min-w-[520px] text-left text-[11px]">
                <thead>
                  <tr className="border-b border-white/10 text-zinc-500">
                    <th className="py-1.5 pr-2">Signal</th>
                    <th className="py-1.5 pr-2">Ch</th>
                    <th className="py-1.5 pr-2 font-mono">z_t(i)</th>
                    <th className="py-1.5 pr-2 font-mono">w_i(c)</th>
                    <th className="py-1.5 font-mono">w_i·z</th>
                  </tr>
                </thead>
                <tbody>
                  {data.signals.map((s) => (
                    <tr key={s.signal_id} className="border-b border-white/5 text-zinc-300">
                      <td className="py-1.5 pr-2">{s.signal_id}</td>
                      <td className="py-1.5 pr-2 capitalize" style={{ color: CHANNEL_COLORS[s.channel] }}>
                        {s.channel}
                      </td>
                      <td className="py-1.5 pr-2 font-mono tabular-nums">{fmt(s.z_score)}</td>
                      <td className="py-1.5 pr-2 font-mono tabular-nums">{fmt(s.weight_in_channel, 2)}</td>
                      <td className="py-1.5 font-mono tabular-nums text-amber-200/80">
                        {fmt((s.weight_in_channel ?? 0) * s.z_score)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Contribution bar chart */}
            <div className="rounded-xl border border-white/10 bg-black/30 p-3">
              <p className="mb-1 text-xs font-medium text-zinc-300">C_t = Σ α_c · Z_c</p>
              <p className="mb-2 text-[10px] text-zinc-500">Channel contributions to composite</p>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={contribChart} layout="vertical" margin={{ left: 4, right: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 9 }} stroke="#555" />
                    <YAxis type="category" dataKey="channel" tick={{ fontSize: 10 }} stroke="#555" width={48} />
                    <Tooltip contentStyle={CHART_TOOLTIP} formatter={(v: number) => [v.toFixed(3), "contribution"]} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {contribChart.map((row) => (
                        <Cell key={row.channel} fill={row.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-2 text-center font-mono text-sm text-zinc-200">
                C_t = <span className="text-amber-300">{fmt(data.composite_raw)}</span>σ
              </p>
            </div>
          </div>

          {/* Per-channel expansion */}
          <div className="grid gap-3 md:grid-cols-3">
            {(["macro", "market", "news"] as const).map((ch) => (
              <div
                key={ch}
                className="rounded-xl border border-white/10 bg-black/25 p-3"
                style={{ borderColor: `${CHANNEL_COLORS[ch]}33` }}
              >
                <p className="text-xs font-medium capitalize" style={{ color: CHANNEL_COLORS[ch] }}>
                  {ch} · α = {fmt(data.parameters.channel_weights[ch], 2)}
                </p>
                <p className="mt-1 font-mono text-lg text-zinc-100">Z_{ch} = {fmt(data.channels[ch]?.value)}</p>
                <ul className="mt-2 space-y-1 text-[10px] text-zinc-500">
                  {byChannel[ch].map((s) => (
                    <li key={s.signal_id} className="font-mono">
                      w({s.signal_id})={fmt(s.weight_in_channel, 2)} · z={fmt(s.z_score)}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
