import type { Metadata } from "next";

import { StoredRunResult } from "@/components/stored-run-result";

export const metadata: Metadata = { title: "Computed Simulation Result" };

export default function ComputedResultPage() {
  return <StoredRunResult />;
}
