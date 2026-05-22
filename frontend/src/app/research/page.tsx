"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { zonePath } from "@/lib/api/v1";

export default function ResearchRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(
      zonePath("physical", "workflows", {
        subdomain: "mechanics",
        model: "cantilever_beam",
      })
    );
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
      <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
    </div>
  );
}
