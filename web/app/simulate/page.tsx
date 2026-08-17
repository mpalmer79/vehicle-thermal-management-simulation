import type { Metadata } from "next";
import { Suspense } from "react";

import { SimulationForm } from "@/components/simulation-form";

export const metadata: Metadata = { title: "Simulation Lab" };

export default function SimulationPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">AUTHORITATIVE SIMULATION INPUT</span>
        <h1>Simulation Lab</h1>
        <p>Configure the operating condition and fault state, then run the frozen VTMS-V1 model through FastAPI.</p>
      </header>
      <Suspense fallback={<div className="simulation-form">Loading scenario controls...</div>}>
        <SimulationForm />
      </Suspense>
    </>
  );
}
