"use client";

import { useCallback, useEffect, useState } from "react";
import { Brain, Loader2, Sparkles } from "lucide-react";
import {
  getStats,
  listArtifacts,
  listEvaluations,
  platformExplain,
  platformInsights,
  type InsightCard,
} from "@/lib/api";

interface InsightsEngineeringProps {
  accentColor: string;
}

export function InsightsEngineering({ accentColor }: InsightsEngineeringProps) {
  const [cards, setCards] = useState<InsightCard[]>([]);
  const [stats, setStats] = useState<Record<string, number>>({});
  const [artifacts, setArtifacts] = useState<Array<Record<string, unknown>>>([]);
  const [evaluations, setEvaluations] = useState<Array<Record<string, unknown>>>([]);
  const [explainQ, setExplainQ] = useState("");
  const [explainAnswer, setExplainAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    platformInsights().then((r) => setCards(r.cards)).catch(() => setCards([]));
    getStats().then(setStats).catch(() => {});
    listArtifacts().then((r) => setArtifacts(r.artifacts.slice(0, 5))).catch(() => {});
    listEvaluations().then((r) => setEvaluations(r.evaluations.slice(0, 5))).catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
    setLoading(false);
  }, [refresh]);

  const handleExplain = async () => {
    if (!explainQ.trim()) return;
    setLoading(true);
    try {
      const res = await platformExplain(explainQ);
      setExplainAnswer(res.answer);
      if (res.cards.length) setCards(res.cards);
    } catch {
      setExplainAnswer("Could not generate explanation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-violet-500/10 to-transparent p-6">
        <p className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-zinc-500">
          <Brain className="h-4 w-4" style={{ color: accentColor }} />
          Insights engineering
        </p>
        <p className="mt-2 text-sm text-zinc-500">
          Warehouse health, registry status, evaluation pass rates, and one-click ML readiness explanations.
        </p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.title} className="glass rounded-2xl border border-white/10 p-5">
            <p className="text-xs uppercase text-zinc-600">{card.title}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
            <p className="mt-2 text-xs text-zinc-500">{card.detail}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <MiniStat label="Synthetic" value={stats.synthetic_datasets ?? 0} />
        <MiniStat label="Inferences" value={stats.inferences ?? stats.runs ?? 0} />
        <MiniStat label="Artifacts" value={stats.artifacts ?? 0} />
        <MiniStat label="Evaluations" value={stats.evaluations ?? 0} />
      </div>

      <section className="glass rounded-2xl p-5">
        <h4 className="text-sm font-medium text-zinc-200">Explain a dataset, run, or model</h4>
        <div className="mt-3 flex gap-2">
          <input
            value={explainQ}
            onChange={(e) => setExplainQ(e.target.value)}
            placeholder="e.g. explain latest synthetic datasets"
            className="flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-2 text-sm text-zinc-300"
          />
          <button
            type="button"
            onClick={handleExplain}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-black"
            style={{ backgroundColor: accentColor }}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Explain
          </button>
        </div>
        {explainAnswer && (
          <p className="mt-4 text-sm leading-6 text-zinc-400">{explainAnswer}</p>
        )}
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass rounded-2xl p-5">
          <h4 className="text-sm font-medium text-zinc-200">Recent artifacts</h4>
          <ul className="mt-3 space-y-2 text-xs text-zinc-500">
            {artifacts.map((a) => (
              <li key={String(a.artifact_id)} className="font-mono">
                {String(a.artifact_id)} · {String(a.stage)} · {String(a.model_id)}
              </li>
            ))}
          </ul>
        </section>
        <section className="glass rounded-2xl p-5">
          <h4 className="text-sm font-medium text-zinc-200">Recent evaluations</h4>
          <ul className="mt-3 space-y-2 text-xs text-zinc-500">
            {evaluations.map((e) => (
              <li key={String(e.evaluation_run_id)}>
                {String(e.benchmark_name)} · {e.passed ? "passed" : "failed"}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-center">
      <p className="text-xs text-zinc-600">{label}</p>
      <p className="mt-1 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}
