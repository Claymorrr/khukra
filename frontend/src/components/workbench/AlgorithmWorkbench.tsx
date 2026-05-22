"use client";

import type { DomainInfo } from "@/lib/types";
import { DomainCockpit } from "../cockpit/DomainCockpit";

export interface AlgorithmWorkbenchProps {
  domain: DomainInfo;
  accentColor: string;
  initialSubdomain?: string;
  initialModel?: string;
}

/** @deprecated Use DomainCockpit */
export function AlgorithmWorkbench(props: AlgorithmWorkbenchProps) {
  return <DomainCockpit {...props} />;
}
