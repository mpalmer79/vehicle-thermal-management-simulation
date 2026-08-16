import type { Metadata } from "next";
import { Suspense } from "react";
import { SimulationForm } from "@/components/simulation-form";

export const metadata: Metadata = { title: "Simulation Lab" };

export default function SimulationPage() {
  return <>
    <header className="page-header">
      <span className="eyebrow">AUTHORITATIVE SIMULATION INPUT</span>
      <h1>Simulation Lab</h1>
      <p>Configure operating conditions and supported fault states, then execute the frozen VTMS-V1 Python model through FastAPI. The browser performs no thermal calculations.</p>
    </header>
    <Suspense fallback={<div className="simulation-form">Loading scenario controls...</div>}>
      <SimulationForm />
    </Suspense>
  </>;
}
