"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { PlatformShell } from "@/components/platform/PlatformShell";
import { AuthProvider, useAuth } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";

function PlatformContent() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const module = searchParams.get("module") ?? undefined;

  if (!isAuthenticated) return <LoginForm />;
  return (
    <PlatformShell
      initialModule={module ?? undefined}
      onSwitchToResearch={() => router.push("/research")}
    />
  );
}

export default function PlatformPage() {
  return (
    <AuthProvider>
      <Suspense
        fallback={
          <div className="flex min-h-screen items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
          </div>
        }
      >
        <PlatformContent />
      </Suspense>
    </AuthProvider>
  );
}
