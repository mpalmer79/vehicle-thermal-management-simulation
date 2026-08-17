import { CircuitDrawing } from "@/components/visuals/circuit-drawing";
import { landscapeLayout, portraitLayout, type SchematicLayout, type SchematicNodeId } from "@/lib/schematic-geometry";

const ARIA =
  "Schematic of the VTMS-V1 cooling circuit: engine heat enters the coolant, a thermostat splits flow between a bypass branch and the radiator, and ram plus fan airflow carries radiator heat to ambient.";

const callouts: Array<{ id: SchematicNodeId; label: string; detail?: string }> = [
  { id: "engine", label: "Engine", detail: "heat source" },
  { id: "coolant", label: "Coolant", detail: "transport" },
  { id: "thermostat", label: "Thermostat", detail: "split" },
  { id: "radiator", label: "Radiator", detail: "rejection" },
  { id: "fan", label: "Fan", detail: "air side" },
  { id: "bypass", label: "Bypass" },
  { id: "pump", label: "Pump" },
  { id: "ambient", label: "Ambient" },
];

function Labels({ layout }: { layout: SchematicLayout }) {
  return (
    <div className="circuit-labels" aria-hidden="true">
      {callouts.map((callout) => {
        const node = layout.nodes.find((item) => item.id === callout.id)!;
        return (
          <span
            className={`circuit-label label-${callout.id}`}
            key={callout.id}
            style={{ left: `${node.labelX}%`, top: `${node.labelY}%` }}
          >
            <b>{callout.label}</b>
            {callout.detail && <i>{callout.detail}</i>}
          </span>
        );
      })}
    </div>
  );
}

/**
 * Anatomy view of the VTMS-V1 cooling circuit for the Overview hero. It is an
 * engineering infographic only: it carries no simulation values, and it does not
 * represent real engine-bay geometry.
 *
 * Both layouts are rendered and selected in CSS so the diagram stays legible from
 * 360 px upward without a client-side measurement pass.
 */
export function ThermalSystemHero() {
  return (
    <figure className="thermal-hero">
      <div className="thermal-hero-stage wide-only">
        <CircuitDrawing ariaLabel={ARIA} idPrefix="heroWide" layout={landscapeLayout} />
        <Labels layout={landscapeLayout} />
      </div>

      <div className="thermal-hero-stage narrow-only">
        <CircuitDrawing ariaLabel={ARIA} idPrefix="heroNarrow" layout={portraitLayout} />
        <Labels layout={portraitLayout} />
      </div>

      <figcaption>
        <span className="flow-key coolant">Coolant</span>
        <span className="flow-key heat">Engine heat</span>
        <span className="flow-key bypass">Bypass</span>
        <span className="flow-key air">Airflow</span>
        <em>System schematic · not engine-bay geometry</em>
      </figcaption>
    </figure>
  );
}
