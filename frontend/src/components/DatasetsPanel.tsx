"use client";

import { useEffect, useState } from "react";
import { Database, Upload } from "lucide-react";
import { ingestDataset, listDatasets } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DatasetInfo } from "@/lib/types";

interface DatasetsPanelProps {
  domainTag?: string;
  accentColor: string;
}

export function DatasetsPanel({ domainTag, accentColor }: DatasetsPanelProps) {
  const { isAuthenticated } = useAuth();
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    listDatasets(domainTag).then(setDatasets).catch(() => setDatasets([]));
  }, [domainTag]);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !isAuthenticated) return;
    setUploading(true);
    try {
      await ingestDataset(file, file.name, domainTag);
      setDatasets(await listDatasets(domainTag));
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="glass rounded-3xl p-6">
      <h3 className="flex items-center gap-2 text-sm font-medium text-zinc-200">
        <Database className="h-4 w-4" style={{ color: accentColor }} />
        Data warehouse and evidence store
      </h3>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
        Ingest external CSV, JSON, or Parquet data alongside generated synthetic datasets.
        Synthetic outputs created by inference and MLOps runs are persisted separately with lineage IDs.
      </p>

      {isAuthenticated ? (
        <label className="mt-5 inline-flex cursor-pointer items-center gap-2 rounded-2xl border border-dashed border-border px-4 py-3 text-xs text-zinc-400 hover:border-zinc-500">
          <Upload className="h-4 w-4" />
          {uploading ? "Uploading…" : "Upload dataset"}
          <input type="file" accept=".csv,.json,.parquet" className="hidden" onChange={onUpload} />
        </label>
      ) : (
        <p className="mt-3 text-xs text-amber-500/80">Sign in to ingest datasets.</p>
      )}

      <ul className="mt-4 space-y-2">
        {datasets.map((d) => (
          <li key={d.dataset_id} className="rounded-2xl border border-white/10 bg-surface px-4 py-3 text-xs">
            <span className="font-medium text-zinc-300">{d.name}</span>
            <span className="ml-2 text-zinc-600">
              {d.row_count} rows · {d.source_type}
            </span>
          </li>
        ))}
        {datasets.length === 0 && (
          <li className="text-xs text-zinc-600">No datasets ingested yet.</li>
        )}
      </ul>
    </div>
  );
}
