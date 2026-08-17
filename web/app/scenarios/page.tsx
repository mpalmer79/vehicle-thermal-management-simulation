import type { Metadata } from "next";

import { MotionReveal } from "@/components/motion-reveal";
import { ScenarioCardV2 } from "@/components/scenario-card-v2";
import { canonicalPreviewFile } from "@/lib/canonical-previews";
import { scenarios } from "@/lib/scenarios";

export const metadata: Metadata = { title: "Scenario Library" };

const groups = [
  { key: "Baseline", eyebrow: "BASELINE OPERATION", title: "Normal thermal behavior" },
  { key: "Fault", eyebrow: "DISCRETE FAULTS", title: "Component failure response" },
  { key: "Degradation", eyebrow: "DEGRADATION", title: "Reduced component capability" },
] as const;

export default function ScenariosPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">FROZEN ENGINEERING TESTS</span>
        <h1>Scenario Library</h1>
        <p>Nine canonical scenarios, unchanged equations, different operating conditions and faults.</p>
      </header>

      {groups.map((group) => {
        const items = scenarios.filter((scenario) => scenario.category === group.key);
        return (
          <MotionReveal className="scenario-section" key={group.key}>
            <div className="section-head">
              <div>
                <span className="eyebrow">{group.eyebrow}</span>
                <h2>{group.title}</h2>
              </div>
              <span className="count-badge">{items.length}</span>
            </div>
            <div className="scenario-grid">
              {items.map((scenario) => <ScenarioCardV2 key={scenario.id} scenario={scenario} />)}
            </div>
          </MotionReveal>
        );
      })}

      <p className="provenance-note">
        Trend and end-state values are sampled from canonical runs of the authoritative VTMS-V1 Python
        engine. {canonicalPreviewFile.samplingNote}
      </p>
    </>
  );
}
