"use client";

import type { DomainInfo } from "@/lib/types";
import { DomainCockpit } from "../cockpit/DomainCockpit";

interface PhysicsSolverWorkbenchProps {
  domain: DomainInfo;
  accentColor: string;
  initialSubdomain?: string;
  initialModel?: string;
}

/** @deprecated Use DomainCockpit */
export function PhysicsSolverWorkbench(props: PhysicsSolverWorkbenchProps) {
  return <DomainCockpit {...props} />;
}
