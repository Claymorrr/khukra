"use client";

import type { ParameterSchema } from "@/lib/types";

interface ParameterFormProps {
  parameters: ParameterSchema[];
  values: Record<string, string | number | boolean>;
  onChange: (name: string, value: string | number | boolean) => void;
  accentColor: string;
}

export function ParameterForm({
  parameters,
  values,
  onChange,
  accentColor,
}: ParameterFormProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {parameters.map((param) => (
        <label
          key={param.name}
          className="group block rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:border-white/20 hover:bg-white/[0.035]"
        >
          <span className="mb-1.5 flex items-center justify-between gap-3 text-xs font-medium text-zinc-400">
            <span>{param.label}</span>
            <span className="rounded-full bg-white/5 px-2 py-0.5 font-mono text-[10px] uppercase text-zinc-600">
              {param.type}
            </span>
          </span>
          <span className="mb-3 block truncate font-mono text-[11px] text-zinc-700">
            {param.name}
          </span>
          {param.options && param.options.length > 0 ? (
            <select
              value={String(values[param.name] ?? param.default)}
              onChange={(e) => {
                const raw = e.target.value;
                const match = param.options?.find((o) => String(o) === raw);
                onChange(param.name, match ?? raw);
              }}
              className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-white outline-none"
            >
              {param.options.map((opt) => (
                <option key={String(opt)} value={String(opt)}>
                  {String(opt)}
                </option>
              ))}
            </select>
          ) : param.type === "string" ? (
            <input
              type="text"
              value={String(values[param.name] ?? param.default)}
              onChange={(e) => onChange(param.name, e.target.value)}
              className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-white outline-none transition focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]"
              style={{ ["--accent" as string]: accentColor }}
            />
          ) : param.type === "boolean" ? (
            <button
              type="button"
              onClick={() => onChange(param.name, !Boolean(values[param.name] ?? param.default))}
              className="flex w-full items-center justify-between rounded-xl border border-border bg-surface px-3 py-2.5 text-sm text-zinc-300"
            >
              <span>{Boolean(values[param.name] ?? param.default) ? "Enabled" : "Disabled"}</span>
              <span
                className="relative h-5 w-9 rounded-full transition"
                style={{
                  backgroundColor: Boolean(values[param.name] ?? param.default) ? accentColor : "#30363d",
                }}
              >
                <span
                  className={`absolute top-0.5 h-4 w-4 rounded-full bg-black transition ${
                    Boolean(values[param.name] ?? param.default) ? "left-4" : "left-0.5"
                  }`}
                />
              </span>
            </button>
          ) : (
            <input
              type="number"
              step={param.step ?? (param.type === "integer" ? 1 : "any")}
              min={param.min ?? undefined}
              max={param.max ?? undefined}
              value={Number(values[param.name] ?? param.default)}
              onChange={(e) =>
                onChange(
                  param.name,
                  param.type === "integer"
                    ? parseInt(e.target.value, 10)
                    : parseFloat(e.target.value)
                )
              }
              className="w-full rounded-xl border border-border bg-surface px-3 py-2.5 font-mono text-sm text-white outline-none transition focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]"
              style={{ ["--accent" as string]: accentColor }}
            />
          )}
        </label>
      ))}
    </div>
  );
}
