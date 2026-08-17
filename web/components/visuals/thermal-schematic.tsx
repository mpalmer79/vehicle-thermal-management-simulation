"use client";

import { useId, useState } from "react";

import { CircuitDrawing, type FlowWeights } from "@/components/visuals/circuit-drawing";
import { c, flow, kw, pct } from "@/lib/format";
import {
  landscapeLayout,
  nodeLabels,
  portraitLayout,
  type SchematicLayout,
  type SchematicNodeId,
} from "@/lib/schematic-geometry";
import type { TimeSeriesPoint } from "@/lib/vtms-types";

const ARIA =
  "Interactive VTMS-V1 thermal circuit. Select engine, coolant, thermostat, bypass, radiator, fan, pump, or ambient to inspect its state at the selected simulation time.";

const nodeOrder: SchematicNodeId[] = [
  "engine",
  "coolant",
  "thermostat",
  "bypass",
  "radiator",
  "fan",
  "pump",
  "ambient",
];

const tone: Record<SchematicNodeId, string> = {
  engine: "engine",
  coolant: "coolant",
  thermostat: "control",
  bypass: "bypass",
  radiator: "radiator",
  fan: "air",
  pump: "coolant",
  ambient: "ambient",
};

/** Headline value shown on each node chip. Every value comes from the selected result point. */
function headline(id: SchematicNodeId, point: TimeSeriesPoint, ambientC: number | null) {
  switch (id) {
    case "engine": return c(point.engine_structure_temp_c);
    case "coolant": return c(point.coolant_temp_c);
    case "thermostat": return pct(point.thermostat_fraction);
    case "bypass": return flow(point.bypass_flow_kg_s);
    case "radiator": return kw(point.radiator_heat_w);
    case "fan": return pct(point.fan_fraction);
    case "pump": return flow(point.pump_flow_kg_s);
    case "ambient": return ambientC === null ? "—" : c(ambientC);
  }
}

/** Inspector rows, all read directly from the authoritative result point. */
function details(id: SchematicNodeId, point: TimeSeriesPoint, ambientC: number | null): Array<[string, string]> {
  switch (id) {
    case "engine":
      return [
        ["Structure temperature", c(point.engine_structure_temp_c)],
        ["Heat generated", kw(point.engine_heat_w)],
        ["To coolant", kw(point.engine_to_coolant_w)],
        ["To ambient", kw(point.engine_to_ambient_w)],
      ];
    case "coolant":
      return [
        ["Bulk temperature", c(point.coolant_temp_c)],
        ["Pump flow", flow(point.pump_flow_kg_s)],
        ["Received from engine", kw(point.engine_to_coolant_w)],
        ["Rejected at radiator", kw(point.radiator_heat_w)],
      ];
    case "thermostat":
      return [
        ["Opening", pct(point.thermostat_fraction)],
        ["To radiator", flow(point.radiator_flow_kg_s)],
        ["To bypass", flow(point.bypass_flow_kg_s)],
        ["Coolant temperature", c(point.coolant_temp_c)],
      ];
    case "bypass":
      return [
        ["Bypass flow", flow(point.bypass_flow_kg_s)],
        ["Bypass fraction", pct(1 - point.thermostat_fraction)],
        ["Radiator flow", flow(point.radiator_flow_kg_s)],
      ];
    case "radiator":
      return [
        ["Heat rejected", kw(point.radiator_heat_w)],
        ["Coolant flow", flow(point.radiator_flow_kg_s)],
        ["Outlet temperature", point.radiator_outlet_temp_c === null ? "no flow" : c(point.radiator_outlet_temp_c)],
        ["Effectiveness ε", point.radiator_effectiveness.toFixed(3)],
        ["NTU", point.radiator_ntu.toFixed(2)],
      ];
    case "fan":
      return [
        ["Fan command", pct(point.fan_fraction)],
        ["Air mass flow", flow(point.air_flow_kg_s)],
        ["Heat carried away", kw(point.radiator_heat_w)],
      ];
    case "pump":
      return [
        ["Coolant flow", flow(point.pump_flow_kg_s)],
        ["To radiator branch", flow(point.radiator_flow_kg_s)],
        ["To bypass branch", flow(point.bypass_flow_kg_s)],
      ];
    case "ambient":
      return [
        ["Ambient temperature", ambientC === null ? "—" : c(ambientC)],
        ["Radiator rejection", kw(point.radiator_heat_w)],
        ["Engine to ambient", kw(point.engine_to_ambient_w)],
        ["Air mass flow", flow(point.air_flow_kg_s)],
      ];
  }
}

/**
 * Relative magnitudes for flow animation. Each value is normalised against a reference
 * that is itself taken from the result, so the drawing shows proportion rather than an
 * invented absolute scale.
 */
function weightsFor(point: TimeSeriesPoint, reference: { pump: number; heat: number }): FlowWeights {
  const pumpRef = reference.pump || 1;
  const heatRef = reference.heat || 1;
  return {
    engineHeat: point.engine_to_coolant_w / heatRef,
    pumpFlow: point.pump_flow_kg_s / pumpRef,
    radiatorFlow: point.radiator_flow_kg_s / pumpRef,
    bypassFlow: point.bypass_flow_kg_s / pumpRef,
  };
}

function NodeButtons({
  layout,
  point,
  ambientC,
  selected,
  onSelect,
  idSuffix,
}: {
  layout: SchematicLayout;
  point: TimeSeriesPoint;
  ambientC: number | null;
  selected: SchematicNodeId;
  onSelect: (id: SchematicNodeId) => void;
  idSuffix: string;
}) {
  return (
    <div className="schematic-nodes">
      {nodeOrder.map((id) => {
        const node = layout.nodes.find((item) => item.id === id)!;
        return (
          <button
            aria-pressed={selected === id}
            className={`node-button tone-${tone[id]}${selected === id ? " selected" : ""}`}
            id={`node-${id}-${idSuffix}`}
            key={id}
            onClick={() => onSelect(id)}
            style={{ left: `${node.labelX}%`, top: `${node.labelY}%` }}
            type="button"
          >
            <b>{nodeLabels[id].chip}</b>
            <i>{headline(id, point, ambientC)}</i>
          </button>
        );
      })}
    </div>
  );
}

export function InteractiveThermalSchematic({
  point,
  ambientC = null,
  reference,
  caption,
}: {
  point: TimeSeriesPoint;
  ambientC?: number | null;
  reference: { pump: number; heat: number };
  caption?: string;
}) {
  const [selected, setSelected] = useState<SchematicNodeId>("engine");
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const weights = weightsFor(point, reference);
  const rows = details(selected, point, ambientC);
  const label = nodeLabels[selected];

  return (
    <div className="schematic">
      <div className="schematic-stage wide-only">
        <CircuitDrawing
          ariaLabel={ARIA}
          fanActive={point.fan_fraction > 0}
          idPrefix={`schemWide${uid}`}
          layout={landscapeLayout}
          selectedId={selected}
          weights={weights}
        />
        <NodeButtons
          ambientC={ambientC}
          idSuffix={`w${uid}`}
          layout={landscapeLayout}
          onSelect={setSelected}
          point={point}
          selected={selected}
        />
      </div>

      <div className="schematic-stage narrow-only">
        <CircuitDrawing
          ariaLabel={ARIA}
          fanActive={point.fan_fraction > 0}
          idPrefix={`schemNarrow${uid}`}
          layout={portraitLayout}
          selectedId={selected}
          weights={weights}
        />
        <NodeButtons
          ambientC={ambientC}
          idSuffix={`n${uid}`}
          layout={portraitLayout}
          onSelect={setSelected}
          point={point}
          selected={selected}
        />
      </div>

      <div className="schematic-inspector" role="region" aria-live="polite" aria-label="Selected component state">
        <div className="inspector-head">
          <div>
            <span className="eyebrow">SELECTED COMPONENT</span>
            <h3>{label.title}</h3>
          </div>
          <span className="fixture-badge">t = {point.time_s.toFixed(0)} s</span>
        </div>
        <p className="inspector-role">{label.role}</p>
        <dl className="inspector-values">
          {rows.map(([term, value]) => (
            <div key={term}><dt>{term}</dt><dd>{value}</dd></div>
          ))}
        </dl>
        {caption && <p className="muted-note">{caption}</p>}
      </div>
    </div>
  );
}
