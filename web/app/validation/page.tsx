import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

import { MotionReveal } from "@/components/motion-reveal";
import { EvidenceTimeline, type EvidenceStage } from "@/components/visuals/evidence-timeline";
import { ValidationTakeaway } from "@/components/visuals/validation-takeaway";

export const metadata: Metadata = { title: "Validation Evidence" };

const stages: EvidenceStage[] = [
  { number: "01", title: "Numerical verification", state: "complete", description: "The frozen equations pass conservation, convergence, component, and regression checks." },
  { number: "02", title: "External plausibility", state: "complete", description: "Independent KIT road telemetry exposed a warm-up mismatch without tuning." },
  { number: "03", title: "Controlled calibration", state: "complete", description: "Two preregistered Argonne stages were executed and frozen. Boundary behavior and a failed radiator stage are preserved." },
  { number: "04", title: "Independent holdouts", state: "complete", description: "The primary hot-start holdout and a separately reserved 55 mph confirmatory holdout both failed the project criteria with no retuning." },
];

const kitMetrics = [["RMSE", "21.40 °C"], ["MAE", "16.50 °C"], ["Mean bias", "+16.13 °C"], ["Final error", "-0.79 °C"]];
const cal01Metrics = [["RMSE", "3.72 °C"], ["MAE", "3.29 °C"], ["Mean bias", "-2.41 °C"], ["P90 error", "5.91 °C"]];
const calRadMetrics = [["RMSE", "5.73 °C"], ["MAE", "5.34 °C"], ["Mean bias", "-5.27 °C"], ["Radiator UA", "400.83 W/K"]];
const holdoutMetrics = [["RMSE", "8.59 °C"], ["MAE", "8.07 °C"], ["Mean bias", "-8.04 °C"], ["P90 error", "10.05 °C"]];
const secondaryMetrics = [["RMSE", "5.13 °C"], ["MAE", "4.11 °C"], ["Mean bias", "-4.01 °C"], ["P90 error", "8.40 °C"]];
const controlledPipeline = [["Acquire", "complete"], ["Hash", "complete"], ["Bounds", "complete"], ["Identify", "complete"], ["Stage", "complete"], ["Map", "complete"], ["Calibrate", "complete"], ["Freeze", "complete"], ["Holdout", "complete"], ["Report", "active"]] as const;

export default function ValidationPage() {
  return (
    <>
      <header className="page-header lean">
        <span className="eyebrow">MODEL EVIDENCE</span><h1>Validation Evidence</h1>
        <p>Verification, calibration, and validation are kept separate, including when the result is a failure.</p>
      </header>

      <MotionReveal as="div"><EvidenceTimeline stages={stages} /></MotionReveal>

      <MotionReveal className="validation-panel">
        <div className="section-head"><div><span className="eyebrow">KIT EXTERNAL PLAUSIBILITY</span><h2>First untouched real-world comparison</h2></div><span className="fixture-badge">No parameter tuning</span></div>
        <div className="validation-grid">
          <div className="validation-chart"><Image alt="Measured versus predicted coolant temperature" height={520} src="/validation/measured-vs-predicted.svg" unoptimized width={900} /></div>
          <div className="validation-side">
            <ValidationTakeaway headline="Warm-up too fast, final region similar"><p>The mismatch is preserved rather than tuned away. This is plausibility evidence against independent OBD-II telemetry, not controlled validation.</p></ValidationTakeaway>
            <div className="validation-metrics">{kitMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
          </div>
        </div>
        <div className="residual-chart"><Image alt="Prediction residual versus time" height={520} src="/validation/residual.svg" unoptimized width={900} /></div>
      </MotionReveal>

      <MotionReveal className="controlled-panel">
        <div className="section-head"><div><span className="eyebrow">CONTROLLED ARGONNE D3 PROGRAM</span><h2>Calibration completed, two independent holdouts failed</h2></div><span className="status-pill pending">Validation criteria not met</span></div>
        <p>The calibration bounds, source roles, preprocessing, and holdout reservations were frozen before their relevant residuals were opened. Every failed result below is preserved without widening bounds or retuning against holdout data.</p>
        <ol className="pipeline">{controlledPipeline.map(([label, state]) => <li className={state === "active" ? "awaiting" : ""} key={label}><span aria-hidden="true" className="stage-dot" /><b>{label}</b><small>{state === "complete" ? "✓ Complete" : "Reporting"}</small></li>)}</ol>

        <div className="section-head"><div><span className="eyebrow">CAL-01 · 71207062</span><h2>Cold-start warm-up calibration</h2></div><span className="fixture-badge">Thresholds met, calibration only</span></div>
        <div className="validation-metrics">{cal01Metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
        <ValidationTakeaway headline="The fit meets calibration-stage thresholds, but two parameters press against their bounds"><p>Wall heat fraction fitted to 0.4999 and engine-to-coolant UA to 2198.4 W/K, both within 1% of their frozen upper bounds. Effective engine capacitance fitted to 52.39 kJ/K. This is calibration evidence, not validation.</p></ValidationTakeaway>

        <div className="section-head"><div><span className="eyebrow">CAL-RAD-01 · 71207057</span><h2>Radiator-only calibration</h2></div><span className="status-pill pending">Outside project thresholds</span></div>
        <div className="validation-metrics">{calRadMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
        <ValidationTakeaway headline="The constrained radiator stage failed"><p>Radiator UA moved to 400.83 W/K, within 1% of the frozen lower bound, yet RMSE, MAE, bias, and P90 error all remained outside the criteria. The bound was not widened and CAL-01 parameters were not reopened.</p></ValidationTakeaway>

        <div className="section-head"><div><span className="eyebrow">VAL-HOT-01 · 71207063</span><h2>Primary blind physical holdout</h2></div><span className="status-pill pending">Formal holdout fail</span></div>
        <div className="validation-metrics">{holdoutMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
        <ValidationTakeaway headline="VTMS-V1 did not pass controlled physical validation"><p>The untouched hot-start run was executed once with the frozen staged parameter snapshot and no fitting. Final coolant prediction was 90.47 °C versus 99.0 °C measured, and the 90 °C arrival was about 125.6 s late. The formal decision is <strong>formal_holdout_acceptance_fail</strong>.</p></ValidationTakeaway>

        <div className="section-head"><div><span className="eyebrow">VAL-SSS-01 · 71207052</span><h2>Secondary confirmatory holdout</h2></div><span className="status-pill pending">Confirmatory fail</span></div>
        <div className="validation-metrics">{secondaryMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
        <ValidationTakeaway headline="A second operating profile shows the same final-temperature underprediction"><p>The separately reserved 55 mph warm-up run was locked and executed after the primary failure, with the same frozen parameters and no fitting. It narrowly missed RMSE and MAE limits, failed bias and P90 limits, and ended at 90.58 °C predicted versus 99.0 °C measured. Its 80 °C and 90 °C arrival timing checks passed.</p></ValidationTakeaway>
        <ValidationTakeaway headline="The evidence now points beyond parameter tuning"><p>Two independent holdouts fail with negative temperature bias while calibration parameters press against their frozen bounds. That pattern strengthens the case for a governed model-form revision. No holdout-driven retuning is permitted, and the generic production model remains unchanged.</p></ValidationTakeaway>

        <div className="hero-actions">
          <Link className="button secondary" href="/model">Review model boundary</Link>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/validation_outputs/ARGONNE_VAL_HOT_01_FORMAL_RESULT.json">Primary holdout ↗</a>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/validation_outputs/ARGONNE_VAL_SSS_01_CONFIRMATORY_RESULT.json">Secondary holdout ↗</a>
          <a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/docs/VALIDATION_GOVERNANCE.md">Validation governance ↗</a>
        </div>
      </MotionReveal>
    </>
  );
}
