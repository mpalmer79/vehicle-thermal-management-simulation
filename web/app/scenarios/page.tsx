import type { Metadata } from "next";
import { ScenarioCard } from "@/components/scenario-card";
import { scenarios } from "@/lib/scenarios";

export const metadata: Metadata = { title: "Scenario Library" };

export default function ScenariosPage() {
  const baseline = scenarios.filter((scenario) => scenario.category === "Baseline");
  const faults = scenarios.filter((scenario) => scenario.category !== "Baseline");
  return <><header className="page-header"><span className="eyebrow">FROZEN ENGINEERING TESTS</span><h1>Scenario Library</h1><p>Nine canonical scenarios exercise baseline thermal behavior, discrete failures, and component degradation without changing the governing equations.</p></header><section className="scenario-section"><div className="section-head"><div><span className="eyebrow">BASELINE OPERATION</span><h2>Normal thermal behavior</h2></div><span>{baseline.length} scenarios</span></div><div className="scenario-grid">{baseline.map((scenario) => <ScenarioCard key={scenario.id} scenario={scenario} />)}</div></section><section className="scenario-section"><div className="section-head"><div><span className="eyebrow">FAULT AND DEGRADATION</span><h2>Directional failure response</h2></div><span>{faults.length} scenarios</span></div><div className="scenario-grid">{faults.map((scenario) => <ScenarioCard key={scenario.id} scenario={scenario} />)}</div></section></>;
}
