export type EvidenceStage = {
  number: string;
  title: string;
  state: "complete" | "active" | "future";
  description: string;
};

const stateLabel: Record<EvidenceStage["state"], string> = {
  complete: "Complete",
  active: "In preparation",
  future: "Not started",
};

/**
 * The verification / plausibility / calibration / validation ladder as a timeline.
 * State is carried by an explicit text label as well as by color and marker shape.
 */
export function EvidenceTimeline({ stages }: { stages: EvidenceStage[] }) {
  return (
    <ol className="evidence-timeline">
      {stages.map((stage) => (
        <li className={`evidence-step ${stage.state}`} key={stage.number}>
          <span aria-hidden="true" className="evidence-marker">
            {stage.state === "complete" ? "✓" : stage.number}
          </span>
          <span className="evidence-state">{stateLabel[stage.state]}</span>
          <h3>{stage.title}</h3>
          <p>{stage.description}</p>
        </li>
      ))}
    </ol>
  );
}
