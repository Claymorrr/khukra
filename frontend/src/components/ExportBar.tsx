"use client";

import { Download, FileText } from "lucide-react";
import { exportUrl } from "@/lib/api";

interface ExportBarProps {
  runId?: string;
  runIds?: string[];
  comparisonId?: string;
  accentColor: string;
}

export function ExportBar({ runId, runIds, comparisonId, accentColor }: ExportBarProps) {
  const ids = runIds?.join(",") ?? runId;

  return (
    <div className="flex flex-wrap gap-2">
      {ids && (
        <a
          href={exportUrl(`/export/runs.csv?run_ids=${ids}`)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/5"
        >
          <Download className="h-3.5 w-3.5" style={{ color: accentColor }} />
          Export metrics CSV
        </a>
      )}
      {runId && (
        <a
          href={exportUrl(`/export/runs/${runId}/series.csv`)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/5"
        >
          <Download className="h-3.5 w-3.5" />
          Export series CSV
        </a>
      )}
      {comparisonId && (
        <a
          href={exportUrl(`/export/comparisons/${comparisonId}.csv`)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/5"
        >
          <Download className="h-3.5 w-3.5" />
          Export comparison CSV
        </a>
      )}
      {ids && (
        <a
          href={exportUrl(
            `/export/report.pdf?title=khukra Report&run_ids=${ids}${comparisonId ? `&comparison_id=${comparisonId}` : ""}`
          )}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/5"
        >
          <FileText className="h-3.5 w-3.5" style={{ color: accentColor }} />
          Export PDF report
        </a>
      )}
    </div>
  );
}
