/**
 * Structured scenario intelligence for the VTMS Knowledge Assistant.
 *
 * Two authoritative sources are joined here and nothing is re-typed by hand:
 *
 * - `lib/scenarios.ts`          — the canonical scenario *inputs* (ambient, rpm, load,
 *                                 vehicle speed, duration, category, behavior label).
 * - `lib/canonical-previews.ts` — the canonical scenario *outputs*, produced by the
 *                                 authoritative VTMS-V1 Python engine through
 *                                 `generate_ui_previews.py`.
 *
 * Every number the assistant quotes flows from one of those two files. Nothing is
 * computed thermally here; the only arithmetic is comparison and ordering of values
 * the engine already produced, which is the same class of deterministic reduction
 * `ResultSnapshot` already performs on returned results.
 *
 * Language rules for anything built on this module:
 *
 * - Outputs are "VTMS-V1 canonical simulation output", never measured telemetry.
 * - An ordering by temperature is a model-output ordering, never a real-world
 *   severity, safety, or damage ranking.
 */

import { previewFor } from "./canonical-previews";
import { scenarios, type ScenarioCardData } from "./scenarios";

/** Attached to any answer that quotes a canonical number. */
export const CANONICAL_OUTPUT_PROVENANCE =
  "VTMS-V1 canonical simulation output, computed by the Python engine. Not measured vehicle telemetry.";

/** Attached whenever scenarios are ordered by a modelled temperature. */
export const RANKING_CAVEAT =
  "This orders VTMS-V1 model output only. It is not a real-world severity, safety, or damage ranking — VTMS-V1 does not model pressure, boiling, or engine damage.";

export type ScenarioConditions = {
  ambientC: number;
  rpm: number;
  loadPercent: number;
  speedKmh: number;
  durationS: number;
};

export type ScenarioOutput = {
  engineEndC: number;
  coolantEndC: number;
  enginePeakC: number;
  coolantPeakC: number;
  thermostatFraction: number;
  fanFraction: number;
  radiatorHeatW: number;
  airFlowKgS: number;
  pumpFlowKgS: number;
  normalizedResidual: number;
  warnings: string[];
};

export type ScenarioFacts = {
  id: string;
  name: string;
  category: ScenarioCardData["category"];
  behavior: string;
  purpose: string;
  basedOn?: string;
  conditions: ScenarioConditions;
  /** Present for every canonical scenario; absent only if a preview were missing. */
  output?: ScenarioOutput;
};

export const SCENARIO_IDS = scenarios.map((scenario) => scenario.id);

function toFacts(card: ScenarioCardData): ScenarioFacts {
  const preview = previewFor(card.id);

  return {
    id: card.id,
    name: card.name,
    category: card.category,
    behavior: card.behavior,
    purpose: card.purpose,
    basedOn: card.basedOn,
    conditions: {
      ambientC: card.ambient,
      rpm: card.rpm,
      loadPercent: card.load,
      speedKmh: card.speedKmh,
      durationS: card.duration,
    },
    output: preview && {
      engineEndC: preview.endState.engineC,
      coolantEndC: preview.endState.coolantC,
      enginePeakC: preview.peak.engineC,
      coolantPeakC: preview.peak.coolantC,
      thermostatFraction: preview.endState.thermostatFraction,
      fanFraction: preview.endState.fanFraction,
      radiatorHeatW: preview.endState.radiatorHeatW,
      airFlowKgS: preview.endState.airFlowKgS,
      pumpFlowKgS: preview.endState.pumpFlowKgS,
      normalizedResidual: preview.energyBalance.normalizedResidual,
      warnings: preview.warnings,
    },
  };
}

const FACTS: ScenarioFacts[] = scenarios.map(toFacts);
const FACTS_BY_ID = new Map(FACTS.map((facts) => [facts.id, facts]));

export const allScenarioFacts = (): ScenarioFacts[] => FACTS;

export const scenarioFacts = (id: string): ScenarioFacts | undefined => FACTS_BY_ID.get(id);

export const scenariosInCategory = (category: ScenarioCardData["category"]): ScenarioFacts[] =>
  FACTS.filter((facts) => facts.category === category);

/* ---------------------------------------------------------------- formatting */

export const degrees = (value: number) => `${value.toFixed(1)} °C`;
export const seconds = (value: number) => `${value.toFixed(0)} s`;
export const minutes = (value: number) => `${(value / 60).toFixed(0)} min`;
const percent = (value: number) => `${(value * 100).toFixed(0)}%`;

export const speedLabel = (kmh: number) => (kmh === 0 ? "stationary" : `${kmh.toFixed(0)} km/h`);

/** Compact condition line used wherever a scenario is described. */
export function conditionSummary(facts: ScenarioFacts): string {
  const { ambientC, rpm, loadPercent, speedKmh, durationS } = facts.conditions;
  return `${ambientC} °C ambient · ${rpm} rpm · ${loadPercent}% load · ${speedLabel(speedKmh)} · ${seconds(durationS)}`;
}

/** What the scenario changes relative to its baseline, in the model's own terms. */
export function faultSummary(facts: ScenarioFacts): string {
  const base = facts.basedOn ? ` Based on ${facts.basedOn}.` : "";
  if (facts.category === "Baseline") return `Baseline operating condition, no fault applied.${base}`;
  return `${facts.category}: ${facts.purpose.toLowerCase()}.${base}`;
}

/** Deterministic readouts of the canonical end state. */
export function outputFacts(facts: ScenarioFacts): string[] {
  const output = facts.output;
  if (!output) return [];

  const lines = [
    `Ends at ${degrees(output.engineEndC)} engine and ${degrees(output.coolantEndC)} coolant.`,
    `Peak ${degrees(output.enginePeakC)} engine, ${degrees(output.coolantPeakC)} coolant.`,
    `Thermostat ${percent(output.thermostatFraction)} open, fan at ${percent(output.fanFraction)} at the final sample.`,
  ];

  if (output.warnings.length > 0) {
    lines.push(`Carries a model caution: ${output.warnings[0]}`);
  }

  return lines;
}

/* ---------------------------------------------------------------- comparison */

export type ScenarioDifference = { label: string; a: string; b: string };

export type ScenarioComparison = {
  a: ScenarioFacts;
  b: ScenarioFacts;
  /** Input conditions that genuinely differ between the two scenarios. */
  differences: ScenarioDifference[];
  /** Shared baseline when both derive from the same one. */
  sharedBaseline?: string;
  /** Model-output comparison, expressed without severity language. */
  outcome?: string;
};

const CONDITION_ROWS: [string, (facts: ScenarioFacts) => string, (facts: ScenarioFacts) => number][] = [
  ["Ambient", (f) => `${f.conditions.ambientC} °C`, (f) => f.conditions.ambientC],
  ["Engine speed", (f) => `${f.conditions.rpm} rpm`, (f) => f.conditions.rpm],
  ["Load", (f) => `${f.conditions.loadPercent}%`, (f) => f.conditions.loadPercent],
  ["Vehicle speed", (f) => speedLabel(f.conditions.speedKmh), (f) => f.conditions.speedKmh],
  ["Duration", (f) => seconds(f.conditions.durationS), (f) => f.conditions.durationS],
];

export function compareScenarios(aId: string, bId: string): ScenarioComparison | undefined {
  const a = scenarioFacts(aId);
  const b = scenarioFacts(bId);
  if (!a || !b || a.id === b.id) return undefined;

  const differences: ScenarioDifference[] = [];

  for (const [label, format, value] of CONDITION_ROWS) {
    if (value(a) !== value(b)) differences.push({ label, a: format(a), b: format(b) });
  }

  if (a.category !== b.category || a.purpose !== b.purpose) {
    differences.push({ label: "What changes", a: faultSummary(a), b: faultSummary(b) });
  }

  const sharedBaseline = a.basedOn && a.basedOn === b.basedOn ? a.basedOn : undefined;

  let outcome: string | undefined;
  if (a.output && b.output) {
    const deltaEngine = a.output.engineEndC - b.output.engineEndC;
    const deltaCoolant = a.output.coolantEndC - b.output.coolantEndC;

    if (Math.abs(deltaEngine) < 0.05 && Math.abs(deltaCoolant) < 0.05) {
      outcome = `Both canonical runs finish at the same modelled state: ${degrees(a.output.engineEndC)} engine and ${degrees(a.output.coolantEndC)} coolant.`;
    } else {
      const hotter = deltaEngine > 0 ? a : b;
      const cooler = deltaEngine > 0 ? b : a;
      outcome = `${hotter.id} finishes ${degrees(Math.abs(deltaEngine))} higher on engine temperature than ${cooler.id} in the canonical output (${degrees(hotter.output!.engineEndC)} against ${degrees(cooler.output!.engineEndC)}).`;
    }
  }

  return { a, b, differences, sharedBaseline, outcome };
}

/* ------------------------------------------------------------------- ranking */

export type RankingMetric =
  | "engineEndC"
  | "coolantEndC"
  | "enginePeakC"
  | "coolantPeakC"
  | "durationS";

export const RANKING_LABELS: Record<RankingMetric, string> = {
  engineEndC: "final engine temperature",
  coolantEndC: "final coolant temperature",
  enginePeakC: "peak engine temperature",
  coolantPeakC: "peak coolant temperature",
  durationS: "run duration",
};

export type RankedScenario = { facts: ScenarioFacts; value: number; display: string };

export type ScenarioRanking = {
  metric: RankingMetric;
  label: string;
  direction: "highest" | "lowest";
  entries: RankedScenario[];
};

function metricValue(facts: ScenarioFacts, metric: RankingMetric): number | undefined {
  if (metric === "durationS") return facts.conditions.durationS;
  return facts.output?.[metric];
}

export function rankScenarios(
  metric: RankingMetric,
  direction: "highest" | "lowest" = "highest",
): ScenarioRanking {
  const entries: RankedScenario[] = [];

  for (const facts of FACTS) {
    const value = metricValue(facts, metric);
    if (value === undefined) continue;
    entries.push({
      facts,
      value,
      display: metric === "durationS" ? seconds(value) : degrees(value),
    });
  }

  entries.sort((left, right) => (direction === "highest" ? right.value - left.value : left.value - right.value));

  return { metric, label: RANKING_LABELS[metric], direction, entries };
}
