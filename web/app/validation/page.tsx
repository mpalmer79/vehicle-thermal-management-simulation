import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

import { MotionReveal } from "@/components/motion-reveal";
import { EvidenceTimeline, type EvidenceStage } from "@/components/visuals/evidence-timeline";
import { ValidationTakeaway } from "@/components/visuals/validation-takeaway";

export const metadata: Metadata = { title: "Validation Evidence" };

const stages: EvidenceStage[] = [
  {
    number: "01",
    title: "Numerical verification",
    state: "complete",
    description: "Does the implementation solve the frozen equations consistently?",
  },
  {
    number: "02",
    title: "External plausibility",
    state: "complete",
    description: "Does a generic model show recognizable behavior against independent road telemetry?",
  },
  {
    number: "03",
    title: "Controlled calibration",
    state: "active",
    description: "Argonne data are received; qualify signals and freeze physical bounds before fitting.",
  },
  {
    number: "04",
    title: "Blind holdout validation",
    state: "future",
    description: "Predict untouched controlled experiments after calibration is frozen.",
  },
];

const kitMetrics = [
  ["RMSE", "21.40 °C"],
  ["MAE", "16.50 °C"],
  ["Mean bias", "+16.13 °C"],
  ["Final error", "-0.79 °C"],
];

const controlledPipeline = [
  ["Acquire", "complete"],
  ["Hash", "complete"],
  ["Map", "active"],
  ["Calibrate", "queued"],
  ["Freeze", "queued"],
  ["Holdout", "queued"],
  ["Report", "queued"],
] as const;

const argonneFacts = [
  ["Received tests", "18"],
  ["CAL candidate", "71207062"],
  ["Primary holdout", "71207063"],
  ["Heat evidence", "Direct fuel flow"],
];

export default function ValidationPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">MODEL EVIDENCE</span>
        <h1>Validation Evidence</h1>
        <p>Verification, plausibility, calibration, and validation are kept separate on purpose.</p>
      </header>

      <MotionReveal as="div">
        <EvidenceTimeline stages={stages} />
      </MotionReveal>

      <MotionReveal className="validation-panel">
        <div className="section-head">
          <div>
            <span className="eyebrow">KIT EXTERNAL PLAUSIBILITY</span>
            <h2>First untouched real-world comparison</h2>
          </div>
          <span className="fixture-badge">No parameter tuning</span>
        </div>

        <div className="validation-grid">
          <div className="validation-chart">
            <Image alt="Measured versus predicted coolant temperature" height={520} src="/validation/measured-vs-predicted.svg" unoptimized width={900} />
          </div>

          <div className="validation-side">
            <ValidationTakeaway headline="Warm-up too fast, final region similar">
              <p>
                The mismatch is preserved as evidence rather than tuned away. This is plausibility
                evidence against independent OBD-II telemetry, not controlled validation.
              </p>
            </ValidationTakeaway>

            <div className="validation-metrics">
              {kitMetrics.map(([label, value]) => (
                <div key={label}><span>{label}</span><strong>{value}</strong></div>
              ))}
            </div>
          </div>
        </div>

        <div className="residual-chart">
          <Image alt="Prediction residual versus time" height={520} src="/validation/residual.svg" unoptimized width={900} />
        </div>
      </MotionReveal>

      <MotionReveal className="controlled-panel">
        <div className="section-head">
          <div>
            <span className="eyebrow">CONTROLLED PHYSICAL VALIDATION</span>
            <h2>Argonne D3 data received</h2>
          </div>
          <span className="status-pill pending">Stage 3 of 7</span>
        </div>

        <p>
          Argonne supplied comprehensive 2012 Ford Focus dynamometer files on August 17, 2026.
          The source artifacts and candidate runs are fingerprinted. Signal quality and preprocessing
          are being frozen before any parameter fit.
        </p>

        <div className="validation-metrics">
          {argonneFacts.map(([label, value]) => (
            <div key={label}><span>{label}</span><strong>{value}</strong></div>
          ))}
        </div>

        <ol className="pipeline">
          {controlledPipeline.map(([label, state]) => (
            <li className={state === "active" ? "awaiting" : ""} key={label}>
              <span aria-hidden="true" className="stage-dot" />
              <b>{label}</b>
              <small>
                {state === "complete" ? "✓ Complete" : state === "active" ? "In progress" : "Queued"}
              </small>
            </li>
          ))}
        </ol>

        <ValidationTakeaway headline="Calibration has not started">
          <p>
            CAL-01 is reserved for cold-start UDDS test 71207062 and hot-start UDDS test 71207063
            is reserved as the primary clean holdout. The received highway and US06 files have
            incomplete coolant-temperature coverage, so they are not currently qualified as
            full-cycle formal holdouts. Physical calibration bounds must still be justified and frozen.
          </p>
        </ValidationTakeaway>

        <div className="hero-actions">
          <Link className="button secondary" href="/model">Review model boundary</Link>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/docs/ARGONNE_D3_DATA_QUALIFICATION.md">Argonne qualification record ↗</a>
        </div>
      </MotionReveal>
    </>
  );
}
