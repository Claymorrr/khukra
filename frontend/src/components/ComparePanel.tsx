"use client";

import { useState } from "react";
import { GitCompare, Loader2 } from "lucide-react";
import { createComparison } from "@/lib/api";
import type { ComparisonResponse, RunSummary } from "@/lib/types";

interface ComparePanelProps {
  history: RunSummary[];
  accentColor: string;
}

export function ComparePanel({ history, accentColor }: ComparePanelProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [name, setName] = useState("Run comparison");
  const [result, setResult] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(false);

  function toggle(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 6 ? [...prev, id] : prev
    );
  }

  async function compare() {
    if (selected.length < 2) return;
    setLoading(true);
    try {
      const res = await createComparison(name, selected);
      setResult(res);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="glass rounded-xl p-5">
        <h3 className="flex items-center gap-2 text-sm font-medium">
          <GitCompare className="h-4 w-4" style={{ color: accentColor }} />
          Compare runs
        </h3>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-3 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
        <div className="mt-3 max-h-48 space-y-1 overflow-y-auto">
          {history.map((run) => (
            <label
              key={run.run_id}
              className="flex cursor-pointer items-center gap-2 rounded px-2 py-1 hover:bg-white/5"
            >
              <input
                type="checkbox"
                checked={selected.includes(run.run_id)}
                onChange={() => toggle(run.run_id)}
              />
              <span className="text-xs text-zinc-400">
                {run.run_id} — {run.model_name}
              </span>
            </label>
          ))}
        </div>
        <button
          type="button"
          onClick={compare}
          disabled={selected.length < 2 || loading}
          className="mt-4 rounded-lg px-4 py-2 text-sm font-medium text-black disabled:opacity-40"
          style={{ backgroundColor: accentColor }}
        >
          {loading ? <Loader2 className="inline h-4 w-4 animate-spin" /> : `Compare ${selected.length} runs`}
        </button>
      </div>

      {result && (
        <div className="glass rounded-xl p-5">
          <h4 className="text-sm font-medium text-zinc-300">Delta metrics</h4>
          <div className="mt-3 space-y-2 font-mono text-xs">
            {Object.entries(result.summary.delta || {}).map(([metric, d]) => (
              <div key={metric} className="flex justify-between text-zinc-400">
                <span>{metric}</span>
                <span style={{ color: accentColor }}>
                  {d.percent >= 0 ? "+" : ""}
                  {d.percent.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
