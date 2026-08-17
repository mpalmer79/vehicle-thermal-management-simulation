/**
 * Entity extraction for the VTMS Knowledge Assistant.
 *
 * A closed set of VTMS nouns is recognized in a question: canonical scenario IDs,
 * thermal components, operating conditions, evidence concepts, model concepts, and the
 * creator. Extraction is exact-match first; only tokens that match nothing are offered
 * to the bounded spell repair in `assistant-text.ts`, and only against this same closed
 * vocabulary. Nothing outside the vocabulary can be pulled into VTMS territory.
 */

import { SCENARIO_IDS } from "./assistant-scenarios";
import {
  STOPWORDS,
  canonicalize,
  contentTokens,
  nearestVocabularyTerm,
} from "./assistant-text";

export type EntityKind = "scenario" | "component" | "condition" | "evidence" | "model" | "creator";

export type Entity = {
  kind: EntityKind;
  /** Stable identifier, e.g. "S-05", "radiator", "digital-twin". */
  id: string;
  label: string;
  /** The token or phrase in the question that produced this entity. */
  matched: string;
  /** True when the match required spelling repair. */
  repaired: boolean;
};

type EntityDefinition = {
  kind: EntityKind;
  id: string;
  label: string;
  /** Canonicalized single tokens that identify the entity. */
  tokens: string[];
  /** Canonicalized multi-word phrases that identify the entity. */
  phrases?: string[];
};

const DEFINITIONS: EntityDefinition[] = [
  /* Components */
  { kind: "component", id: "engine", label: "engine", tokens: ["engine", "block", "cylinder"] },
  { kind: "component", id: "coolant", label: "coolant", tokens: ["coolant", "antifreeze"] },
  { kind: "component", id: "radiator", label: "radiator", tokens: ["radiator"], phrases: ["heat exchanger"] },
  { kind: "component", id: "thermostat", label: "thermostat", tokens: ["thermostat"] },
  { kind: "component", id: "bypass", label: "bypass branch", tokens: ["bypass"] },
  { kind: "component", id: "pump", label: "coolant pump", tokens: ["pump"] },
  { kind: "component", id: "fan", label: "cooling fan", tokens: ["fan"] },
  { kind: "component", id: "airflow", label: "airflow", tokens: ["airflow", "ram"], phrases: ["ram air", "air side"] },
  { kind: "component", id: "ambient", label: "ambient", tokens: ["ambient"], phrases: ["outside air"] },

  /* Operating conditions */
  { kind: "condition", id: "idle", label: "idle", tokens: ["idle", "idling"] },
  { kind: "condition", id: "highway", label: "highway", tokens: ["highway", "cruise", "motorway"] },
  { kind: "condition", id: "cold-start", label: "cold start", tokens: [], phrases: ["cold start", "warm up", "warmup"] },
  { kind: "condition", id: "high-load", label: "high load", tokens: [], phrases: ["high load", "higher load", "sustained load"] },

  /* Evidence concepts */
  { kind: "evidence", id: "verification", label: "verification", tokens: ["verification", "verified", "verify"] },
  { kind: "evidence", id: "validation", label: "validation", tokens: ["validation", "validated", "validate"] },
  { kind: "evidence", id: "kit", label: "KIT plausibility", tokens: ["kit"], phrases: ["seat leon", "obd ii", "obd"] },
  { kind: "evidence", id: "argonne", label: "Argonne controlled validation", tokens: ["argonne"], phrases: ["d3", "national laboratory"] },
  { kind: "evidence", id: "calibration", label: "calibration", tokens: ["calibration", "calibrated", "calibrate"] },
  { kind: "evidence", id: "holdout", label: "holdout", tokens: ["holdout"], phrases: ["blind holdout"] },

  /* Model concepts */
  { kind: "model", id: "vtms-v1", label: "VTMS-V1", tokens: [], phrases: ["vtms v1"] },
  { kind: "model", id: "em-v1", label: "EM-V1", tokens: [], phrases: ["em v1"] },
  { kind: "model", id: "digital-twin", label: "digital twin", tokens: ["twin"], phrases: ["digital twin"] },

  /* Creator */
  {
    kind: "creator",
    id: "michael-palmer",
    label: "Michael Palmer",
    tokens: ["michael", "palmer", "creator"],
    phrases: ["who built", "michael palmer"],
  },
];

/** Every canonical single token the assistant is willing to spell-repair towards. */
export const VOCABULARY: Set<string> = new Set(
  DEFINITIONS.flatMap((definition) => definition.tokens).filter((token) => token.length >= 5),
);

// A handful of additional domain words worth repairing that are not entity tokens.
for (const extra of [
  "temperature",
  "simulation",
  "scenario",
  "effectiveness",
  "conservation",
  "architecture",
  "degradation",
  "thermal",
  "energy",
  "solver",
  "boiling",
  "failure",
  "telemetry",
]) {
  VOCABULARY.add(extra);
}

const TOKEN_INDEX = new Map<string, EntityDefinition>();
for (const definition of DEFINITIONS) {
  for (const token of definition.tokens) TOKEN_INDEX.set(canonicalize(token), definition);
}

const PHRASE_INDEX: [string, EntityDefinition][] = DEFINITIONS.flatMap((definition) =>
  (definition.phrases ?? []).map((phrase) => [canonicalize(phrase), definition] as [string, EntityDefinition]),
);

const SCENARIO_TOKEN = new Map(SCENARIO_IDS.map((id) => [canonicalize(id), id]));

/**
 * Canonical scenario *names* people actually type. These are the scenario titles from
 * `lib/scenarios.ts` in ordinary phrasing, so "the fan failure case" resolves to S-05
 * exactly as "S-05" does. Only explicit scenario wording is aliased — generic condition
 * words such as "warm up" stay conditions so they do not hijack mechanism questions.
 */
const SCENARIO_NAME_ALIASES: [string, string][] = [
  ["cold start", "S-01"],
  ["fast idle", "S-01"],
  ["warm highway", "S-02"],
  ["highway cruise", "S-02"],
  ["hot ambient idle", "S-03"],
  ["hot idle", "S-03"],
  ["sustained higher load", "S-04"],
  ["sustained load", "S-04"],
  ["fan failure", "S-05"],
  ["fan failing", "S-05"],
  ["fan fails", "S-05"],
  ["failed fan", "S-05"],
  ["fan has failed", "S-05"],
  ["thermostat stuck closed", "S-06"],
  ["stuck closed", "S-06"],
  ["stuck thermostat", "S-06"],
  ["thermostat stuck", "S-06"],
  ["pump degradation", "S-07"],
  ["pump degraded", "S-07"],
  ["degraded pump", "S-07"],
  ["radiator degradation", "S-08"],
  ["radiator degraded", "S-08"],
  ["degraded radiator", "S-08"],
  ["radiator ua loss", "S-08"],
  ["airflow degradation", "S-09"],
  ["airflow restriction", "S-09"],
  ["restricted airflow", "S-09"],
].map(([phrase, id]) => [canonicalize(phrase), id]);

export type ExtractionResult = {
  entities: Entity[];
  /** Repairs applied, for transparency in tests and debugging. */
  repairs: { from: string; to: string }[];
  /** The canonical query after repairs were substituted in. */
  repairedQuery: string;
};

function push(entities: Entity[], entity: Entity) {
  if (entities.some((existing) => existing.kind === entity.kind && existing.id === entity.id)) return;
  entities.push(entity);
}

/**
 * Extract VTMS entities from a raw question.
 *
 * Spell repair runs only on tokens that are not already known vocabulary, are long
 * enough to carry a reliable signal, and resolve to exactly one vocabulary word within
 * a tight edit budget.
 */
export function extractEntities(question: string): ExtractionResult {
  const canonical = canonicalize(question);
  const entities: Entity[] = [];
  const repairs: { from: string; to: string }[] = [];

  const rawTokens = canonical.split(" ").filter(Boolean);
  const repairedTokens = rawTokens.map((token) => {
    if (TOKEN_INDEX.has(token) || SCENARIO_TOKEN.has(token) || VOCABULARY.has(token)) return token;
    if (STOPWORDS.has(token)) return token;
    const repaired = nearestVocabularyTerm(token, VOCABULARY);
    if (!repaired) return token;
    repairs.push({ from: token, to: repaired });
    return repaired;
  });

  const repairedQuery = repairedTokens.join(" ");
  const padded = ` ${repairedQuery} `;

  for (const [phrase, scenarioId] of SCENARIO_NAME_ALIASES) {
    if (padded.includes(` ${phrase} `)) {
      push(entities, {
        kind: "scenario",
        id: scenarioId,
        label: scenarioId,
        matched: phrase,
        repaired: false,
      });
    }
  }

  for (const [phrase, definition] of PHRASE_INDEX) {
    if (padded.includes(` ${phrase} `)) {
      push(entities, {
        kind: definition.kind,
        id: definition.id,
        label: definition.label,
        matched: phrase,
        repaired: false,
      });
    }
  }

  repairedTokens.forEach((token, index) => {
    const scenarioId = SCENARIO_TOKEN.get(token);
    if (scenarioId) {
      push(entities, {
        kind: "scenario",
        id: scenarioId,
        label: scenarioId,
        matched: token,
        repaired: false,
      });
      return;
    }

    const definition = TOKEN_INDEX.get(token);
    if (!definition) return;

    const wasRepaired = rawTokens[index] !== token;
    push(entities, {
      kind: definition.kind,
      id: definition.id,
      label: definition.label,
      matched: rawTokens[index],
      repaired: wasRepaired,
    });
  });

  return { entities, repairs, repairedQuery };
}

export const entitiesOfKind = (entities: Entity[], kind: EntityKind): Entity[] =>
  entities.filter((entity) => entity.kind === kind);

export const scenarioIdsIn = (entities: Entity[]): string[] =>
  entitiesOfKind(entities, "scenario").map((entity) => entity.id);

/** Re-exported so callers do not need a second import for tokenization. */
export { contentTokens };
