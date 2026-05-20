"use client";

import { useRouter } from "next/navigation";
import { Beaker, Layers, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth";

export function WorkspaceGate() {
  const { user, logout } = useAuth();
  const router = useRouter();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#07090d] px-6">
      <p className="text-xs font-medium uppercase tracking-[0.32em] text-zinc-600">Khukra</p>
      <h1 className="mt-4 text-center text-3xl font-semibold text-white">
        Choose your workspace
      </h1>
      <p className="mt-3 max-w-lg text-center text-sm leading-6 text-zinc-500">
        Research focuses on domain models, stochastic forecasts, and sweeps. Platform handles data
        generation, MLOps, ML inferencing, analytics, and insights.
      </p>
      {user && (
        <p className="mt-4 text-xs text-zinc-600">Signed in as {user.display_name}</p>
      )}
      <div className="mt-10 grid w-full max-w-2xl gap-6 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => router.push("/research")}
          className="group rounded-3xl border border-white/10 bg-gradient-to-br from-emerald-500/10 to-transparent p-8 text-left transition hover:border-emerald-500/40"
        >
          <Beaker className="h-8 w-8 text-emerald-400" />
          <h2 className="mt-4 text-xl font-semibold text-white">Research workspace</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-500">
            Five domains, 15 forecasting models, inference, sweeps, comparisons, and documentation.
          </p>
        </button>
        <button
          type="button"
          onClick={() => router.push("/platform")}
          className="group rounded-3xl border border-white/10 bg-gradient-to-br from-sky-500/10 to-transparent p-8 text-left transition hover:border-sky-500/40"
        >
          <Layers className="h-8 w-8 text-sky-400" />
          <h2 className="mt-4 text-xl font-semibold text-white">Platform workspace</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-500">
            Data generation studio, MLOps, ML inferencing, analytics workbench, insights engineering.
          </p>
        </button>
      </div>
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
