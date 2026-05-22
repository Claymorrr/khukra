"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Database,
  GitBranch,
  Layers,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import { getDataProduct, listDataProducts, syncDataProducts } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DataProductDetail, DataProductInfo } from "@/lib/types";
import { LineagePanel } from "../LineagePanel";
import { DatasetsPanel } from "../DatasetsPanel";

interface DataHubProps {
  domainId: string;
  accentColor: string;
}

export function DataHub({ domainId, accentColor }: DataHubProps) {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState<DataProductInfo[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<DataProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listDataProducts(domainId);
      setProducts(res.products);
      if (!selectedId && res.products.length > 0) {
        setSelectedId(res.products[0].product_id);
      }
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [domainId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    setDetailLoading(true);
    getDataProduct(selectedId)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  async function handleSync() {
    setSyncing(true);
    try {
      await syncDataProducts();
      await refresh();
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.06] to-transparent p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">Domain data plane</p>
            <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold text-white">
              <Layers className="h-6 w-6" style={{ color: accentColor }} />
              Data Hub
            </h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
              Governed catalog of ingested files, synthetic datasets, and solver outputs - schema, contracts, versions,
              lineage, and preview in one place. Domains filter products; products are the system of record.
            </p>
          </div>
          <button
            type="button"
            onClick={handleSync}
            disabled={syncing}
            className="rounded-xl border border-white/10 px-4 py-2 text-xs text-zinc-400 hover:bg-white/5"
          >
            {syncing ? "Syncing…" : "Sync warehouse → products"}
          </button>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-600">Products in domain</p>
          {loading && (
            <div className="flex justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-zinc-600" />
            </div>
          )}
          {!loading && products.length === 0 && (
            <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-zinc-600">
              No data products yet. Ingest a file or run data generation, then sync.
            </p>
          )}
          <ul className="space-y-2">
            {products.map((p) => (
              <li key={p.product_id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(p.product_id)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition ${
                    selectedId === p.product_id
                      ? "border-white/20 bg-white/10 text-white"
                      : "border-white/10 bg-white/[0.02] text-zinc-400 hover:bg-white/5"
                  }`}
                >
                  <span className="font-medium">{p.name}</span>
                  <span className="mt-1 flex flex-wrap gap-2 text-[11px] text-zinc-600">
                    <span>{p.kind}</span>
                    <span>v{p.version_label}</span>
                    <QualityBadge status={p.quality_status} />
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-4">
          {detailLoading && (
            <div className="flex justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-zinc-600" />
            </div>
          )}
          {detail && !detailLoading && (
            <>
              <ProductDetailCard product={detail} accentColor={accentColor} />
              {detail.preview && (
                <section className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-zinc-600">Preview</p>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="text-zinc-500">
                          {detail.preview.columns.map((c) => (
                            <th key={c} className="px-2 py-1 font-medium">
                              {c}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {detail.preview.rows.slice(0, 8).map((row, i) => (
                          <tr key={i} className="border-t border-white/5 text-zinc-400">
                            {detail.preview!.columns.map((c) => (
                              <td key={c} className="px-2 py-1">
                                {String((row as Record<string, unknown>)[c] ?? "")}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              )}
              <LineagePanel entityId={detail.product_id} accentColor={accentColor} />
            </>
          )}
        </div>
      </div>

      <DatasetsPanel domainTag={domainId} accentColor={accentColor} />
    </div>
  );
}

function QualityBadge({ status }: { status: string }) {
  const tone =
    status === "passed"
      ? "text-emerald-400"
      : status === "failed"
        ? "text-red-400"
        : "text-zinc-500";
  return (
    <span className={`inline-flex items-center gap-1 ${tone}`}>
      <ShieldCheck className="h-3 w-3" />
      {status}
    </span>
  );
}

function ProductDetailCard({
  product,
  accentColor,
}: {
  product: DataProductDetail;
  accentColor: string;
}) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-start gap-3">
        <Database className="h-5 w-5 shrink-0" style={{ color: accentColor }} />
        <div className="min-w-0 flex-1">
          <h4 className="text-lg font-semibold text-white">{product.name}</h4>
          <p className="mt-1 font-mono text-xs text-zinc-500">{product.product_id}</p>
        </div>
      </div>
      <dl className="mt-4 grid gap-2 text-xs sm:grid-cols-2">
        <Stat label="Kind" value={product.kind} />
        <Stat label="Version" value={product.version_label} />
        <Stat label="Rows" value={String(product.row_count ?? "—")} />
        <Stat label="Quality" value={product.quality_status} />
        <Stat label="Lineage" value={product.lineage_status} />
        <Stat label="Source" value={`${product.source_type}:${product.source_id}`} />
      </dl>
      {Object.keys(product.column_schema).length > 0 && (
        <div className="mt-4">
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-600">Schema</p>
          <pre className="mt-2 max-h-32 overflow-auto rounded-xl bg-black/30 p-3 font-mono text-[11px] text-zinc-400">
            {JSON.stringify(product.column_schema, null, 2)}
          </pre>
        </div>
      )}
      {product.versions.length > 0 && (
        <div className="mt-4">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-zinc-600">
            <GitBranch className="h-3.5 w-3.5" />
            Versions ({product.versions.length})
          </p>
          <ul className="mt-2 space-y-1 text-xs text-zinc-500">
            {product.versions.slice(0, 5).map((v) => (
              <li key={String(v.version_id)}>
                {String(v.version_label)} · {String(v.status)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-zinc-600">{label}</dt>
      <dd className="text-zinc-300">{value}</dd>
    </div>
  );
}
