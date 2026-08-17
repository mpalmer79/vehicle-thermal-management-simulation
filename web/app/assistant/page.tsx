import type { Metadata } from "next";
import Link from "next/link";

import { AssistantPanel } from "@/components/assistant/assistant-panel";
import { KnowledgeMap } from "@/components/assistant/knowledge-map";
import { MotionReveal } from "@/components/motion-reveal";

export const metadata: Metadata = {
  title: "VTMS Assistant",
  description:
    "Ask about the VTMS thermal model, canonical scenarios, verification and validation evidence, and system architecture. Answers come from a knowledge base bundled with this site.",
};

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
          <KnowledgeMap />

          <div className="assistant-honesty">
            <span className="eyebrow">HOW IT WORKS</span>
            <ol className="assistant-pipeline">
              <li>Reads the question</li>
              <li>Finds VTMS terms</li>
              <li>Matches the knowledge base</li>
              <li>Composes from approved facts</li>
            </ol>
            <p>
              No external AI service is contacted. There is no internet access and no vehicle
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
