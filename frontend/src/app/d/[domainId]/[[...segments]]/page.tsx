"use client";

import { Suspense } from "react";
import { useParams } from "next/navigation";
import { AuthProvider, useAuth } from "@/lib/auth";
import { AuthLoadingShell } from "@/components/AuthLoadingShell";
import { LoginForm } from "@/components/LoginForm";
import { AppShell } from "@/components/shell/AppShell";
import type { AppZone } from "@/lib/api/v1";

const VALID_ZONES: AppZone[] = ["discover", "data", "knowledge", "workflows", "operations"];

function DContent() {
  const { isAuthenticated, ready } = useAuth();
  const params = useParams();
  const domainId = typeof params.domainId === "string" ? params.domainId : "physical";
  const segments = params.segments;
  const segList = Array.isArray(segments) ? segments : segments ? [segments] : [];

  if (!ready) return <AuthLoadingShell />;
  if (!isAuthenticated) return <LoginForm />;

  let zone: AppZone = "data";
  let productId: string | undefined;

  if (segList[0] === "products" && segList[1]) {
    zone = "data";
    productId = segList[1];
  } else if (segList[0] && VALID_ZONES.includes(segList[0] as AppZone)) {
    zone = segList[0] as AppZone;
  }

  return <AppShell domainId={domainId} zone={zone} productId={productId} />;
}

export default function DPage() {
  return (
    <AuthProvider>
      <Suspense fallback={<AuthLoadingShell />}>
        <DContent />
      </Suspense>
    </AuthProvider>
  );
}
