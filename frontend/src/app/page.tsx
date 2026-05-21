"use client";

import { AuthProvider, useAuth } from "@/lib/auth";
import { AuthLoadingShell } from "@/components/AuthLoadingShell";
import { LoginForm } from "@/components/LoginForm";
import { WorkspaceGate } from "@/components/WorkspaceGate";

function AppGate() {
  const { isAuthenticated, ready } = useAuth();
  if (!ready) return <AuthLoadingShell />;
  return isAuthenticated ? <WorkspaceGate /> : <LoginForm />;
}

export default function Home() {
  return (
    <AuthProvider>
      <AppGate />
    </AuthProvider>
  );
}
