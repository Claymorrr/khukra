"use client";

import type { ParameterSchema } from "@/lib/types";
import { ParameterForm } from "./ParameterForm";

export interface DynamicParameterField extends ParameterSchema {
  description?: string;
  unit?: string;
  min?: number | null;
  max?: number | null;
  step?: number | null;
  options?: Array<string | number | boolean>;
}

interface DynamicParameterFormProps {
  parameters: DynamicParameterField[];
  values: Record<string, string | number | boolean>;
  onChange: (name: string, value: string | number | boolean) => void;
  accentColor: string;
}

export function defaultParamValues(
  parameters: DynamicParameterField[]
): Record<string, string | number | boolean> {
  const defaults: Record<string, string | number | boolean> = {};
  for (const p of parameters) {
    defaults[p.name] = p.default as string | number | boolean;
  }
  return defaults;
}

export function DynamicParameterForm({
  parameters,
  values,
  onChange,
  accentColor,
}: DynamicParameterFormProps) {
  return (
    <div className="space-y-4">
      <ParameterForm
        parameters={parameters}
        values={values}
        onChange={onChange}
        accentColor={accentColor}
      />
      {parameters.some((p) => p.description) && (
        <div className="grid gap-2 sm:grid-cols-2">
          {parameters
            .filter((p) => p.description)
            .map((p) => (
              <p key={p.name} className="text-xs text-zinc-600">
                <span className="font-mono text-zinc-500">{p.name}</span>
                {p.unit ? ` (${p.unit})` : ""}: {p.description}
              </p>
            ))}
        </div>
      )}
    </div>
  );
}
