"use client";

import { Loader2 } from "lucide-react";

/** Shared shell used before client auth state is read from localStorage. */
export function AuthLoadingShell() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
      <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
    </div>
  );
}
