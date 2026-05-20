"use client";

import { useEffect, useMemo, useState } from "react";
import { Database, Loader2, Play, Rows3, TableProperties, TerminalSquare } from "lucide-react";
import { getQueryCatalog, runDuckDBQuery, type QueryCatalog, type QueryResult } from "@/lib/api";

interface QueryPanelProps {
  accentColor: string;
}

const DEFAULT_SQL = `SELECT dataset_id, scenario_id, domain, subdomain, model_id, file_uri, row_count
FROM synthetic_datasets
ORDER BY created_at DESC
LIMIT 20`;

export function QueryPanel({ accentColor }: QueryPanelProps) {
  const [catalog, setCatalog] = useState<QueryCatalog | null>(null);
  const [sql, setSql] = useState(DEFAULT_SQL);
  const [limit, setLimit] = useState(100);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getQueryCatalog().then(setCatalog).catch(() => setCatalog(null));
  }, []);

  const visibleTables = useMemo(() => catalog?.tables.slice(0, 12) ?? [], [catalog]);

  async function execute() {
    setLoading(true);
    setError(null);
    try {
      setResult(await runDuckDBQuery(sql, limit));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.02] p-6">
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-20 blur-3xl"
          style={{ backgroundColor: accentColor }}
        />
        <div className="relative">
          <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
            <Database className="h-4 w-4" style={{ color: accentColor }} />
            DuckDB SQL workspace
          </p>
          <h3 className="mt-3 text-2xl font-semibold tracking-tight text-white">
            Query your warehouse and generated Parquet data
          </h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-500">
            Run read-only SQL against `data/warehouse/khukra.duckdb`, inspect synthetic datasets,
            inference events, lineage, artifacts, and read generated Parquet files with DuckDB.
          </p>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <section className="glass rounded-3xl p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h4 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
                <TerminalSquare className="h-4 w-4" style={{ color: accentColor }} />
                SQL editor
              </h4>
              <p className="mt-1 text-xs text-zinc-600">
                Allowed: SELECT, WITH, SHOW, DESCRIBE, EXPLAIN. Mutating statements are blocked.
              </p>
            </div>
            <label className="flex items-center gap-2 text-xs text-zinc-500">
              Limit
              <input
                type="number"
                min={1}
                max={1000}
                value={limit}
                onChange={(e) => setLimit(Math.max(1, Math.min(1000, Number(e.target.value) || 100)))}
                className="w-24 rounded-xl border border-border bg-black/20 px-3 py-2 font-mono text-xs text-white outline-none"
              />
            </label>
          </div>

          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            spellCheck={false}
            className="min-h-[220px] w-full resize-y rounded-2xl border border-border bg-[#070a0d] p-4 font-mono text-sm leading-6 text-zinc-200 outline-none transition focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]"
            style={{ ["--accent" as string]: accentColor }}
          />

          {error && (
            <div className="mt-3 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={execute}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-black disabled:opacity-50"
              style={{ backgroundColor: accentColor }}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
              Run query
            </button>
            {result && (
              <span className="text-xs text-zinc-500">
                {result.row_count} rows · showing {result.rows.length} · {result.duration_ms} ms
              </span>
            )}
          </div>
        </section>

        <aside className="space-y-4">
          <section className="glass rounded-3xl p-5">
            <h4 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
              <TableProperties className="h-4 w-4" style={{ color: accentColor }} />
              Warehouse tables
            </h4>
            <div className="mt-4 max-h-[320px] space-y-2 overflow-y-auto pr-1">
              {visibleTables.map((table) => (
                <button
                  key={table.table}
                  type="button"
                  onClick={() => setSql(`SELECT * FROM ${table.table} LIMIT 50`)}
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-3 py-3 text-left transition hover:border-white/20 hover:bg-white/[0.04]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono text-xs text-zinc-300">{table.table}</span>
                    <span className="text-[10px] text-zinc-600">{table.row_count} rows</span>
                  </div>
                  <p className="mt-1 truncate text-[11px] text-zinc-600">
                    {table.columns.slice(0, 4).map((c) => c.name).join(", ")}
                    {table.columns.length > 4 ? "..." : ""}
                  </p>
                </button>
              ))}
            </div>
          </section>

          <section className="glass rounded-3xl p-5">
            <h4 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
              <Rows3 className="h-4 w-4" style={{ color: accentColor }} />
              Example queries
            </h4>
            <div className="mt-4 space-y-2">
              {catalog?.examples.map((example) => (
                <button
                  key={example.title}
                  type="button"
                  onClick={() => setSql(example.sql)}
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-3 py-3 text-left text-xs text-zinc-400 transition hover:border-white/20 hover:text-zinc-200"
                >
                  {example.title}
                </button>
              ))}
            </div>
          </section>
        </aside>
      </div>

      {result && <QueryResults result={result} accentColor={accentColor} />}
    </div>
  );
}

function QueryResults({ result, accentColor }: { result: QueryResult; accentColor: string }) {
  return (
    <section className="glass rounded-3xl p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h4 className="text-sm font-medium text-zinc-200">Result set</h4>
        <p className="text-xs text-zinc-500">
          {result.columns.length} columns · {result.rows.length} displayed
        </p>
      </div>
      <div className="overflow-auto rounded-2xl border border-white/10">
        <table className="min-w-full border-collapse text-left text-xs">
          <thead className="sticky top-0 bg-surface-overlay">
            <tr>
              {result.columns.map((column) => (
                <th
                  key={column}
                  className="border-b border-border px-3 py-2 font-medium uppercase tracking-wide text-zinc-500"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, idx) => (
              <tr key={idx} className="odd:bg-black/20 hover:bg-white/[0.03]">
                {result.columns.map((column) => (
                  <td key={column} className="max-w-[280px] truncate border-b border-white/5 px-3 py-2 font-mono text-zinc-400">
                    {formatCell(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full"
          style={{
            width: `${Math.min(100, (result.rows.length / Math.max(result.row_count, 1)) * 100)}%`,
            backgroundColor: accentColor,
          }}
        />
      </div>
    </section>
  );
}

function formatCell(value: unknown): string {
  if (value == null) return "null";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
