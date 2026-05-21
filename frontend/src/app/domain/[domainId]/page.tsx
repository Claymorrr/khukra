"use client";

import { Suspense } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { AuthProvider, useAuth } from "@/lib/auth";
import { AuthLoadingShell } from "@/components/AuthLoadingShell";
import { LoginForm } from "@/components/LoginForm";
import { DomainShell } from "@/components/domain/DomainShell";

function DomainContent() {
  const { isAuthenticated, ready } = useAuth();
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
      <Suspense fallback={<AuthLoadingShell />}>
        <DomainContent />
      </Suspense>
    </AuthProvider>
  );
}
