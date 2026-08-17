/**
 * Deterministic intent router.
 *
 * Classification is purely lexical and structural: fixed cue phrases, question-word
 * position, superlatives, and how many VTMS entities the question mentions. There is no
 * model, no training data, and no probability estimate — the same question always
 * produces the same intent.
 */

import { type Entity, scenarioIdsIn } from "./assistant-entities";
import { canonicalize, contentTokens } from "./assistant-text";
import type { RankingMetric } from "./assistant-scenarios";

export type Intent =
  | "definition"
  | "explanation"
  | "comparison"
  | "scenario_lookup"
  | "scenario_comparison"
  | "status"
  | "capability"
  | "exclusion"
  | "numerical_question"
  | "creator"
  | "architecture"
  | "follow_up";

const has = (padded: string, ...phrases: string[]) =>
  phrases.some((phrase) => padded.includes(` ${phrase} `));

const COMPARISON_CUES = [
  "compare",
  "comparison",
  "versus",
  "vs",
  "difference",
  "differ",
  "different",
  "compared",
  "against",
  "better",
  "worse",
  "same a",
];

const SUPERLATIVES = [
  "hottest",
  "coolest",
  "coldest",
  "warmest",
  "highest",
  "lowest",
  "longest",
  "shortest",
  "most",
  "least",
  "maximum",
  "minimum",
  "biggest",
  "smallest",
];

const CAPABILITY_CUES = [
  "doe vtms model",
  "doe vtms",
  "can vtms",
  "doe it model",
  "do you model",
  "can it",
  "can you",
  "doe this tell",
  "doe it tell",
  "are you able",
  "doe the model",
  "doe vtms predict",
  "doe it predict",
  "will it tell",
  "capable",
];

const EXCLUSION_CUES = [
  "boiling",
  "boil",
  "damage",
  "damaged",
  "overheat",
  "overheating",
  "pressure",
  "two phase",
  "oil temperature",
  "heater core",
  "condenser",
  "cfd",
  "excluded",
  "exclude",
  "not modelled",
  "not modeled",
  "out of scope",
  "limitation",
];

const STATUS_CUES = [
  "trustworthy",
  "trust",
  "accurate",
  "accuracy",
  "reliable",
  "credible",
  "proven",
  "status",
  "standing",
  "mature",
  "maturity",
  "how good",
  "believe",
];

const ARCHITECTURE_CUES = [
  "architecture",
  "architected",
  "tech stack",
  "stack",
  "fastapi",
  "next j",
  "nextjs",
  "react",
  "backend",
  "frontend",
  "endpoint",
  "api",
  "deployed",
  "deployment",
  "railway",
  "hosted",
  "browser calculate",
];

const NUMERIC_CUES = [
  "how long",
  "how many",
  "how hot",
  "how much",
  "what temperature",
  "final temperature",
  "end temperature",
  "how far",
  "duration",
];

const FOLLOW_UP_CUES = [
  "what about",
  "how about",
  "and what",
  "what if",
  "and if",
  "then what",
  "same for",
  "in that case",
];

/** Superlative wording mapped to the canonical ranking metric it asks for. */
const METRIC_CUES: [RegExp, RankingMetric, "highest" | "lowest"][] = [
  [/\bpeak coolant\b|\bhighest coolant peak\b/, "coolantPeakC", "highest"],
  [/\bpeak engine\b|\bhighest engine peak\b/, "enginePeakC", "highest"],
  [/\bcoolant\b/, "coolantEndC", "highest"],
  [/\b(long|short|duration|run time|runtime)\w*\b/, "durationS", "highest"],
];

export type IntentAnalysis = {
  intent: Intent;
  /** True when the question leans on the previous turn to be understood. */
  isFollowUp: boolean;
  /** Cue phrases that fired, for debugging and tests. */
  signals: string[];
  /** Ranking request detected in a numerical question, if any. */
  ranking?: { metric: RankingMetric; direction: "highest" | "lowest" };
};

function detectRanking(padded: string): { metric: RankingMetric; direction: "highest" | "lowest" } | undefined {
  const wantsLowest = has(padded, "coolest", "coldest", "lowest", "least", "minimum", "shortest");
  const wantsHighest = has(padded, "hottest", "warmest", "highest", "most", "maximum", "longest");
  if (!wantsLowest && !wantsHighest) return undefined;

  const direction: "highest" | "lowest" = wantsLowest ? "lowest" : "highest";

  for (const [pattern, metric] of METRIC_CUES) {
    if (pattern.test(padded)) {
      // Duration questions ignore the temperature direction words above.
      if (metric === "durationS" && !has(padded, "longest", "shortest")) continue;
      return { metric, direction };
    }
  }

  return { metric: "engineEndC", direction };
}

/**
 * Classify a question.
 *
 * Order matters: the most structurally specific reading wins, so a question naming two
 * scenarios and a comparison cue is a scenario comparison rather than a bare
 * definition, and a superlative over scenarios is a ranking rather than a lookup.
 */
export function classifyIntent(question: string, entities: Entity[]): IntentAnalysis {
  const canonical = canonicalize(question);
  const padded = ` ${canonical} `;
  const tokens = contentTokens(canonical);
  const signals: string[] = [];

  const record = (label: string) => {
    signals.push(label);
    return true;
  };

  const scenarioIds = scenarioIdsIn(entities);
  const mentionsScenarioWord = has(padded, "scenario", "scenarios", "case", "test");
  const comparison = COMPARISON_CUES.some((cue) => has(padded, cue)) && record("comparison");
  const superlative = SUPERLATIVES.some((cue) => has(padded, cue)) && record("superlative");
  const ranking = detectRanking(padded);
  const followUpCue = FOLLOW_UP_CUES.some((cue) => padded.includes(` ${cue} `)) && record("follow-up-cue");
  const isFollowUp = Boolean(followUpCue) || tokens.length <= 2;

  const decide = (intent: Intent): IntentAnalysis => ({ intent, isFollowUp, signals, ranking });

  // A superlative across the scenario suite is a ranking question first.
  if (superlative && (mentionsScenarioWord || scenarioIds.length > 0 || has(padded, "canonical"))) {
    return decide("numerical_question");
  }

  if (comparison && scenarioIds.length >= 2) return decide("scenario_comparison");
  if (comparison && scenarioIds.length === 1 && mentionsScenarioWord) return decide("scenario_comparison");

  if (NUMERIC_CUES.some((cue) => has(padded, cue)) && (scenarioIds.length > 0 || mentionsScenarioWord)) {
    record("numeric-cue");
    return decide("numerical_question");
  }

  if (comparison) return decide("comparison");

  if (EXCLUSION_CUES.some((cue) => has(padded, cue))) {
    record("exclusion");
    return decide("exclusion");
  }

  if (CAPABILITY_CUES.some((cue) => padded.includes(` ${cue}`))) {
    record("capability");
    return decide("capability");
  }

  if (scenarioIds.length >= 2) return decide("scenario_comparison");
  if (scenarioIds.length === 1) return decide("scenario_lookup");

  if (mentionsScenarioWord && has(padded, "degradation", "fault", "baseline", "which", "list")) {
    record("scenario-set");
    return decide("scenario_lookup");
  }

  if (STATUS_CUES.some((cue) => has(padded, cue))) {
    record("status");
    return decide("status");
  }

  if (entities.some((entity) => entity.kind === "creator") || has(padded, "who built", "who is he")) {
    record("creator");
    return decide("creator");
  }

  if (ARCHITECTURE_CUES.some((cue) => has(padded, cue))) {
    record("architecture");
    return decide("architecture");
  }

  if (has(padded, "why") || has(padded, "how doe", "how do", "how is", "how are", "explain")) {
    record("explanation");
    return decide("explanation");
  }

  if (has(padded, "what is", "what are", "define", "meaning", "what doe")) {
    record("definition");
    return decide("definition");
  }

  if (isFollowUp) return decide("follow_up");

  return decide("definition");
}
