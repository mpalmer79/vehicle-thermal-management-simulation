/**
 * Shared geometry for the VTMS thermal-circuit visuals.
 *
 * This is a system schematic of the VTMS-V1 model boundary. It is not CAD geometry,
 * CFD output, or a spatial representation of a real engine bay. Node placement is
 * chosen for readability of the energy path, not for physical dimension.
 *
 * Two layouts are provided so the same circuit stays legible on narrow viewports.
 * SVG carries the circuit; text labels are rendered as an HTML overlay so they keep
 * real CSS type sizes at any width.
 */

export type SchematicNodeId =
  | "engine"
  | "coolant"
  | "thermostat"
  | "bypass"
  | "radiator"
  | "fan"
  | "pump"
  | "ambient";

export type SchematicShape =
  | { kind: "rect"; x: number; y: number; width: number; height: number; radius: number }
  | { kind: "diamond"; cx: number; cy: number; half: number }
  | { kind: "circle"; cx: number; cy: number; r: number }
  | { kind: "marker"; cx: number; cy: number };

export type SchematicNode = {
  id: SchematicNodeId;
  shape: SchematicShape;
  /** Overlay anchor as a percentage of the viewBox, used for HTML labels. */
  labelX: number;
  labelY: number;
};

export type SchematicPathId =
  | "engineHeat"
  | "hotCoolant"
  | "toRadiator"
  | "bypass"
  | "radiatorReturn"
  | "returnTrunk";

export type SchematicPath = {
  id: SchematicPathId;
  d: string;
  /** Which flow quantity drives this path's animation and weight. */
  driver: "engineHeat" | "pumpFlow" | "radiatorFlow" | "bypassFlow" | "radiatorHeat";
};

export type SchematicLayout = {
  name: "landscape" | "portrait";
  viewBox: string;
  width: number;
  height: number;
  nodes: SchematicNode[];
  paths: SchematicPath[];
  /** Air-side lanes, drawn behind the radiator and fan. */
  airLanes: string[];
  /** Air leaving the system toward the ambient sink. */
  ambientLanes: string[];
};

const pct = (value: number, total: number) => Number(((value / total) * 100).toFixed(3));

export const landscapeLayout: SchematicLayout = {
  name: "landscape",
  viewBox: "0 0 780 500",
  width: 780,
  height: 500,
  nodes: [
    {
      id: "engine",
      shape: { kind: "rect", x: 56, y: 56, width: 190, height: 134, radius: 16 },
      labelX: pct(151, 780),
      labelY: pct(123, 500),
    },
    {
      id: "coolant",
      shape: { kind: "rect", x: 330, y: 56, width: 150, height: 134, radius: 16 },
      labelX: pct(405, 780),
      labelY: pct(123, 500),
    },
    {
      id: "thermostat",
      shape: { kind: "diamond", cx: 536, cy: 123, half: 32 },
      labelX: pct(536, 780),
      labelY: pct(64, 500),
    },
    {
      id: "radiator",
      shape: { kind: "rect", x: 566, y: 196, width: 150, height: 132, radius: 14 },
      labelX: pct(641, 780),
      labelY: pct(262, 500),
    },
    {
      id: "fan",
      shape: { kind: "circle", cx: 500, cy: 262, r: 42 },
      labelX: pct(500, 780),
      labelY: pct(330, 500),
    },
    {
      id: "bypass",
      shape: { kind: "marker", cx: 400, cy: 215 },
      labelX: pct(280, 780),
      labelY: pct(178, 500),
    },
    {
      id: "pump",
      shape: { kind: "circle", cx: 205, cy: 420, r: 26 },
      labelX: pct(205, 780),
      labelY: pct(468, 500),
    },
    {
      id: "ambient",
      shape: { kind: "marker", cx: 350, cy: 300 },
      labelX: pct(348, 780),
      labelY: pct(318, 500),
    },
  ],
  paths: [
    { id: "engineHeat", d: "M250,123 L326,123", driver: "engineHeat" },
    { id: "hotCoolant", d: "M480,123 L504,123", driver: "pumpFlow" },
    { id: "toRadiator", d: "M568,123 L641,123 L641,196", driver: "radiatorFlow" },
    { id: "bypass", d: "M536,155 L536,215 L272,215 L272,420", driver: "bypassFlow" },
    { id: "radiatorReturn", d: "M641,328 L641,420", driver: "radiatorFlow" },
    { id: "returnTrunk", d: "M641,420 L151,420 L151,190", driver: "pumpFlow" },
  ],
  airLanes: ["M770,222 L546,222", "M770,262 L546,262", "M770,302 L546,302"],
  ambientLanes: ["M458,232 L398,232", "M458,262 L392,262", "M458,292 L398,292"],
};

export const portraitLayout: SchematicLayout = {
  name: "portrait",
  viewBox: "0 0 380 660",
  width: 380,
  height: 660,
  nodes: [
    {
      id: "engine",
      shape: { kind: "rect", x: 24, y: 28, width: 148, height: 92, radius: 14 },
      labelX: pct(98, 380),
      labelY: pct(74, 660),
    },
    {
      id: "coolant",
      shape: { kind: "rect", x: 212, y: 28, width: 144, height: 92, radius: 14 },
      labelX: pct(284, 380),
      labelY: pct(74, 660),
    },
    {
      id: "thermostat",
      shape: { kind: "diamond", cx: 284, cy: 182, half: 28 },
      labelX: pct(284, 380),
      labelY: pct(232, 660),
    },
    {
      id: "radiator",
      shape: { kind: "rect", x: 196, y: 268, width: 160, height: 116, radius: 12 },
      labelX: pct(276, 380),
      labelY: pct(326, 660),
    },
    {
      id: "fan",
      shape: { kind: "circle", cx: 276, cy: 452, r: 36 },
      labelX: pct(334, 380),
      labelY: pct(452, 660),
    },
    {
      id: "bypass",
      shape: { kind: "marker", cx: 112, cy: 300 },
      labelX: pct(152, 380),
      labelY: pct(316, 660),
    },
    {
      id: "pump",
      shape: { kind: "circle", cx: 82, cy: 520, r: 22 },
      labelX: pct(82, 380),
      labelY: pct(576, 660),
    },
    {
      id: "ambient",
      shape: { kind: "marker", cx: 130, cy: 232 },
      labelX: pct(136, 380),
      labelY: pct(224, 660),
    },
  ],
  paths: [
    { id: "engineHeat", d: "M172,74 L208,74", driver: "engineHeat" },
    { id: "hotCoolant", d: "M284,120 L284,154", driver: "pumpFlow" },
    { id: "toRadiator", d: "M312,182 L344,182 L344,268", driver: "radiatorFlow" },
    { id: "bypass", d: "M256,182 L112,182 L112,520", driver: "bypassFlow" },
    { id: "radiatorReturn", d: "M204,384 L204,520", driver: "radiatorFlow" },
    { id: "returnTrunk", d: "M204,520 L52,520 L52,120", driver: "pumpFlow" },
  ],
  airLanes: ["M220,616 L220,236", "M260,616 L260,236", "M300,616 L300,236"],
  ambientLanes: ["M220,258 L220,220", "M260,258 L260,220", "M300,258 L300,220"],
};

export const nodeLabels: Record<SchematicNodeId, { short: string; chip: string; title: string; role: string }> = {
  engine: {
    short: "ENG",
    chip: "Engine",
    title: "Engine structure",
    role: "Lumped engine thermal mass. Receives wall heat from combustion and rejects it to coolant and ambient.",
  },
  coolant: {
    short: "CLT",
    chip: "Coolant",
    title: "Engine-side coolant",
    role: "Bulk coolant thermal storage. Transports engine heat toward the thermostat split.",
  },
  thermostat: {
    short: "THM",
    chip: "Thermostat",
    title: "Thermostat",
    role: "Temperature-driven split between the radiator branch and the bypass branch.",
  },
  bypass: {
    short: "BYP",
    chip: "Bypass",
    title: "Bypass branch",
    role: "Coolant that returns to the engine without passing through the radiator.",
  },
  radiator: {
    short: "RAD",
    chip: "Radiator",
    title: "Radiator",
    role: "Crossflow effectiveness-NTU heat exchanger rejecting coolant heat to the air stream.",
  },
  fan: {
    short: "FAN",
    chip: "Fan / air",
    title: "Fan and air side",
    role: "Ram-air capture plus commanded electric-fan volume flow through the radiator face.",
  },
  pump: {
    short: "PMP",
    chip: "Pump",
    title: "Coolant pump",
    role: "Engine-speed-driven coolant mass flow, scaled by pump health.",
  },
  ambient: {
    short: "AMB",
    chip: "Ambient",
    title: "Ambient sink",
    role: "Boundary condition receiving rejected heat at the scenario ambient temperature.",
  },
};
