"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Beaker,
  Briefcase,
  Database,
  GitBranch,
  Layers,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import {
  v1GetDomainLake,
  v1GetLakeAsset,
  v1ListLakeAssets,
  v1SyncDomainLake,
} from "@/lib/api/v1";
import type { DomainLakeDetail, DomainLakeSummary, LakeAssetInfo } from "@/lib/types";
import { LineagePanel } from "../LineagePanel";
import { DatasetsPanel } from "../DatasetsPanel";

type LakeTab = "research" | "development";

interface DomainLakePanelProps {
  domainId: string;
  accentColor: string;
}

export function DomainLakePanel({ domainId, accentColor }: DomainLakePanelProps) {
  const [tab, setTab] = useState<LakeTab>("research");
  const [summary, setSummary] = useState<DomainLakeSummary | null>(null);
  const [assets, setAssets] = useState<LakeAssetInfo[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<DomainLakeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [sum, list] = await Promise.all([
        v1GetDomainLake(domainId),
        v1ListLakeAssets(domainId, tab),
      ]);
      setSummary(sum);
      setAssets(list.assets);
      if (!selectedId && list.assets.length > 0) {
        setSelectedId(list.assets[0].lake_asset_id);
      }
    } catch {
      setSummary(null);
      setAssets([]);
    } finally {
      setLoading(false);
    }
  }, [domainId, tab]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    setDetailLoading(true);
    v1GetLakeAsset(domainId, selectedId)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  }, [domainId, selectedId]);

  async function handleSync() {
    setSyncing(true);
    try {
      await v1SyncDomainLake(domainId);
      await refresh();
    } finally {
      setSyncing(false);
    }
  }

  const tabLabel = tab === "research" ? "Research Lake" : "Product Development Lake";
  const TabIcon = tab === "research" ? Beaker : Briefcase;
  const isPhysical = domainId === "physical";

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.06] to-transparent p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">
              Domain knowledge &amp; development lake
            </p>
            <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold text-white">
              <Layers className="h-6 w-6" style={{ color: accentColor }} />
              {domainId} workspace lake
            </h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
              {isPhysical
                ? "Simulation traces, parameter sweeps, validation evidence, and solver artifacts stored and governed per domain."
                : "Research data, experiments, and product development artifacts stored and governed per domain - versions, lineage, contracts, and knowledge in one lake."}
            </p>
            {summary && (
              <p className="mt-2 text-xs text-zinc-600">
                {summary.totals.lake_assets} lake assets · {summary.totals.research_artifacts}{" "}
                research notes · {summary.totals.development_artifacts} development records
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={handleSync}
            disabled={syncing}
            className="rounded-xl border border-white/10 px-4 py-2 text-xs text-zinc-400 hover:bg-white/5"
          >
            {syncing ? "Syncing…" : "Sync warehouse → lake"}
          </button>
        </div>
        <div className="mt-4 flex gap-2">
          {(["research", "development"] as LakeTab[]).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => {
                setTab(t);
                setSelectedId(null);
              }}
              className={`rounded-xl px-4 py-2 text-xs ${
                tab === t ? "bg-white/10 text-white" : "text-zinc-500 hover:bg-white/5"
              }`}
            >
              {t === "research" ? "Research Lake" : "Product Development"}
            </button>
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <div className="space-y-3">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-zinc-600">
            <TabIcon className="h-3.5 w-3.5" />
            {tabLabel}
          </p>
          {loading && (
            <div className="flex justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-zinc-600" />
            </div>
          )}
          {!loading && assets.length === 0 && (
            <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-zinc-600">
              No assets in this lake space yet. Ingest data, run generation, or sync the warehouse.
            </p>
          )}
          <ul className="space-y-2">
            {assets.map((a) => (
              <li key={a.lake_asset_id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(a.lake_asset_id)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition ${
                    selectedId === a.lake_asset_id
                      ? "border-white/20 bg-white/10 text-white"
                      : "border-white/10 bg-white/[0.02] text-zinc-400 hover:bg-white/5"
                  }`}
                >
                  <span className="font-medium">{a.name}</span>
                  <span className="mt-1 flex flex-wrap gap-2 text-[11px] text-zinc-600">
                    <span>{a.asset_kind}</span>
                    <span>v{a.version_label}</span>
                    <QualityBadge status={a.quality_status} />
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
              <LakeAssetDetailCard asset={detail} accentColor={accentColor} />
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
              <LineagePanel entityId={detail.lake_asset_id} accentColor={accentColor} />
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

function LakeAssetDetailCard({
  asset,
  accentColor,
}: {
  asset: DomainLakeDetail;
  accentColor: string;
}) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-start gap-3">
        <Database className="h-5 w-5 shrink-0" style={{ color: accentColor }} />
        <div className="min-w-0 flex-1">
          <h4 className="text-lg font-semibold text-white">{asset.name}</h4>
          <p className="mt-1 font-mono text-xs text-zinc-500">{asset.lake_asset_id}</p>
          <p className="mt-1 text-xs text-zinc-600 capitalize">{asset.lake_space} · {asset.asset_kind}</p>
        </div>
      </div>
      <dl className="mt-4 grid gap-2 text-xs sm:grid-cols-2">
        <Stat label="Version" value={asset.version_label} />
        <Stat label="Rows" value={String(asset.row_count ?? "—")} />
        <Stat label="Quality" value={asset.quality_status} />
        <Stat label="Lineage" value={asset.lineage_status} />
        <Stat label="Source" value={`${asset.source_type}:${asset.source_id}`} />
      </dl>
      {asset.versions.length > 0 && (
        <div className="mt-4">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-zinc-600">
            <GitBranch className="h-3.5 w-3.5" />
            Versions ({asset.versions.length})
          </p>
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
