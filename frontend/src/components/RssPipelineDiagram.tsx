"use client";

import { useState } from "react";
import {
  ArrowRight,
  BarChart3,
  Database,
  GitMerge,
  Filter,
  Newspaper,
  Rss,
  Search,
  Sparkles,
  Tags,
  Brain,
} from "lucide-react";
import type { NewsStatus } from "@/lib/api/disruption";

const STAGES = [
  {
    id: "feeds",
    label: "RSS sources",
    detail: "BBC · FreightWaves · Supply Chain Dive · Reuters · Al Jazeera",
    icon: Rss,
    color: "#22d3ee",
  },
  {
    id: "fetch",
    label: "Fetch & parse",
    detail: "Pull latest items from each feed (~2s round-trip)",
    icon: Newspaper,
    color: "#38bdf8",
  },
  {
    id: "judge",
    label: "Objective judgment",
    detail: "Keep logistics/shock/trade stories · drop sports & noise",
    icon: Filter,
    color: "#34d399",
  },
  {
    id: "cache",
    label: "Retained cache",
    detail: "Only objective-aligned headlines · headlines.parquet",
    icon: Database,
    color: "#818cf8",
  },
  {
    id: "nlp",
    label: "VADER NLP",
    detail: "Sentiment compound on title + summary; negative tone boosts impact",
    icon: Brain,
    color: "#f472b6",
  },
  {
    id: "score",
    label: "Impact scoring",
    detail: "judgment × tone → news_stress + daily news_sentiment",
    icon: Tags,
    color: "#a78bfa",
  },
  {
    id: "signal",
    label: "News signals",
    detail: "news_stress + news_sentiment parquet series",
    icon: Sparkles,
    color: "#e879f9",
  },
  {
    id: "panel",
    label: "Panel merge",
    detail: "Align with VIX, oil, FX, shipping on calendar",
    icon: GitMerge,
    color: "#fb923c",
  },
  {
    id: "insights",
    label: "Insights & charts",
    detail: "Discover narratives · Explore 7 methods · composite z",
    icon: Search,
    color: "#fbbf24",
  },
] as const;

interface RssPipelineDiagramProps {
  news: NewsStatus | null;
  lastLatencyMs?: number | null;
}

export function RssPipelineDiagram({ news, lastLatencyMs }: RssPipelineDiagramProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="mt-4 rounded-xl border border-cyan-500/15 bg-black/30">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-cyan-200/90">
          <BarChart3 className="h-3.5 w-3.5" />
          RSS pipeline
        </span>
        <span className="text-[10px] text-zinc-600">{expanded ? "Hide" : "Show"} flow</span>
      </button>

      {expanded && (
        <div className="border-t border-cyan-500/10 px-4 pb-4 pt-3">
          {/* Desktop: horizontal flow */}
          <div className="hidden overflow-x-auto lg:block">
            <div className="flex min-w-max items-stretch gap-1 py-2">
              {STAGES.map((stage, i) => {
                const Icon = stage.icon;
                return (
                  <div key={stage.id} className="flex items-center">
                    <StageCard stage={stage} stats={stageStats(stage.id, news, lastLatencyMs)} />
                    {i < STAGES.length - 1 && (
                      <ArrowRight className="mx-1 h-4 w-4 shrink-0 text-cyan-500/40" aria-hidden />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mobile: vertical flow */}
          <div className="space-y-2 lg:hidden">
            {STAGES.map((stage, i) => (
              <div key={stage.id} className="flex flex-col items-center">
                <StageCard stage={stage} stats={stageStats(stage.id, news, lastLatencyMs)} fullWidth />
                {i < STAGES.length - 1 && (
                  <div className="my-1 h-4 w-px bg-gradient-to-b from-cyan-500/50 to-transparent" />
                )}
              </div>
            ))}
          </div>

          {news && (
            <div className="mt-3 flex flex-wrap gap-2 border-t border-white/5 pt-3">
              {news.feeds.map((f) => (
                <span
                  key={f.feed_id}
                  className="rounded-md border border-cyan-500/20 bg-cyan-500/5 px-2 py-1 text-[10px] text-cyan-100/80"
                >
                  {f.label}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StageCard({
  stage,
  stats,
  fullWidth,
}: {
  stage: (typeof STAGES)[number];
  stats?: string;
  fullWidth?: boolean;
}) {
  const Icon = stage.icon;
  return (
    <div
      className={`rounded-lg border border-white/10 bg-gradient-to-b from-white/[0.06] to-black/40 p-3 ${
        fullWidth ? "w-full" : "w-[148px]"
      }`}
      style={{ boxShadow: `0 0 0 1px ${stage.color}12` }}
    >
      <div className="flex items-center gap-2">
        <div
          className="flex h-7 w-7 items-center justify-center rounded-md"
          style={{ background: `${stage.color}22`, color: stage.color }}
        >
          <Icon className="h-3.5 w-3.5" />
        </div>
        <p className="text-[11px] font-semibold text-zinc-100">{stage.label}</p>
      </div>
      <p className="mt-2 text-[10px] leading-4 text-zinc-500">{stage.detail}</p>
      {stats && (
        <p className="mt-2 font-mono text-[10px]" style={{ color: stage.color }}>
          {stats}
        </p>
      )}
    </div>
  );
}

function stageStats(
  stageId: string,
  news: NewsStatus | null,
  lastLatencyMs?: number | null,
): string | undefined {
  if (!news) return undefined;
  switch (stageId) {
    case "feeds":
      return `${news.feeds.length} feeds`;
    case "fetch":
      return lastLatencyMs ? `${lastLatencyMs}ms` : undefined;
    case "judge":
      return news.stress_headlines ? `${news.stress_headlines} retained` : "filters noise";
    case "cache":
      return `${news.headlines_total} kept`;
    case "nlp":
      return news.negative_headlines != null ? `${news.negative_headlines} negative` : "VADER";
    case "score":
      return `${news.stress_headlines} scored`;
    case "signal":
      return news.sentiment_last_date
        ? `stress + sentiment → ${news.sentiment_last_date}`
        : "2 signals";
    case "panel":
      return "merged on Discover";
    case "insights":
      return "news_spike · theme · headline";
    default:
      return undefined;
  }
}
