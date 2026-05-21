"use client";

import { Suspense, useEffect } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { AuthProvider } from "@/lib/auth";
import { AuthLoadingShell } from "@/components/AuthLoadingShell";
import type { AppZone } from "@/lib/api/v1";

const MODULE_TO_ZONE: Record<string, AppZone> = {
  overview: "discover",
  data_hub: "data",
  data: "data",
  data_generation: "data",
  knowledge: "knowledge",
  inference: "workflows",
  results: "workflows",
  sweeps: "workflows",
  compare: "workflows",
  history: "workflows",
  mlops: "workflows",
  ml_inference: "workflows",
  analytics: "workflows",
  insights: "knowledge",
  infraops: "operations",
  devops: "operations",
  docs: "discover",
};

function DomainRedirect() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const domainId = typeof params.domainId === "string" ? params.domainId : "physical";
  const module = searchParams.get("module") ?? "data_hub";
  const zone = MODULE_TO_ZONE[module] ?? "data";

  useEffect(() => {
    const extra = new URLSearchParams();
    const sub = searchParams.get("subdomain");
    const model = searchParams.get("model");
    if (sub) extra.set("subdomain", sub);
    if (model) extra.set("model", model);
    if (module && !MODULE_TO_ZONE[module]) extra.set("legacyModule", module);
    const q = extra.toString() ? `?${extra}` : "";
    router.replace(`/d/${domainId}/${zone}${q}`);
  }, [domainId, module, router, searchParams, zone]);

  return <AuthLoadingShell />;
}

export default function DomainPage() {
  return (
    <AuthProvider>
      <Suspense fallback={<AuthLoadingShell />}>
        <DomainRedirect />
      </Suspense>
    </AuthProvider>
  );
}
