"use client";

import { useMemo, useState } from "react";
import { Bot, MessageSquare, Send, Sparkles, X } from "lucide-react";
import type { AppZone } from "@/lib/api/v1";
import type { DomainInfo } from "@/lib/types";

interface DomainAssistantProps {
  domain?: DomainInfo;
  domainId: string;
  zone: AppZone;
  accentColor: string;
}

interface AssistantMessage {
  role: "assistant" | "user";
  content: string;
}

const PHYSICAL_SUGGESTIONS = [
  "What should I run first?",
  "Explain physical units on parameters",
  "What equations does the beam solver use?",
  "Local solver vs external backend?",
];

const DEFAULT_SUGGESTIONS = [
  "What should I do next?",
  "Explain this workspace",
  "How do I use the lake?",
  "How do I compare runs?",
];

export function DomainAssistant({
  domain,
  domainId,
  zone,
  accentColor,
}: DomainAssistantProps) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      role: "assistant",
      content: introFor(domainId, domain?.label),
    },
  ]);

  const suggestions = useMemo(
    () => (domainId === "physical" ? PHYSICAL_SUGGESTIONS : DEFAULT_SUGGESTIONS),
    [domainId]
  );

  function submit(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmed },
      {
        role: "assistant",
        content: answerFor(trimmed, domainId, zone, domain),
      },
    ]);
    setInput("");
  }

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <div className="mb-3 flex h-[34rem] w-[25rem] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-3xl border border-white/10 bg-[#080b10]/95 shadow-2xl shadow-black/50 backdrop-blur-xl">
          <header className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div className="flex items-center gap-2">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-2xl"
                style={{ backgroundColor: `${accentColor}22`, color: accentColor }}
              >
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">Khukra Assistant</p>
                <p className="text-xs text-zinc-600">{domain?.label ?? domainId} · {zone}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg p-1.5 text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
              aria-label="Close assistant"
            >
              <X className="h-4 w-4" />
            </button>
          </header>

          <div className="scrollbar-thin flex-1 space-y-3 overflow-y-auto px-4 py-4">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`rounded-2xl px-4 py-3 text-sm leading-6 ${
                  message.role === "assistant"
                    ? "border border-white/10 bg-white/[0.04] text-zinc-300"
                    : "ml-8 bg-white/[0.09] text-white"
                }`}
              >
                {message.content}
              </div>
            ))}
          </div>

          <div className="border-t border-white/10 p-3">
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => submit(suggestion)}
                  className="rounded-full border border-white/10 px-3 py-1 text-xs text-zinc-500 hover:bg-white/5 hover:text-zinc-300"
                >
                  {suggestion}
                </button>
              ))}
            </div>
            <form
              className="flex items-center gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                submit(input);
              }}
            >
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask what to run, inspect, or compare..."
                className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-700 focus:border-white/20"
              />
              <button
                type="submit"
                className="rounded-xl px-3 py-2 text-black disabled:opacity-50"
                style={{ backgroundColor: accentColor }}
                disabled={!input.trim()}
                aria-label="Send assistant message"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-2 rounded-full px-4 py-3 text-sm font-semibold text-black shadow-2xl shadow-black/40"
        style={{ backgroundColor: accentColor }}
      >
        {open ? <Sparkles className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
        Assistant
      </button>
    </div>
  );
}

function introFor(domainId: string, label?: string): string {
  if (domainId === "physical") {
    return "I can help with the Physics Solver workspace: explain parameter units (m, Pa, deg C, etc.), structured equation specs, local vs future external/GPU backends, metrics/traces, and surrogate-ready sweeps.";
  }
  return `I can help navigate ${label ?? domainId}: models, data products, workflows, analytics, and evidence lineage.`;
}

function answerFor(
  question: string,
  domainId: string,
  zone: AppZone,
  domain?: DomainInfo
): string {
  const q = question.toLowerCase();
  if (domainId === "physical") {
    if (q.includes("first") || q.includes("start") || q.includes("run")) {
      return "Start in Workflows. Open the full solver shell, choose Mechanics -> Cantilever Beam, keep defaults, and press Solve. You should get deflection metrics plus a spatial trace. Then try Dynamics -> Point Mass 2D for an ODE trace.";
    }
    if (q.includes("surrogate") || q.includes("dataset") || q.includes("data")) {
      return "Use Data or Workflows to generate solver datasets. Good surrogate candidates come from sweeps: vary a small set of physical parameters, keep solver outputs such as max_deflection_mm or effectiveness as targets, and store traces in the Physical solver lake.";
    }
    if (q.includes("trace") || q.includes("series")) {
      return "Traces are the solver's time or spatial outputs. Beam traces are position vs deflection/moment/shear. Thermofluid traces are time vs hot/cold temperatures and heat transfer. Dynamics traces are position and speed over time.";
    }
    if (q.includes("metric") || q.includes("output")) {
      return "Metrics are scalar scientific summaries from a solver run: extrema, steady-state estimates, energy, effectiveness, displacement, and numerical status. Use them for comparisons and sweeps; use traces for deeper analytics.";
    }
    if (q.includes("workflow") || q.includes("sweep")) {
      return "A solver workflow is: set physical parameters, run the equation model, inspect metrics and traces, sweep parameters, then register the resulting solver artifacts or surrogate training dataset.";
    }
    if (q.includes("unit") || q.includes("pa") || q.includes("deg")) {
      const modelCount =
        domain?.subdomains?.reduce((n, s) => n + (s.models?.length ?? 0), 0) ?? 4;
      return `Physical parameters carry SI-style units from the solver catalog (${modelCount} solvers). Examples: beam span in m, modulus in Pa, load in N/m, temperatures in deg C. Plain numeric values stay numeric, and explicit unit payloads can be normalized to each solver's canonical unit before run.`;
    }
    if (q.includes("equation") || q.includes("symbol") || q.includes("sympy")) {
      return "Each solver exposes structured EquationSpec metadata (name, form, variables, parameters, equation_type, optional residual) alongside the human-readable governing_equations string. This is symbolic-ready for SymPy/Jacobian generation later—not full computer algebra yet.";
    }
    if (
      q.includes("backend") ||
      q.includes("gpu") ||
      q.includes("cfd") ||
      q.includes("fea") ||
      q.includes("external")
    ) {
      return "Today all physics predictors route through the local RuleBasedPredictor registry (mechanics_beam_solver, thermofluid_heat_exchanger_solver, etc.). The predictor registry is the extension point for external CFD/FEA jobs, GPU batched sweeps, and symbolic backends without changing the workflow UI.";
    }
    return "For Physical Systems: choose a solver family, set parameters with catalog units, run Solve, inspect metrics/traces/numerical status and equation specs, then sweep for sensitivity or surrogate data.";
  }

  if (q.includes("lake") || q.includes("data")) {
    return "Open the Data zone to inspect lake assets, data products, contracts, quality status, and lineage. Use Workflows to generate or infer new evidence.";
  }
  if (q.includes("compare") || q.includes("sweep")) {
    return "Use Workflows for sweeps and comparisons. Sweeps vary model inputs; Compare helps inspect output deltas across saved runs.";
  }
  return `For ${domain?.label ?? domainId}, use Discover for strategy, Data for lake assets, Workflows for model runs and pipelines, Knowledge for reports, and Operations for readiness.`;
}
