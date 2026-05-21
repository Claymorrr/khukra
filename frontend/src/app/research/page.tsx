"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { domainPath } from "@/components/domain/types";

export default function ResearchRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(domainPath("physical", "inference"));
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07090d]">
      <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
    </div>
  );
}
