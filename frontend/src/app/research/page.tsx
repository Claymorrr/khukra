"use client";

import { Suspense } from "react";
import { useRouter } from "next/navigation";
import { Dashboard } from "@/components/Dashboard";
import { AuthProvider } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";
import { useAuth } from "@/lib/auth";

function ResearchContent() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  if (!isAuthenticated) return <LoginForm />;
  return <Dashboard onSwitchToPlatform={() => router.push("/platform")} />;
}

export default function ResearchPage() {
  return (
    <AuthProvider>
      <Suspense fallback={null}>
        <ResearchContent />
      </Suspense>
    </AuthProvider>
  );
}
