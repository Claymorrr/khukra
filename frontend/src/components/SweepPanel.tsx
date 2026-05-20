"use client";

import { useState } from "react";
import { Grid3X3, Loader2 } from "lucide-react";
import { createSweep } from "@/lib/api";
import type { Selection } from "@/lib/types";

interface SweepPanelProps {
  selection: Selection;
  accentColor: string;
  onComplete: (sweepId: string) => void;
}

export function SweepPanel({ selection, accentColor, onComplete }: SweepPanelProps) {
  const [paramName, setParamName] = useState("volatility");
  const [values, setValues] = useState("0.1,0.2,0.3");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSweep() {
    setLoading(true);
    setError(null);
    try {
      const parsed = values.split(",").map((v) => {
        const n = parseFloat(v.trim());
        return Number.isNaN(n) ? v.trim() : n;
      });
      const res = await createSweep({
        domain: selection.domainId,
        subdomain: selection.subdomainId,
        model: selection.modelId,
        sweep: { [paramName]: parsed },
      });
      onComplete(res.sweep_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sweep failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="flex items-center gap-2 text-sm font-medium text-zinc-300">
        <Grid3X3 className="h-4 w-4" style={{ color: accentColor }} />
        Parameter sweep
      </h3>
      <p className="mt-1 text-xs text-zinc-500">
        Run the model across multiple values for one parameter.
      </p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <input
          value={paramName}
          onChange={(e) => setParamName(e.target.value)}
          placeholder="Parameter name"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
        <input
          value={values}
          onChange={(e) => setValues(e.target.value)}
          placeholder="Values (comma-separated)"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
      </div>
      {error && <p className="mt-2 text-xs text-red-400">{error}</p>}
      <button
        type="button"
        onClick={runSweep}
        disabled={loading}
        className="mt-4 rounded-lg px-4 py-2 text-sm font-medium text-black"
        style={{ backgroundColor: accentColor }}
      >
        {loading ? <Loader2 className="inline h-4 w-4 animate-spin" /> : "Run sweep"}
      </button>
    </div>
  );
}
