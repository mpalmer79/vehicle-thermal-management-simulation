import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = { title: "Validation Evidence" };

const stages = [
  ["01", "Numerical verification", "Complete", "Does the implementation solve the frozen equations consistently?"],
  ["02", "External plausibility", "Complete", "Does a generic model show physically recognizable behavior against independent road telemetry?"],
  ["03", "Controlled calibration", "Pending", "Fit only preregistered uncertain parameters using one qualified experiment."],
  ["04", "Blind holdout validation", "Pending", "Predict untouched controlled experiments after calibration is frozen."],
];

export default function ValidationPage() {
  return <>
    <header className="page-header"><span className="eyebrow">MODEL EVIDENCE</span><h1>Validation Evidence</h1><p>Verification, plausibility, calibration, and validation are deliberately separated so a numerical result cannot be mistaken for proven vehicle accuracy.</p></header>
    <section className="evidence-ladder">{stages.map(([number, title, status, description]) => <article key={number} className={status === "Complete" ? "complete" : "pending"}><span>{number}</span><div><small>{status}</small><h3>{title}</h3><p>{description}</p></div></article>)}</section>
    <section className="validation-panel"><div className="section-head"><div><span className="eyebrow">KIT EXTERNAL PLAUSIBILITY</span><h2>First untouched real-world comparison</h2></div><span className="fixture-badge">No parameter tuning</span></div><div className="validation-grid"><div className="validation-chart"><Image alt="Measured versus predicted coolant temperature" height={520} src="/validation/measured-vs-predicted.svg" unoptimized width={900} /></div><div className="validation-metrics"><div><span>RMSE</span><strong>21.40 °C</strong></div><div><span>MAE</span><strong>16.50 °C</strong></div><div><span>Mean bias</span><strong>+16.13 °C</strong></div><div><span>Final error</span><strong>-0.79 °C</strong></div><p>VTMS reaches a similar final temperature region but warms substantially too quickly. This mismatch is preserved as evidence rather than tuned away.</p></div></div><div className="residual-chart"><Image alt="Prediction residual versus time" height={520} src="/validation/residual.svg" unoptimized width={900} /></div></section>
    <section className="controlled-panel"><span className="eyebrow">CONTROLLED PHYSICAL VALIDATION</span><h2>Argonne D3 acquisition pending</h2><p>The preregistered protocol reserves calibration and holdout datasets before fitting begins. The V1 model remains frozen while the requested controlled data is pending.</p><div className="hero-actions"><Link className="button secondary" href="/model">Review model boundary</Link><a className="button secondary" href="https://github.com/mpalmer79/vehicle-thermal-management-simulation/blob/main/docs/VTMS_V1_Physical_Validation_Protocol.docx">Validation protocol ↗</a></div></section>
  </>;
}
