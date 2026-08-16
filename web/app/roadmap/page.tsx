import type { Metadata } from "next";

export const metadata: Metadata = { title: "Maturity Roadmap" };

const steps = [
  ["NOW", "VTMS-V1", "Generic physics simulation", "Frozen model, Python engine, verification suite, validation toolkit, and UI foundation."],
  ["NEXT", "Controlled validation", "Calibrated and holdout tested", "Argonne D3 calibration using a preregistered four-parameter subset, followed by untouched holdout tests."],
  ["V2", "Vehicle-calibrated simulation", "OBD-II / CAN replay", "Vehicle-specific parameter sets and replay of measured operating inputs without claiming live synchronization."],
  ["FUTURE", "Connected model", "State estimation", "Synchronized physical vehicle telemetry, state updates, and continuous vehicle-specific prediction."],
  ["TARGET", "Digital twin", "Vehicle-specific synchronized model", "Only after persistent physical linkage, state estimation, calibration, prediction, and evidence justify the term."],
];

export default function RoadmapPage() {
  return <><header className="page-header"><span className="eyebrow">MATURITY, NOT MARKETING</span><h1>Roadmap to a Digital Twin</h1><p>VTMS keeps future capability visible without confusing it with what the model can prove today.</p></header><section className="roadmap">{steps.map(([tag, title, subtitle, copy], index) => <article key={title} className={index === 0 ? "current" : ""}><span className="roadmap-index">{String(index + 1).padStart(2, "0")}</span><div><small>{tag}</small><h2>{title}</h2><strong>{subtitle}</strong><p>{copy}</p></div></article>)}</section></>;
}
