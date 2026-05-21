"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { getStoredToken } from "@/lib/auth";
import { v1ListProducts } from "@/lib/api/v1";
import type { DataProductInfo } from "@/lib/types";

interface DataOpsPanelProps {
  domainId: string;
  accentColor: string;
}

interface ContractRow {
  contract_id: string;
  name: string;
  domain?: string;
  version?: string;
}

async function governanceFetch<T>(path: string): Promise<T> {
  const token = getStoredToken();
  const res = await fetch(`/api/v1/governance${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export function DataOpsPanel({ domainId, accentColor }: DataOpsPanelProps) {
  const [products, setProducts] = useState<DataProductInfo[]>([]);
  const [contracts, setContracts] = useState<ContractRow[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [prodRes, contractRes] = await Promise.all([
        v1ListProducts(domainId),
        governanceFetch<{ contracts: ContractRow[] }>(
          `/contracts?domain=${encodeURIComponent(domainId)}`
        ),
      ]);
      setProducts(prodRes.products);
      setContracts(contractRes.contracts);
    } catch {
      setProducts([]);
      setContracts([]);
    } finally {
      setLoading(false);
    }
  }, [domainId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const passed = products.filter((p) => p.quality_status === "passed").length;
  const linked = products.filter((p) => p.lineage_status === "linked" || p.lineage_status === "registered").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-6 w-6" style={{ color: accentColor }} />
        <div>
          <h2 className="text-lg font-semibold">DataOps</h2>
          <p className="text-sm text-zinc-500">
            Contracts, quality gates, freshness, and promotion readiness for {domainId}.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-zinc-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading DataOps signals…
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <MetricCard label="Products" value={products.length} accent={accentColor} />
            <MetricCard label="Quality passed" value={passed} accent={accentColor} ok={passed > 0} />
            <MetricCard label="Lineage linked" value={linked} accent={accentColor} ok={linked > 0} />
          </div>

          <section className="rounded-2xl border border-white/10 bg-white/[0.02] p-4">
            <h3 className="text-sm font-medium text-zinc-300">Data contracts</h3>
            {contracts.length === 0 ? (
              <p className="mt-2 text-xs text-zinc-600">No contracts registered for this domain yet.</p>
            ) : (
              <ul className="mt-3 space-y-2">
                {contracts.map((c) => (
                  <li
                    key={c.contract_id}
                    className="flex items-center justify-between rounded-lg border border-white/5 px-3 py-2 text-xs"
                  >
                    <span>{c.name}</span>
                    <span className="font-mono text-zinc-600">{c.version ?? "1.0"}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="rounded-2xl border border-white/10 bg-white/[0.02] p-4">
            <h3 className="text-sm font-medium text-zinc-300">Product readiness</h3>
            <ul className="mt-3 space-y-2">
              {products.slice(0, 12).map((p) => (
                <li
                  key={p.product_id}
                  className="flex items-center gap-2 rounded-lg border border-white/5 px-3 py-2 text-xs"
                >
                  {p.quality_status === "passed" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <AlertCircle className="h-3.5 w-3.5 text-amber-500" />
                  )}
                  <span className="flex-1 truncate">{p.name}</span>
                  <span className="text-zinc-600">{p.quality_status}</span>
                  <span className="font-mono text-zinc-600">{p.version_label}</span>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  accent,
  ok,
}: {
  label: string;
  value: number;
  accent: string;
  ok?: boolean;
}) {
  return (
    <div
      className="rounded-2xl border border-white/10 p-4"
      style={{ boxShadow: ok ? `inset 0 0 0 1px ${accent}33` : undefined }}
    >
      <p className="text-xs uppercase tracking-wider text-zinc-600">{label}</p>
      <p className="mt-1 text-2xl font-semibold" style={{ color: accent }}>
        {value}
      </p>
    </div>
  );
}
