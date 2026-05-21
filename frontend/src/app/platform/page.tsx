"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { Suspense } from "react";
import type { DomainModule } from "@/components/domain/types";
import { domainPath } from "@/components/domain/types";

function PlatformRedirect() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const domain = searchParams.get("domain") ?? "physical";
  const module = (searchParams.get("module") ?? "overview") as DomainModule;
  const subdomain = searchParams.get("subdomain");
  const model = searchParams.get("model");

  useEffect(() => {
    const extra: Record<string, string> = {};
    if (subdomain) extra.subdomain = subdomain;
    if (model) extra.model = model;
    router.replace(domainPath(domain, module, Object.keys(extra).length ? extra : undefined));
  }, [router, domain, module, subdomain, model]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
      <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
    </div>
  );
}

export default function PlatformRedirectPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
          <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
        </div>
      }
    >
      <PlatformRedirect />
    </Suspense>
  );
}
