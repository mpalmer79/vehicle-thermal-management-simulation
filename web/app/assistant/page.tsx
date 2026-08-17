import type { Metadata } from "next";
import Link from "next/link";

import { AssistantPanel } from "@/components/assistant/assistant-panel";
import { MotionReveal } from "@/components/motion-reveal";

export const metadata: Metadata = {
  title: "VTMS Assistant",
  description:
    "Ask about the VTMS thermal model, canonical scenarios, verification and validation evidence, and system architecture. Answers come from a knowledge base bundled with this site.",
};

const coverage = [
  ["MODEL", "Two-state physics, radiator, thermostat, pump, fan, air side"],
  ["SCENARIOS", "S-01 to S-09 baselines, faults, and degradations"],
  ["EVIDENCE", "Verification, KIT plausibility, controlled validation status"],
  ["SYSTEM", "Next.js, FastAPI, Python engine, deployment"],
] as const;

export default function AssistantPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">VTMS KNOWLEDGE ASSISTANT</span>
        <h1>Ask VTMS.</h1>
        <p>Answers are read from a curated knowledge base that ships with this site.</p>
      </header>

      <div className="assistant-layout">
        <MotionReveal as="div" className="assistant-stage">
          <AssistantPanel variant="page" />
        </MotionReveal>

        <MotionReveal as="aside" className="assistant-aside" delayMs={80}>
          <div className="assistant-coverage">
            <span className="eyebrow">WHAT IT KNOWS</span>
            <dl>
              {coverage.map(([term, value]) => (
                <div key={term}>
                  <dt>{term}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="assistant-honesty">
            <span className="eyebrow">HOW IT WORKS</span>
            <p>
              Your question is matched against the knowledge base by keyword and phrase scoring.
              No external AI service is contacted, and there is no internet access or vehicle
              telemetry behind it. If nothing matches confidently, it says so instead of guessing.
            </p>
            <Link className="assistant-route" href="/validation">
              See the evidence ladder <span aria-hidden="true">→</span>
            </Link>
          </div>
        </MotionReveal>
      </div>
    </>
  );
}
