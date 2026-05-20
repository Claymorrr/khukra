"use client";

import { useState } from "react";
import {
  ArrowRight,
  BadgeCheck,
  Database,
  Loader2,
  LockKeyhole,
  LogIn,
  Sparkles,
  UserPlus,
  Workflow,
} from "lucide-react";
import { login, register } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export function LoginForm() {
  const { login: setAuth } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res =
        mode === "login"
          ? await login(email, password)
          : await register(email, password, displayName || email.split("@")[0]);
      setAuth(res.access_token, res.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-10">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-10%] top-[-20%] h-96 w-96 rounded-full bg-sky-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl" />
      </div>

      <div className="relative grid w-full max-w-6xl overflow-hidden rounded-3xl border border-white/10 bg-[#0b1015]/90 shadow-2xl shadow-sky-950/30 backdrop-blur-xl lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden min-h-[680px] border-r border-white/10 p-10 lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(56,189,248,0.18),transparent_30%),radial-gradient(circle_at_80%_80%,rgba(52,211,153,0.12),transparent_35%)]" />
          <div className="relative flex h-full flex-col justify-between">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-medium text-sky-300">
                <Sparkles className="h-3.5 w-3.5" />
                Khukra private beta
              </div>

              <h1 className="mt-8 max-w-xl text-5xl font-semibold tracking-tight text-white">
                Stochastic research MLOps for computational modeling systems.
              </h1>
              <p className="mt-5 max-w-lg text-base leading-7 text-zinc-400">
                Build synthetic scenarios, forecast uncertainty, inspect lineage,
                and prepare optimization-ready research across five advanced domains.
              </p>

              <div className="mt-10 grid gap-3">
                <FeatureCard
                  icon={<Workflow className="h-5 w-5" />}
                  title="Stochastic scenario sweeps"
                  description="Evaluate rare-event, regime, and queueing inputs across reproducible scenario grids."
                />
                <FeatureCard
                  icon={<Database className="h-5 w-5" />}
                  title="Local lakehouse"
                  description="Persist synthetic datasets, traces, evaluations, artifacts, and exports in DuckDB/Parquet."
                />
                <FeatureCard
                  icon={<BadgeCheck className="h-5 w-5" />}
                  title="Smart research documentation"
                  description="Understand model purpose, stochastic process design, lineage, and optimization orientation."
                />
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <p className="text-xs uppercase tracking-[0.25em] text-zinc-500">
                Current platform
              </p>
              <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                <Stat value="5" label="Domains" />
                <Stat value="15" label="Subdomains" />
                <Stat value="MLOps" label="Ready" />
              </div>
            </div>
          </div>
        </section>

        <section className="p-6 sm:p-10">
          <div className="mx-auto flex min-h-[620px] max-w-md flex-col justify-center">
            <div className="mb-8">
              <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-400 text-black shadow-lg shadow-sky-500/20">
                <LockKeyhole className="h-6 w-6" />
              </div>
              <h2 className="text-3xl font-semibold tracking-tight text-white">
                {mode === "register" ? "Create your workspace" : "Welcome back"}
              </h2>
              <p className="mt-2 text-sm leading-6 text-zinc-500">
                {mode === "register"
                  ? "Set up your Khukra account to start producing stochastic inferences and lineage-backed evidence."
                  : "Sign in to continue your research, MLOps, and optimization work."}
              </p>
            </div>

            <div className="mb-6 grid grid-cols-2 rounded-2xl border border-white/10 bg-black/20 p-1">
              <ModeButton
                active={mode === "register"}
                onClick={() => {
                  setMode("register");
                  setError(null);
                }}
              >
                Register
              </ModeButton>
              <ModeButton
                active={mode === "login"}
                onClick={() => {
                  setMode("login");
                  setError(null);
                }}
              >
                Sign in
              </ModeButton>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "register" && (
                <Field label="Display name">
                  <input
                    type="text"
                    placeholder="Ahmed"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="auth-input"
                  />
                </Field>
              )}

              <Field label="Email address">
                <input
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="auth-input"
                  required
                />
              </Field>

              <Field label="Password">
                <input
                  type="password"
                  placeholder={mode === "register" ? "Choose a strong password" : "Enter your password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="auth-input"
                  required
                />
              </Field>

              {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="group mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-sky-400 px-4 py-3 text-sm font-semibold text-black transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : mode === "login" ? (
                  <LogIn className="h-4 w-4" />
                ) : (
                  <UserPlus className="h-4 w-4" />
                )}
                {mode === "login" ? "Sign in to Khukra" : "Create Khukra account"}
                {!loading && <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />}
              </button>
            </form>

            <div className="mt-6 rounded-2xl border border-amber-400/15 bg-amber-400/5 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-amber-300/80">
                Development access
              </p>
              <p className="mt-2 text-sm text-zinc-400">
                Use the seeded admin account if you want to skip registration.
              </p>
              <div className="mt-3 grid gap-2 rounded-xl bg-black/20 p-3 font-mono text-xs text-zinc-400">
                <span>admin@khukra.local</span>
                <span>khukra-admin</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function ModeButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-4 py-2.5 text-sm font-medium transition ${
        active
          ? "bg-white text-black shadow-sm"
          : "text-zinc-500 hover:text-zinc-300"
      }`}
    >
      {children}
    </button>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-zinc-300">
        {label}
      </span>
      {children}
    </label>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-400/10 text-sky-300">
          {icon}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-zinc-500">{description}</p>
        </div>
      </div>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl bg-black/20 px-3 py-4">
      <p className="text-2xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-xs text-zinc-500">{label}</p>
    </div>
  );
}
