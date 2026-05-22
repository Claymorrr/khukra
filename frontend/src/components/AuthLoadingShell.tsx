"use client";

import { Loader2 } from "lucide-react";
import { KhukraMark } from "@/components/brand/KhukraLogo";

/** Shared shell used before client auth state is read from localStorage. */
export function AuthLoadingShell() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#07090d]">
      <KhukraMark className="h-12 w-12 text-white" accentColor="#38bdf8" />
      <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
    </div>
  );
}
