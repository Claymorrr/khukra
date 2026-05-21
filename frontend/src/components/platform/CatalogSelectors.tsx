"use client";

import type { CatalogResponse, Selection } from "@/lib/types";
import { catalogSelectors } from "@/hooks/useCatalogSelection";

interface CatalogSelectorsProps {
  catalog: CatalogResponse;
  selection: Selection;
  onSelectionChange: (s: Selection) => void;
  lockDomain?: string;
}

export function CatalogSelectors({
  catalog,
  selection,
  onSelectionChange,
  lockDomain,
}: CatalogSelectorsProps) {
  const visibleDomains = lockDomain
    ? catalog.domains.filter((d) => d.id === lockDomain)
    : catalog.domains;
  const scopedCatalog = { ...catalog, domains: visibleDomains };
  const { domain, subdomain } = catalogSelectors(scopedCatalog, selection, onSelectionChange);

  return (
    <div className={`grid gap-3 ${lockDomain ? "sm:grid-cols-2" : "sm:grid-cols-3"}`}>
      {!lockDomain && (
        <select
          className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-300"
          value={selection.domainId}
          onChange={(e) => {
            const d = catalog.domains.find((x) => x.id === e.target.value);
            const sub = d?.subdomains[0];
            const mod = sub?.models[0];
            if (d && sub && mod) {
              onSelectionChange({ domainId: d.id, subdomainId: sub.id, modelId: mod.id });
            }
          }}
        >
          {catalog.domains.map((d) => (
            <option key={d.id} value={d.id}>
              {d.label}
            </option>
          ))}
        </select>
      )}
      <select
        className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-300"
        value={selection.subdomainId}
        onChange={(e) => {
          const sub = domain?.subdomains.find((s) => s.id === e.target.value);
          const mod = sub?.models[0];
          if (sub && mod) {
            onSelectionChange({ ...selection, subdomainId: sub.id, modelId: mod.id });
          }
        }}
      >
        {domain?.subdomains.map((s) => (
          <option key={s.id} value={s.id}>
            {s.label}
          </option>
        ))}
      </select>
      <select
        className="rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-300"
        value={selection.modelId}
        onChange={(e) => onSelectionChange({ ...selection, modelId: e.target.value })}
      >
        {subdomain?.models.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label}
          </option>
        ))}
      </select>
    </div>
  );
}
