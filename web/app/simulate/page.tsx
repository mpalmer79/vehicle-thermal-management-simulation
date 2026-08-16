import type { Metadata } from "next";
import { Suspense } from "react";
import { SimulationForm } from "@/components/simulation-form";

export const metadata: Metadata = { title: "Simulation Lab" };

export default function SimulationPage() {
  return <>
    <header className="page-header">
      <span className="eyebrow">SCENARIO INPUT</span>
      <h1>Simulation Lab</h1>
      <p>Configure the inputs that will be sent to the authoritative VTMS Python engine. UI-1 exposes the contract without reproducing the physics in React.</p>
    </header>
    <Suspense fallback={<div className="simulation-form">Loading scenario controls...</div>}>
      <SimulationForm />
    </Suspense>
  </>;
}
