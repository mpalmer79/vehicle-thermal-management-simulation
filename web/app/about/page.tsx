import type { Metadata } from "next";
import Link from "next/link";

import { BuildBlocks } from "@/components/about/build-blocks";
import { CreatorMonogram } from "@/components/about/creator-hero";
import { CreatorLinks } from "@/components/about/creator-links";
import { ExperiencePath } from "@/components/about/experience-path";
import { MotionReveal } from "@/components/motion-reveal";
import { CREATOR_LINKS, CREDIBILITY_NOTE, INTERSECTION, WHY_VTMS } from "@/lib/about-content";

export const metadata: Metadata = {
  title: "About the Creator",
  description:
    "Michael Palmer — 25+ years in automotive retail and dealership operations, dealer technology, and software/AI, and the creator of the VTMS thermal simulation platform.",
};

export default function AboutPage() {
  return (
    <>
      <section className="creator-hero">
        <div className="creator-lede">
          <span className="eyebrow">CREATOR OF VTMS</span>
          <h1>Built at the intersection of automotive experience, software, and engineering computation.</h1>
          <p>
            Michael Palmer — 25+ years in automotive retail and dealership operations, now building
            software, AI, and applied technical systems.
          </p>
          <CreatorLinks />
        </div>

        <div className="creator-visual">
          <CreatorMonogram />
        </div>

        <ul className="intersection-strip">
          {INTERSECTION.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <MotionReveal className="about-section">
        <div className="section-head">
          <div>
            <span className="eyebrow">THE PATH</span>
            <h2>From the showroom floor to a solver</h2>
          </div>
        </div>
        <ExperiencePath />
      </MotionReveal>

      <MotionReveal className="why-vtms">
        <div className="why-vtms-copy">
          <span className="eyebrow">WHY VTMS?</span>
          <p>{WHY_VTMS}</p>
        </div>
        <aside className="credibility-note">
          <span className="status-pill pending">Model standing</span>
          <p>{CREDIBILITY_NOTE}</p>
          <Link className="assistant-route" href="/validation">
            See the evidence ladder <span aria-hidden="true">→</span>
          </Link>
        </aside>
      </MotionReveal>

      <MotionReveal className="about-section">
        <div className="section-head">
          <div>
            <span className="eyebrow">WHAT I BUILD</span>
            <h2>Three working areas</h2>
          </div>
        </div>
        <BuildBlocks />
      </MotionReveal>

      <MotionReveal className="creator-cta">
        <div className="creator-cta-copy">
          <span className="eyebrow">NEXT</span>
          <h2>Explore the project</h2>
          <p>Run a scenario, follow the thermal loop, or ask the assistant about any of it.</p>
        </div>

        <div className="creator-cta-actions">
          <Link className="button primary" href="/simulate">
            Explore the project
          </Link>
          <a className="button secondary" href={CREATOR_LINKS.github} rel="noreferrer noopener" target="_blank">
            View GitHub ↗
          </a>
          <a className="button secondary" href={CREATOR_LINKS.linkedin} rel="noreferrer noopener" target="_blank">
            Connect on LinkedIn ↗
          </a>
        </div>

        <Link className="assistant-cross-link" href="/assistant">
          <span className="assistant-cross-glyph" aria-hidden="true">
            <svg viewBox="0 0 24 24" role="presentation">
              <circle className="al-ring" cx="12" cy="12" r="9" />
              <path className="al-loop" d="M6.6,15 Q12,19.6 17.4,15" />
              <circle className="al-core" cx="12" cy="9.8" r="3.2" />
            </svg>
          </span>
          <span>
            <strong>Ask the VTMS Assistant about this project</strong>
            <small>Answers from the knowledge base bundled with this site</small>
          </span>
          <i aria-hidden="true">→</i>
        </Link>

        <CreatorLinks tone="quiet" />
      </MotionReveal>
    </>
  );
}
