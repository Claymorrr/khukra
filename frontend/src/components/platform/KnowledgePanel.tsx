"use client";

import { useEffect, useState } from "react";
import { BookOpen, FileText, Loader2, Plus } from "lucide-react";
import {
  createKnowledgeAsset,
  listDataProducts,
  listKnowledgeAssets,
  saveKnowledgeQuery,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { KnowledgeAssetInfo } from "@/lib/types";

interface KnowledgePanelProps {
  domainId: string;
  accentColor: string;
}

export function KnowledgePanel({ domainId, accentColor }: KnowledgePanelProps) {
  const { isAuthenticated } = useAuth();
  const [assets, setAssets] = useState<KnowledgeAssetInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [productId, setProductId] = useState<string>("");

  useEffect(() => {
    listDataProducts(domainId)
      .then((r) => setProductId(r.products[0]?.product_id ?? ""))
      .catch(() => setProductId(""));
  }, [domainId]);

  useEffect(() => {
    setLoading(true);
    listKnowledgeAssets(domainId, productId || undefined)
      .then(setAssets)
      .catch(() => setAssets([]))
      .finally(() => setLoading(false));
  }, [domainId, productId]);

  async function addModelCard() {
    if (!isAuthenticated) return;
    await createKnowledgeAsset({
      asset_type: "model_card",
      title: `${domainId} model card`,
      domain: domainId,
      product_id: productId || undefined,
      content: {
        summary: "Evidence-backed model card linked to data products.",
        metrics: {},
      },
    });
    setAssets(await listKnowledgeAssets(domainId, productId || undefined));
  }

  async function addSavedQuery() {
    if (!isAuthenticated) return;
    await saveKnowledgeQuery({
      name: `${domainId} exploratory query`,
      sql_text: "SELECT * FROM runs LIMIT 20",
      domain: domainId,
      product_id: productId || undefined,
    });
    await createKnowledgeAsset({
      asset_type: "saved_query_ref",
      title: "Saved analytics query",
      domain: domainId,
      product_id: productId || undefined,
      content: { sql: "SELECT * FROM runs LIMIT 20" },
    });
    setAssets(await listKnowledgeAssets(domainId, productId || undefined));
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <p className="text-xs uppercase tracking-[0.28em] text-zinc-600">Knowledge layer</p>
        <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold text-white">
          <BookOpen className="h-6 w-6" style={{ color: accentColor }} />
          Reports, queries & evidence
        </h3>
        <p className="mt-2 max-w-2xl text-sm text-zinc-500">
          Model cards, saved SQL, evaluation summaries, and reports tied to governed data products.
        </p>
        {isAuthenticated && (
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={addModelCard}
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-xs text-zinc-400 hover:bg-white/5"
            >
              <Plus className="h-3.5 w-3.5" />
              Model card
            </button>
            <button
              type="button"
              onClick={addSavedQuery}
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-xs text-zinc-400 hover:bg-white/5"
            >
              <FileText className="h-3.5 w-3.5" />
              Saved query
            </button>
          </div>
        )}
      </section>

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-zinc-600" />
        </div>
      ) : assets.length === 0 ? (
        <p className="text-sm text-zinc-600">No knowledge assets yet for this domain.</p>
      ) : (
        <ul className="grid gap-3 md:grid-cols-2">
          {assets.map((a) => (
            <li key={a.asset_id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-[10px] uppercase tracking-wider text-zinc-600">{a.asset_type}</p>
              <p className="mt-1 font-medium text-zinc-200">{a.title}</p>
              {a.product_id && (
                <p className="mt-1 font-mono text-[11px] text-zinc-600">{a.product_id}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
