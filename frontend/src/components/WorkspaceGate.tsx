"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowUpRight,
  Box,
  Brain,
  Cpu,
  LineChart,
  Loader2,
  LogOut,
  Truck,
} from "lucide-react";
import { getCatalog } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { DomainInfo } from "@/lib/types";
import { zonePath } from "@/lib/api/v1";
import { KhukraLogo } from "@/components/brand/KhukraLogo";

const DOMAIN_ICONS: Record<string, typeof Box> = {
  physical: Box,
  finance: LineChart,
  supply_chain: Truck,
  intelligence: Brain,
  computing: Cpu,
};

const DOMAIN_BLURBS: Record<string, string> = {
  physical: "Simulation cockpit: mechanics, thermofluid, dynamics solvers, sweeps, surrogate-ready outputs.",
  finance: "Inference cockpit: scenarios, signals, backtests, execution simulation, risk, paper-trading gates.",
  supply_chain: "Resilience simulations: quality drift, disruption risk, recovery policy workloads.",
  intelligence: "Fusion inference: signal fusion, influence diffusion, warning simulations.",
  computing: "Reliability simulation: latency, throughput, edge-degradation workloads.",
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
    <div className="relative min-h-screen overflow-hidden bg-[#05070a] px-6 py-8 text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-[-18rem] h-[34rem] w-[52rem] -translate-x-1/2 rounded-full bg-sky-500/10 blur-3xl" />
        <div className="absolute bottom-[-16rem] right-[-10rem] h-[34rem] w-[34rem] rounded-full bg-violet-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.035)_1px,transparent_1px)] bg-[size:64px_64px] opacity-20" />
      </div>

      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col">
        <header className="flex items-center justify-between">
          <KhukraLogo accentColor="#7dd3fc" subtitle="Inference & Simulation Cockpit" />
          <button
            type="button"
            onClick={logout}
            className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-xs text-zinc-500 transition hover:bg-white/[0.06] hover:text-zinc-300"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </header>

        <main className="flex flex-1 flex-col justify-center py-12">
          <section className="mb-10 max-w-3xl">
            <p className="text-xs uppercase tracking-[0.32em] text-zinc-600">Mission control</p>
            <h1 className="mt-4 text-5xl font-semibold tracking-[-0.04em] text-white sm:text-6xl">
              Interactive cockpit for inference and simulation.
            </h1>
            <div className="mt-5 flex flex-wrap items-center gap-3 text-xs text-zinc-600">
              {user && <span>{user.display_name}</span>}
              <span className="h-1 w-1 rounded-full bg-zinc-700" />
              <span>Develop · Validate · Package · Operate</span>
            </div>
          </section>

          {loading && (
            <div className="flex h-56 items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
            </div>
          )}

          {error && (
            <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-6 text-sm text-red-300">
              {error}
            </div>
          )}

          {!loading && !error && (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              {domains.map((domain, index) => {
                const Icon = DOMAIN_ICONS[domain.id] ?? Box;
                const modelCount = domain.subdomains.reduce((n, s) => n + s.models.length, 0);
                const domainTitle = domain.label.split(" — ")[0];
                const domainDetail = `${domain.subdomains.length} workload families · ${modelCount} instruments`;
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => router.push(zonePath(domain.id, "workflows"))}
                    className="group relative min-h-72 overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.035] p-5 text-left shadow-2xl shadow-black/20 transition duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/[0.06]"
                  >
                    <div
                      className="absolute -right-16 -top-16 h-40 w-40 rounded-full opacity-20 blur-3xl transition group-hover:opacity-35"
                      style={{ backgroundColor: domain.color }}
                    />
                    <div className="relative flex h-full flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-zinc-700">0{index + 1}</span>
                          <ArrowUpRight className="h-4 w-4 text-zinc-700 transition group-hover:text-white" />
                        </div>
                        <div
                          className="mt-10 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10"
                          style={{ backgroundColor: `${domain.color}18`, color: domain.color }}
                        >
                          <Icon className="h-6 w-6" />
                        </div>
                      </div>

                      <div>
                        <h2 className="text-lg font-medium tracking-tight text-white">{domainTitle}</h2>
                        <p className="mt-2 text-xs text-zinc-600">{domainDetail}</p>
                        <p className="mt-3 text-xs leading-5 text-zinc-500">
                          {DOMAIN_BLURBS[domain.id] ??
                            "Inference and simulation workloads with validation and lifecycle ops."}
                        </p>
                        <div
                          className="mt-5 h-1 w-12 rounded-full transition-all group-hover:w-20"
                          style={{ backgroundColor: domain.color }}
                        />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
