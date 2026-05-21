"use client";

import { useEffect, useMemo, useState } from "react";
import { Database, Loader2, Play, TerminalSquare } from "lucide-react";
import {
  getPlatformAnalyticsCatalog,
  platformAnalyticsQuery,
  type QueryCatalog,
  type QueryResult,
} from "@/lib/api";

interface AnalyticsWorkbenchProps {
  accentColor: string;
  domainId: string;
}

function domainSql(domainId: string) {
  return `SELECT dataset_id, scenario_id, domain, subdomain, model_id, file_uri, row_count
FROM synthetic_datasets
WHERE domain = '${domainId}'
ORDER BY created_at DESC
LIMIT 20`;
}

export function AnalyticsWorkbench({ accentColor, domainId }: AnalyticsWorkbenchProps) {
  const [catalog, setCatalog] = useState<QueryCatalog | null>(null);
  const [sql, setSql] = useState(() => domainSql(domainId));
  const [limit, setLimit] = useState(100);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPlatformAnalyticsCatalog().then(setCatalog).catch(() => setCatalog(null));
  }, []);

  useEffect(() => {
    setSql(domainSql(domainId));
  }, [domainId]);

  const visibleTables = useMemo(() => catalog?.tables.slice(0, 12) ?? [], [catalog]);

  async function execute() {
    setLoading(true);
    setError(null);
    try {
      setResult(await platformAnalyticsQuery(sql, limit));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.02] p-6">
        <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
          <Database className="h-4 w-4" style={{ color: accentColor }} />
          Analytics Workbench
        </p>
        <h3 className="mt-3 text-2xl font-semibold text-white">
          DuckDB & Parquet analytics
        </h3>
        <p className="mt-2 max-w-3xl text-sm text-zinc-500">
          Read-only SQL against the warehouse and generated Parquet files. Mutating statements are blocked.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        <section className="glass rounded-3xl p-5">
          <h4 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
            <TerminalSquare className="h-4 w-4" style={{ color: accentColor }} />
            SQL editor
          </h4>
          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            rows={12}
            className="mt-4 w-full rounded-xl border border-white/10 bg-black/40 p-4 font-mono text-xs text-zinc-300"
            spellCheck={false}
          />
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-xs text-zinc-500">
              Limit
              <input
                type="number"
                min={1}
                max={1000}
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-20 rounded-lg border border-white/10 bg-black/30 px-2 py-1"
              />
            </label>
            <button
              type="button"
              onClick={execute}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-black disabled:opacity-50"
              style={{ backgroundColor: accentColor }}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Run query
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
          {result && (
            <div className="mt-6 overflow-x-auto">
              <p className="mb-2 text-xs text-zinc-600">
                {result.row_count} rows · {result.duration_ms} ms · showing {result.rows.length}
              </p>
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-zinc-500">
                    {result.columns.map((c) => (
                      <th key={c} className="py-2 pr-3">
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, i) => (
                    <tr key={i} className="border-b border-white/5 text-zinc-400">
                      {result.columns.map((c) => (
                        <td key={c} className="py-2 pr-3 font-mono">
                          {String(row[c] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <aside className="space-y-4">
          <section className="glass rounded-2xl p-4">
            <h4 className="text-xs font-medium uppercase text-zinc-500">Tables</h4>
            <ul className="mt-3 space-y-2 text-xs text-zinc-500">
              {visibleTables.map((t) => (
                <li key={t.table}>
                  <button
                    type="button"
                    className="text-left hover:text-sky-400"
                    onClick={() => setSql(`SELECT * FROM "${t.table}" LIMIT 20`)}
                  >
                    {t.table} ({t.row_count})
                  </button>
                </li>
              ))}
            </ul>
          </section>
          {(
            catalog?.example_groups?.length
              ? catalog.example_groups.flatMap((g) =>
                  g.examples.map((ex) => ({ title: ex.title, sql: ex.sql, group: g.group }))
                )
              : (catalog?.examples ?? []).map((ex) => ({
                  title: ex.title,
                  sql: ex.sql,
                  group: undefined as string | undefined,
                }))
          ).map((ex) => (
            <button
              key={`${ex.group ?? ""}-${ex.title}`}
              type="button"
              onClick={() => setSql(ex.sql)}
              className="block w-full rounded-xl border border-white/10 p-3 text-left text-xs text-zinc-500 hover:border-sky-500/30"
            >
              {ex.group ? (
                <span className="block text-[10px] uppercase text-zinc-700">{ex.group}</span>
              ) : null}
              {ex.title}
            </button>
          ))}
        </aside>
      </div>
    </div>
  );
}
