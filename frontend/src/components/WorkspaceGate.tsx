"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Box, Brain, Cpu, LineChart, Loader2, LogOut, Truck } from "lucide-react";
import { getCatalog } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DomainInfo } from "@/lib/types";
import { domainPath } from "./domain/types";

const DOMAIN_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

export function WorkspaceGate() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [domains, setDomains] = useState<DomainInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCatalog()
      .then((c) => setDomains(c.domains))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load domains"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#07090d] px-6 py-12">
      <p className="text-xs font-medium uppercase tracking-[0.32em] text-zinc-600">Khukra</p>
      <h1 className="mt-4 text-center text-3xl font-semibold text-white">Choose a domain</h1>
      <p className="mt-3 max-w-lg text-center text-sm leading-6 text-zinc-500">
        Each domain includes inference, sweeps, data generation, MLOps, analytics, and insights in one workspace.
      </p>
      {user && (
        <p className="mt-4 text-xs text-zinc-600">Signed in as {user.display_name}</p>
      )}

      {loading && (
        <div className="mt-12">
          <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
        </div>
      )}

      {error && (
        <p className="mt-8 text-sm text-red-400">{error}</p>
      )}

      {!loading && !error && (
        <div className="mt-10 grid w-full max-w-4xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {domains.map((domain) => {
            const Icon = DOMAIN_ICONS[domain.id] ?? Box;
            const modelCount = domain.subdomains.reduce((n, s) => n + s.models.length, 0);
            return (
              <button
                key={domain.id}
                type="button"
                onClick={() => router.push(domainPath(domain.id, "overview"))}
                className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-6 text-left transition hover:border-white/20 hover:bg-white/[0.06]"
              >
                <div
                  className="absolute inset-x-0 top-0 h-1"
                  style={{ backgroundColor: domain.color }}
                />
                <Icon className="h-7 w-7" style={{ color: domain.color }} />
                <h2 className="mt-4 text-lg font-semibold text-white">{domain.label}</h2>
                <p className="mt-2 text-sm text-zinc-500">
                  {domain.subdomains.length} subdomains · {modelCount} models
                </p>
                <p className="mt-4 flex items-center gap-1 text-xs text-zinc-400 group-hover:text-white">
                  Open domain
                  <ArrowRight className="h-3.5 w-3.5" />
                </p>
              </button>
            );
          })}
        </div>
      )}

      <button
        type="button"
        onClick={logout}
        className="mt-10 flex items-center gap-2 text-xs text-zinc-600 hover:text-zinc-400"
      >
        <LogOut className="h-3.5 w-3.5" />
        Sign out
      </button>
    </div>
  );
}
