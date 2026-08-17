import Link from "next/link";

import { MotionReveal } from "@/components/motion-reveal";
import { PlaybackWorkspace } from "@/components/playback-workspace";
import { PathGlyph } from "@/components/visuals/path-glyph";
import { ThermalSystemHero } from "@/components/visuals/thermal-system-hero";

const productPath = [
  {
    kind: "configure" as const,
    step: "01",
    eyebrow: "SIMULATE",
    title: "Set the operating condition",
    copy: "Nine frozen canonical tests, plus custom conditions and fault states.",
    href: "/simulate",
    cta: "Simulation Lab",
  },
  {
    kind: "observe" as const,
    step: "02",
    eyebrow: "WATCH THE SYSTEM",
    title: "Follow energy through the loop",
    copy: "Engine heat, thermostat split, bypass, radiator rejection, and air side at any selected time.",
    href: "/system",
    cta: "System Explorer",
  },
  {
    kind: "evidence" as const,
    step: "03",
    eyebrow: "REVIEW THE EVIDENCE",
    title: "Separate verification from validation",
    copy: "Numerical verification is complete. Controlled physical validation is not.",
    href: "/validation",
    cta: "Validation Evidence",
  },
];

const modelFacts = [
  ["MODEL", "VTMS-V1"],
  ["EQUATIONS", "EM-V1"],
  ["STATES", "2 transient"],
  ["SOLVER", "RK45"],
  ["RADIATOR", "ε-NTU"],
];

export default function OverviewPage() {
  return (
    <>
      <section className="hero">
        <div className="hero-lede">
          <span className="eyebrow">VTMS-V1 · PHYSICS-BASED AUTOMOTIVE THERMAL SIMULATION</span>
          <h1>See where the heat goes.</h1>
          <p>Transient engine, coolant, and radiator behavior computed by a frozen physics model.</p>
        </div>

        <ThermalSystemHero />

        <div className="hero-tail">
          <div className="hero-actions">
            <Link className="button primary" href="/simulate">Open Simulation Lab</Link>
            <Link className="button secondary" href="/validation">Review validation evidence</Link>
          </div>
          <dl className="spec-strip">
            {modelFacts.map(([term, value]) => (
              <div key={term}><dt>{term}</dt><dd>{value}</dd></div>
            ))}
          </dl>
          <p className="hero-standing">
            <span className="standing-dot verified" aria-hidden="true" />
            <span>Numerically verified</span>
            <span className="standing-dot pending" aria-hidden="true" />
            <span>Controlled validation pending</span>
            <Link href="/model">Model boundary →</Link>
          </p>
        </div>
      </section>

      <MotionReveal className="overview-preview">
        <PlaybackWorkspace mode="overview" />
      </MotionReveal>

      <MotionReveal className="product-path">
        {productPath.map((item, index) => (
          <article className={`path-step step-${item.kind}`} key={item.step} style={{ transitionDelay: `${index * 70}ms` }}>
            <div className="path-step-visual">
              <PathGlyph kind={item.kind} />
              <span className="path-step-index">{item.step}</span>
            </div>
            <span className="eyebrow">{item.eyebrow}</span>
            <h3>{item.title}</h3>
            <p>{item.copy}</p>
            <Link className="path-step-cta" href={item.href}>{item.cta} <span aria-hidden="true">→</span></Link>
          </article>
        ))}
      </MotionReveal>
    </>
  );
}
