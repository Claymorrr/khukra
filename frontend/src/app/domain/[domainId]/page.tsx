"use client";

import { Suspense } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { AuthProvider, useAuth } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";
import { DomainShell } from "@/components/domain/DomainShell";

function DomainContent() {
  const { isAuthenticated } = useAuth();
  const params = useParams();
  const searchParams = useSearchParams();
  const domainId = typeof params.domainId === "string" ? params.domainId : "physical";
  const module = searchParams.get("module") ?? undefined;
  const subdomain = searchParams.get("subdomain") ?? undefined;
  const model = searchParams.get("model") ?? undefined;

  if (!isAuthenticated) return <LoginForm />;
  return (
    <DomainShell
      domainId={domainId}
      initialModule={module ?? undefined}
      initialSubdomain={subdomain ?? undefined}
      initialModel={model ?? undefined}
    />
  );
}

export default function DomainPage() {
  return (
    <AuthProvider>
      <Suspense
        fallback={
          <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
            <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
          </div>
        }
      >
        <DomainContent />
      </Suspense>
    </AuthProvider>
  );
}
