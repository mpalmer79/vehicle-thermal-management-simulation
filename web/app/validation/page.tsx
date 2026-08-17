import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

import { MotionReveal } from "@/components/motion-reveal";
import { EvidenceTimeline, type EvidenceStage } from "@/components/visuals/evidence-timeline";
import { ValidationTakeaway } from "@/components/visuals/validation-takeaway";

export const metadata: Metadata = { title: "Validation Evidence" };

const stages: EvidenceStage[] = [
  { number: "01", title: "Numerical verification", state: "complete", description: "Does the implementation solve the frozen equations consistently?" },
  { number: "02", title: "External plausibility", state: "complete", description: "Does a generic model show recognizable behavior against independent road telemetry?" },
  { number: "03", title: "Controlled calibration preparation", state: "active", description: "Bounds and staged roles are frozen; exact mappings and manifests are next." },
  { number: "04", title: "Blind holdout validation", state: "future", description: "Predict untouched controlled experiments after both calibration stages are frozen." },
];

const kitMetrics = [["RMSE", "21.40 °C"], ["MAE", "16.50 °C"], ["Mean bias", "+16.13 °C"], ["Final error", "-0.79 °C"]];
const controlledPipeline = [["Acquire", "complete"], ["Hash", "complete"], ["Bounds", "complete"], ["Identify", "complete"], ["Stage", "complete"], ["Map", "active"], ["Calibrate", "queued"], ["Freeze", "queued"], ["Holdout", "queued"], ["Report", "queued"]] as const;
const argonneFacts = [["Received tests", "18"], ["Warm-up CAL", "71207062"], ["Radiator CAL", "71207057"], ["Primary holdout", "71207063"]];
const identifiabilityFacts = [["Warm-up rank", "4 of 4"], ["Condition number", "≈ 8.12"], ["Wall vs Cₑ cosine", "≈ -0.88"], ["Radiator UA sensitivity", "≈ 0.94% of strongest"]];

export default function ValidationPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">MODEL EVIDENCE</span><h1>Validation Evidence</h1>
        <p>Verification, plausibility, calibration, and validation are kept separate on purpose.</p>
      </header>

      <MotionReveal as="div"><EvidenceTimeline stages={stages} /></MotionReveal>

      <MotionReveal className="validation-panel">
        <div className="section-head"><div><span className="eyebrow">KIT EXTERNAL PLAUSIBILITY</span><h2>First untouched real-world comparison</h2></div><span className="fixture-badge">No parameter tuning</span></div>
        <div className="validation-grid">
          <div className="validation-chart"><Image alt="Measured versus predicted coolant temperature" height={520} src="/validation/measured-vs-predicted.svg" unoptimized width={900} /></div>
          <div className="validation-side">
            <ValidationTakeaway headline="Warm-up too fast, final region similar"><p>The mismatch is preserved as evidence rather than tuned away. This is plausibility evidence against independent OBD-II telemetry, not controlled validation.</p></ValidationTakeaway>
            <div className="validation-metrics">{kitMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
          </div>
        </div>
        <div className="residual-chart"><Image alt="Prediction residual versus time" height={520} src="/validation/residual.svg" unoptimized width={900} /></div>
      </MotionReveal>

      <MotionReveal className="controlled-panel">
        <div className="section-head"><div><span className="eyebrow">CONTROLLED PHYSICAL VALIDATION</span><h2>Argonne D3 pre-fit controls</h2></div><span className="status-pill pending">Mappings next</span></div>
        <p>Argonne supplied comprehensive 2012 Ford Focus dynamometer files on August 17, 2026. Physical bounds and the two-stage calibration structure are frozen before model residual inspection. Exact preprocessing and immutable manifests still have to be frozen before any physical fit.</p>
        <div className="validation-metrics">{argonneFacts.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
        <ol className="pipeline">{controlledPipeline.map(([label, state]) => <li className={state === "active" ? "awaiting" : ""} key={label}><span aria-hidden="true" className="stage-dot" /><b>{label}</b><small>{state === "complete" ? "✓ Complete" : state === "active" ? "In progress" : "Queued"}</small></li>)}</ol>

        <div className="section-head"><div><span className="eyebrow">PRE-FIT IDENTIFIABILITY</span><h2>One four-parameter warm-up fit is blocked</h2></div><span className="fixture-badge">Synthetic only</span></div>
        <div className="validation-metrics">{identifiabilityFacts.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>

        <ValidationTakeaway headline="CAL-01 is a three-parameter warm-up stage"><p>Cold-start test 71207062 may eventually fit wall heat fraction, effective engine thermal capacitance, and engine-to-coolant UA within their already-frozen bounds. Radiator UA remains fixed in this stage.</p></ValidationTakeaway>
        <ValidationTakeaway headline="CAL-RAD-01 reserves 71207057 for radiator UA"><p>The radiator stage was selected from source measurements before any VTMS residual was inspected. Its ECT is complete at 91 to 99 °C, mean dyno speed is about 57.31 mph, and about 92.65% of samples are at or above 40 mph while ECT is at or above 88 °C. Only radiator UA may move, after the CAL-01 snapshot is frozen.</p></ValidationTakeaway>
        <ValidationTakeaway headline="Holdouts remain untouched"><p>Hot-start test 71207063 remains the primary clean holdout and 55 mph warm-up test 71207052 remains a secondary holdout. No Argonne calibration or validation result exists yet.</p></ValidationTakeaway>

        <div className="hero-actions">
          <Link className="button secondary" href="/model">Review model boundary</Link>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/docs/ARGONNE_CALIBRATION_BOUNDS_AND_IDENTIFIABILITY.md">Bounds &amp; identifiability ↗</a>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/docs/ARGONNE_D3_DATA_QUALIFICATION.md">Argonne qualification ↗</a>
        </div>
      </MotionReveal>
    </>
  );
}
