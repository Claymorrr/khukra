"use client";

import { AuthProvider, useAuth } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";
import { WorkspaceGate } from "@/components/WorkspaceGate";

function AppGate() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <WorkspaceGate /> : <LoginForm />;
}

export default function Home() {
  return (
    <AuthProvider>
      <AppGate />
    </AuthProvider>
  );
}
