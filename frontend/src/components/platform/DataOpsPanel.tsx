"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { getStoredToken } from "@/lib/auth";
import { v1GetDomainLake, v1ListLakeAssets } from "@/lib/api/v1";
import type { LakeAssetInfo } from "@/lib/types";

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
  const [assets, setAssets] = useState<LakeAssetInfo[]>([]);
  const [contracts, setContracts] = useState<ContractRow[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [lakeRes, researchRes, contractRes] = await Promise.all([
        v1GetDomainLake(domainId),
        v1ListLakeAssets(domainId, "research"),
        governanceFetch<{ contracts: ContractRow[] }>(
          `/contracts?domain=${encodeURIComponent(domainId)}`
        ),
      ]);
      const devRes = await v1ListLakeAssets(domainId, "development");
      setAssets([...researchRes.assets, ...devRes.assets]);
      setContracts(contractRes.contracts);
      void lakeRes;
    } catch {
      setAssets([]);
      setContracts([]);
    } finally {
      setLoading(false);
    }
  }, [domainId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const passed = assets.filter((p) => p.quality_status === "passed").length;
  const linked = assets.filter((p) => p.lineage_status === "linked" || p.lineage_status === "registered").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-6 w-6" style={{ color: accentColor }} />
        <div>
          <h2 className="text-lg font-semibold">DataOps</h2>
          <p className="text-sm text-zinc-500">
            Lake governance: contracts, quality, freshness, and readiness for {domainId}.
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
            <MetricCard label="Lake assets" value={assets.length} accent={accentColor} />
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
            <h3 className="text-sm font-medium text-zinc-300">Lake readiness</h3>
            <ul className="mt-3 space-y-2">
              {assets.slice(0, 12).map((p) => (
                <li
                  key={p.lake_asset_id}
                  className="flex items-center gap-2 rounded-lg border border-white/5 px-3 py-2 text-xs"
                >
                  {p.quality_status === "passed" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <AlertCircle className="h-3.5 w-3.5 text-amber-500" />
                  )}
                  <span className="flex-1 truncate">{p.name}</span>
                  <span className="text-zinc-600">{p.lake_space}</span>
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
