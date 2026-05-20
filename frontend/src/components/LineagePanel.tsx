"use client";

import { useEffect, useState } from "react";
import { GitBranch } from "lucide-react";
import { getLineage } from "@/lib/api";

interface LineagePanelProps {
  entityId: string | null;
  accentColor: string;
}

export function LineagePanel({ entityId, accentColor }: LineagePanelProps) {
  const [edges, setEdges] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    if (!entityId) {
      setEdges([]);
      return;
    }
    getLineage(entityId)
      .then((r) => setEdges(r.edges))
      .catch(() => setEdges([]));
  }, [entityId]);

  if (!entityId) {
    return (
      <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.02] px-6 py-16 text-center">
        <GitBranch className="mx-auto h-8 w-8 text-zinc-700" />
        <p className="mt-4 text-sm text-zinc-500">Run an inference or MLOps pipeline to view lineage.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <section className="glass rounded-3xl p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-zinc-600">Provenance graph</p>
        <h3 className="mt-2 text-2xl font-semibold text-white">Lineage evidence</h3>
        <p className="mt-2 text-sm leading-6 text-zinc-500">
          Entity <span className="font-mono text-zinc-400">{entityId}</span> is connected to synthetic
          scenarios, datasets, inference events, artifacts, and evaluation records when available.
        </p>
      </section>
      {edges.length === 0 ? (
        <p className="rounded-2xl border border-white/10 bg-black/20 p-5 text-sm text-zinc-600">
          No lineage edges recorded yet.
        </p>
      ) : (
        <ul className="grid gap-3 lg:grid-cols-2">
          {edges.map((e) => (
            <li
              key={String(e.edge_id)}
              className="glass rounded-2xl px-4 py-4 text-sm"
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <GitBranch className="h-4 w-4 shrink-0" style={{ color: accentColor }} />
                <span className="rounded-full bg-white/5 px-2 py-1 text-xs text-zinc-500">{String(e.relation)}</span>
              </div>
              <div className="space-y-2 font-mono text-xs">
                <Entity label={String(e.source_type)} value={String(e.source_id)} />
                <Entity label={String(e.target_type)} value={String(e.target_id)} strong />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Entity({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="rounded-xl bg-black/20 px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-zinc-700">{label}</p>
      <p className={strong ? "truncate text-zinc-300" : "truncate text-zinc-500"}>{value}</p>
    </div>
  );
}
