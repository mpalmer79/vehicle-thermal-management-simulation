/**
 * Run-aware readout foundation.
 *
 * When the visitor is on a computed-result route, the assistant may read the result
 * that is *already* in browser session storage and answer factual readout questions
 * about it. This is intentionally the narrowest possible interface:
 *
 * - It reads the same `vtms:run:{runId}` record `StoredRunResult` reads. It does not
 *   import anything from the Results components, and Results does not know it exists,
 *   so neither side is coupled to the other.
 * - It performs no thermal calculation. Every field is a direct read or the same class
 *   of deterministic reduction (max, first-crossing, threshold comparison) that
 *   `ResultSnapshot` already performs on returned results.
 * - It never diagnoses a mechanical condition, infers a damage or boiling limit, or
 *   judges safety. Those remain outside VTMS-V1 and outside the assistant.
 *
 * If no run is present for the current route the assistant simply has no run context,
 * and run-specific questions fall through to the knowledge base as before.
 */

import type { SimulationApiResponse } from "./vtms-types";

/** Energy-balance pass threshold used by the existing result surfaces. */
const ENERGY_BALANCE_TOLERANCE = 0.001;

export type RunReadout = {
  runId: string;
  scenarioId: string;
  scenarioName: string;
  modelId: string;
  equationSet: string;
  validationStatus: string;
  durationS: number;
  finalEngineC: number;
  finalCoolantC: number;
  peakEngineC: number;
  peakCoolantC: number;
  fanActivated: boolean;
  thermostatOpenedFraction: number;
  energyBalancePass: boolean;
  normalizedResidual: number;
  solverSuccess: boolean;
  warnings: string[];
};

/** `/results/<runId>` → `<runId>`. Returns null for any other route. */
export function runIdFromPathname(pathname: string): string | null {
  const match = /^\/results\/([^/]+)\/?$/.exec(pathname);
  if (!match) return null;
  const runId = decodeURIComponent(match[1]);
  // The demo route renders a build-time fixture, not a session-stored run.
  return runId === "demo-s03" ? null : runId;
}

export const runStorageKey = (runId: string) => `vtms:run:${runId}`;

/** Reduce a stored API response to the readout fields, with no further inference. */
export function readoutFromResponse(response: SimulationApiResponse): RunReadout | null {
  const result = response.result;
  const series = result.time_series;
  if (!series || series.length === 0) return null;

  const final = series[series.length - 1];

  return {
    runId: response.run_id,
    scenarioId: result.scenario_metadata.scenario_id,
    scenarioName: result.scenario_metadata.name,
    modelId: result.model_metadata.model_id,
    equationSet: result.model_metadata.equation_set,
    validationStatus: result.model_metadata.validation_status,
    durationS: result.scenario_metadata.duration_s,
    finalEngineC: final.engine_structure_temp_c,
    finalCoolantC: final.coolant_temp_c,
    peakEngineC: Math.max(...series.map((point) => point.engine_structure_temp_c)),
    peakCoolantC: Math.max(...series.map((point) => point.coolant_temp_c)),
    fanActivated: series.some((point) => point.fan_fraction > 0),
    thermostatOpenedFraction: final.thermostat_fraction,
    energyBalancePass: result.energy_balance.normalized_residual <= ENERGY_BALANCE_TOLERANCE,
    normalizedResidual: result.energy_balance.normalized_residual,
    solverSuccess: result.solver_diagnostics.success,
    warnings: result.warnings ?? [],
  };
}

/**
 * Read the run for a route from session storage.
 *
 * Returns null on the server, on any non-result route, or when the session does not
 * hold that run — computed results are session-scoped by design.
 */
export function readRunForPathname(pathname: string): RunReadout | null {
  const runId = runIdFromPathname(pathname);
  if (!runId) return null;
  if (typeof window === "undefined") return null;

  let raw: string | null = null;
  try {
    raw = window.sessionStorage.getItem(runStorageKey(runId));
  } catch {
    return null;
  }
  if (!raw) return null;

  try {
    return readoutFromResponse(JSON.parse(raw) as SimulationApiResponse);
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------ readout answers */

export type RunQuestionKind =
  | "final_temperature"
  | "peak_temperature"
  | "energy_balance"
  | "scenario_identity"
  | "duration"
  | "fan"
  | "solver";

const RUN_CUES: [RunQuestionKind, RegExp][] = [
  ["final_temperature", /\b(final|end|ending|finish\w*|last)\b.*\b(temperature|coolant|engine)\b|\bwhat is the final\b/],
  ["peak_temperature", /\b(peak|maximum|max|hottest|highest)\b.*\b(temperature|coolant|engine)\b/],
  ["energy_balance", /\benergy balance\b|\bdid energy\b|\benergy conserv\w*\b|\bresidual\b/],
  ["scenario_identity", /\bwhat scenario\b|\bwhich scenario is this\b|\bwhat is this run\b|\bwhat is this\b/],
  ["duration", /\bhow long\b|\bduration\b|\bhow many second\b|\brun time\b/],
  ["fan", /\bdid the fan\b|\bfan activat\w*\b|\bdid it use the fan\b/],
  ["solver", /\bsolver\b|\bconverge\w*\b/],
];

/**
 * Classify a question against the run readout vocabulary.
 *
 * Only fires when the question is about *this run*; general questions about the model
 * are left to the knowledge base.
 */
export function classifyRunQuestion(canonicalQuery: string): RunQuestionKind | null {
  const padded = ` ${canonicalQuery} `;
  const refersToThisRun =
    /\bthis (run|result|simulation|scenario)\b|\bthe run\b|\bthis\b/.test(padded) ||
    /\b(final|peak|energy balance|how long|did the fan|solver)\b/.test(padded);
  if (!refersToThisRun) return null;

  for (const [kind, pattern] of RUN_CUES) {
    if (pattern.test(padded)) return kind;
  }
  return null;
}
