"use client";

import { useState } from "react";
import {
  ArrowRight,
  Loader2,
  LockKeyhole,
  LogIn,
  UserPlus,
} from "lucide-react";
import { login, register } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { KhukraMark } from "@/components/brand/KhukraLogo";

export function LoginForm() {
  const { login: setAuth } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
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
    <div
      className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-10 text-white"
      style={{ backgroundColor: "#05070a", color: "#e6edf3" }}
    >
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-[-18rem] h-[34rem] w-[52rem] -translate-x-1/2 rounded-full bg-sky-500/10 blur-3xl" />
        <div className="absolute bottom-[-16rem] right-[-10rem] h-[34rem] w-[34rem] rounded-full bg-violet-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.035)_1px,transparent_1px)] bg-[size:64px_64px] opacity-20" />
      </div>

      <div className="relative w-full max-w-md">
        <header className="mb-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <KhukraMark className="h-8 w-8 text-white" accentColor="#7dd3fc" />
          </div>
          <p className="mt-5 text-xs uppercase tracking-[0.32em] text-zinc-600">Khukra</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] text-white">Work by domain.</h1>
          <p className="mt-3 text-sm leading-6 text-zinc-500">
            Sign in to open Physical, Finance, and the other domain workspaces.
          </p>
        </header>

        <div
          className="rounded-3xl border border-white/10 bg-[#0b1015]/90 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl sm:p-8"
          style={{ backgroundColor: "rgba(11, 16, 21, 0.92)" }}
        >
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-400 text-black">
              <LockKeyhole className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">
                {mode === "register" ? "Create account" : "Sign in"}
              </h2>
              <p className="text-xs text-zinc-500">Inference · Data · MLOps · Analytics</p>
            </div>
          </div>

          <div className="mb-6 grid grid-cols-2 rounded-2xl border border-white/10 bg-black/20 p-1">
            <ModeButton
              active={mode === "login"}
              onClick={() => {
                setMode("login");
                setError(null);
              }}
            >
              Sign in
            </ModeButton>
            <ModeButton
              active={mode === "register"}
              onClick={() => {
                setMode("register");
                setError(null);
              }}
            >
              Register
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

            <Field label="Email">
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
                placeholder={mode === "register" ? "Choose a password" : "Your password"}
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
              {mode === "login" ? "Continue" : "Create account"}
              {!loading && <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />}
            </button>
          </form>

          <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-zinc-600">Dev access</p>
            <p className="mt-2 font-mono text-xs text-zinc-500">
              admin@khukra.local · khukra-admin
            </p>
          </div>
        </div>
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
        active ? "bg-white text-black shadow-sm" : "text-zinc-500 hover:text-zinc-300"
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
      <span className="mb-2 block text-sm font-medium text-zinc-300">{label}</span>
      {children}
    </label>
  );
}
