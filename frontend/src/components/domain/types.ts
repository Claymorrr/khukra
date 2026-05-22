export type DomainModule =
  | "overview"
  | "inference"
  | "results"
  | "sweeps"
  | "compare"
  | "docs"
  | "history"
  | "data"
  | "data_hub"
  | "knowledge"
  | "data_generation"
  | "mlops"
  | "infraops"
  | "devops"
  | "ml_inference"
  | "analytics"
  | "insights";

export const DOMAIN_MODULES: Array<{ id: DomainModule; label: string }> = [
  { id: "overview", label: "Overview" },
  { id: "inference", label: "Models & Solvers" },
  { id: "results", label: "Results" },
  { id: "sweeps", label: "Sweeps" },
  { id: "compare", label: "Compare" },
  { id: "docs", label: "Docs" },
  { id: "history", label: "History" },
  { id: "data_hub", label: "Data Hub" },
  { id: "knowledge", label: "Knowledge" },
  { id: "data", label: "Datasets" },
  { id: "data_generation", label: "Data Generation" },
  { id: "mlops", label: "MLOps" },
  { id: "infraops", label: "InfraOps" },
  { id: "devops", label: "DevOps" },
  { id: "ml_inference", label: "ML Inferencing" },
  { id: "analytics", label: "Analytics" },
  { id: "insights", label: "Insights" },
];

export function domainPath(domainId: string, module: DomainModule, extra?: Record<string, string>) {
  const params = new URLSearchParams({ module, ...extra });
  return `/domain/${domainId}?${params.toString()}`;
}
