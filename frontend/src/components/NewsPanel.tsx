"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Newspaper, RefreshCw } from "lucide-react";
import { RssPipelineDiagram } from "@/components/RssPipelineDiagram";
import { getNewsStatus, refreshNews, type NewsStatus } from "@/lib/api/disruption";

export function NewsPanel({ onRefreshed }: { onRefreshed?: () => void }) {
  const [news, setNews] = useState<NewsStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastLatencyMs, setLastLatencyMs] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setNews(await getNewsStatus());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load news");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const poll = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const result = await refreshNews();
      setLastLatencyMs(result.latency_ms ?? null);
      await load();
      onRefreshed?.();
      if (result.errors?.length) {
        setError(
          `${result.entries_new} retained · ${result.entries_rejected ?? 0} filtered · ${result.errors.length} feed error(s)`,
        );
      } else if (result.entries_rejected) {
        setError(
          `${result.entries_new} retained · ${result.entries_rejected} filtered as off-objective`,
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "News refresh failed");
    } finally {
      setRefreshing(false);
    }
  }, [load, onRefreshed]);

  return (
    <section className="rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.04] p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="flex items-center gap-2 text-sm font-medium text-cyan-100">
            <Newspaper className="h-4 w-4" />
            News intelligence (RSS)
          </p>
          <p className="mt-1 text-xs text-zinc-500">
            Polls RSS → objective judgment → VADER NLP →{" "}
            <code className="text-zinc-400">news_stress</code> +{" "}
            <code className="text-zinc-400">news_sentiment</code>.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void poll()}
          disabled={refreshing}
          className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs text-cyan-100 disabled:opacity-50"
        >
          {refreshing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          Poll RSS feeds
        </button>
      </div>

      {error && <p className="mt-3 text-xs text-amber-300/90">{error}</p>}

      <RssPipelineDiagram news={news} lastLatencyMs={lastLatencyMs} />

      {loading ? (
        <p className="mt-4 text-xs text-zinc-500">Loading news cache…</p>
      ) : news ? (
        <div className="mt-4 space-y-3">
          <p className="text-[11px] text-zinc-500">
            {news.objective ? `${news.objective} · ` : ""}
            {news.headlines_total} retained · {news.stress_headlines} impact-scored
            {news.negative_headlines != null ? ` · ${news.negative_headlines} NLP-negative` : ""} ·{" "}
            {news.first_date && news.last_date ? `${news.first_date} → ${news.last_date}` : "no series yet"}
          </p>
          <ul className="max-h-48 space-y-2 overflow-y-auto">
            {news.recent_headlines.length === 0 ? (
              <li className="text-xs text-zinc-600">No headlines yet — click Poll RSS feeds.</li>
            ) : (
              news.recent_headlines.map((h) => (
                <li key={h.link} className="rounded-lg border border-white/5 bg-black/20 px-3 py-2 text-xs">
                  <a
                    href={h.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-zinc-200 hover:text-cyan-200"
                  >
                    {h.title}
                  </a>
                  <p className="mt-1 text-[10px] text-zinc-600">
                    {h.feed_id} · {h.published_at.slice(0, 10)}
                    {h.judgment_tier && (
                      <span className="ml-2 text-violet-400/80">{h.judgment_tier}</span>
                    )}
                    {(h.impact_score ?? h.stress_score) > 0 && (
                      <span className="ml-2 text-cyan-400/80">
                        impact {h.impact_score ?? h.stress_score}
                        {h.sentiment_compound != null && (
                          <span className="text-fuchsia-400/80">
                            {" "}
                            · sentiment {h.sentiment_compound.toFixed(2)}
                          </span>
                        )}
                        {h.matched_keywords ? ` · ${h.matched_keywords}` : ""}
                      </span>
                    )}
                  </p>
                  {h.judgment_rationale && (
                    <p className="mt-1 text-[10px] italic text-zinc-600">{h.judgment_rationale}</p>
                  )}
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
