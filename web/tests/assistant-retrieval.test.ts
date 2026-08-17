/**
 * Deterministic coverage for the VTMS Knowledge Assistant.
 *
 * Run with `npm test` (Node's built-in test runner with TypeScript type stripping).
 *
 * The suite is the guard rail on assistant truthfulness. It drives more than a hundred
 * distinct queries through the real pipeline — entity extraction, intent routing,
 * retrieval, composition — and asserts both that the right thing is answered and, just
 * as importantly, that nothing the assistant can emit ever claims OEM calibration,
 * completed physical validation, digital-twin status, live telemetry, a damage or
 * boiling limit, or a real-world severity judgement.
 */

import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  type AnswerCategory,
  type AssistantResponse,
  type ComposedAnswer,
  answerQuestion,
} from "../lib/assistant-compose";
import { type ConversationContext, emptyContext } from "../lib/assistant-context";
import { extractEntities } from "../lib/assistant-entities";
import { classifyIntent, type Intent } from "../lib/assistant-intent";
import {
  ASSISTANT_DISCLOSURE,
  CREATOR_LINKS,
  FALLBACK_ANSWER,
  knowledgeTopics,
} from "../lib/assistant-knowledge";
import { PRESET_QUESTIONS, quickQuestionsForRoute } from "../lib/assistant-prompts";
import { canonicalize, rankTopics, retrieveAnswer } from "../lib/assistant-retrieval";
import { readoutFromResponse, runIdFromPathname } from "../lib/assistant-run-context";
import {
  allScenarioFacts,
  compareScenarios,
  rankScenarios,
  scenarioFacts,
} from "../lib/assistant-scenarios";
import { previewFor } from "../lib/canonical-previews";
import { scenarios } from "../lib/scenarios";
import { boundedEditDistance } from "../lib/assistant-text";

const WEB_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/* ------------------------------------------------------------------- helpers */

function respond(question: string, context?: ConversationContext): AssistantResponse {
  return answerQuestion(question, { context: context ?? emptyContext() }).response;
}

function composed(question: string, context?: ConversationContext): ComposedAnswer {
  const response = respond(question, context);
  assert.equal(response.kind, "answer", `expected a composed answer for: ${question}`);
  return response as ComposedAnswer;
}

/** Every string an answer can put in front of a visitor. */
function allText(response: AssistantResponse): string {
  if (response.kind === "fallback") return response.answer;
  if (response.kind === "clarify") {
    return [response.question, ...response.options.map((option) => option.label)].join(" ");
  }
  return [
    response.heading,
    response.lead,
    ...response.facts,
    ...response.notes,
    ...response.sections.flatMap((section) => [section.title, section.body ?? "", ...section.facts]),
    ...response.figures.flatMap((figure) => [figure.label, figure.value, figure.note ?? ""]),
  ].join(" ");
}

/* ------------------------------------------------------------ the case table */

type QueryCase = {
  group: string;
  q: string;
  kind?: AssistantResponse["kind"];
  /** sourceTopicIds must include this id. */
  topic?: string;
  category?: AnswerCategory;
  intent?: Intent;
  contains?: RegExp;
  lacks?: RegExp;
};

const CASES: QueryCase[] = [
  /* --- preset questions ------------------------------------------------- */
  { group: "preset", q: "What is VTMS and what does it simulate?", topic: "what-is-vtms", intent: "definition" },
  { group: "preset", q: "How does VTMS model engine and coolant temperature?", topic: "two-state-model" },
  { group: "preset", q: "What happens in the built-in fault scenarios?", topic: "fault-scenarios" },
  { group: "preset", q: "How has VTMS been verified and validated?", topic: "verification-and-validation" },
  { group: "preset", q: "Is VTMS a digital twin?", topic: "digital-twin", contains: /not a digital twin/i },

  /* --- definitions and paraphrases -------------------------------------- */
  { group: "paraphrase", q: "What is VTMS?", topic: "what-is-vtms", intent: "definition" },
  { group: "paraphrase", q: "what is this project", topic: "what-is-vtms" },
  { group: "paraphrase", q: "explain vtms to me", topic: "what-is-vtms" },
  { group: "paraphrase", q: "What does VTMS simulate?", topic: "what-is-vtms" },
  { group: "paraphrase", q: "What is VTMS-V1?", topic: "vtms-v1" },
  { group: "paraphrase", q: "what is em-v1", topic: "vtms-v1" },
  { group: "paraphrase", q: "Tell me about the equation set", topic: "vtms-v1" },
  { group: "paraphrase", q: "Why does the project exist?", topic: "intended-purpose" },
  { group: "paraphrase", q: "What is the purpose of VTMS?", topic: "intended-purpose" },

  /* --- physics ----------------------------------------------------------- */
  { group: "physics", q: "How does the radiator work?", topic: "radiator-heat-rejection", category: "Physics" },
  { group: "physics", q: "How does the radiator reject heat?", topic: "radiator-heat-rejection" },
  { group: "physics", q: "What is the epsilon-NTU formulation?", topic: "epsilon-ntu" },
  { group: "physics", q: "what is effectiveness ntu", topic: "epsilon-ntu" },
  { group: "physics", q: "What does the thermostat do?", topic: "thermostat" },
  { group: "physics", q: "How does the thermostat route coolant?", topic: "thermostat" },
  { group: "physics", q: "What is the bypass branch for?", topic: "bypass-flow" },
  { group: "physics", q: "How does the coolant pump behave?", topic: "coolant-pump" },
  { group: "physics", q: "What does the cooling fan do?", topic: "cooling-fan" },
  { group: "physics", q: "How does ram airflow work?", topic: "ram-airflow" },
  { group: "physics", q: "How does ambient temperature affect results?", topic: "ambient-temperature" },
  { group: "physics", q: "How is energy conservation checked?", topic: "energy-balance" },
  { group: "physics", q: "How does heat move from the engine to the coolant?", topic: "engine-to-coolant" },
  { group: "physics", q: "What is the engine thermal state?", topic: "engine-thermal-state" },
  { group: "physics", q: "What is the coolant thermal state?", topic: "coolant-thermal-state" },

  /* --- numerics and architecture ---------------------------------------- */
  { group: "numerics", q: "How is the model solved numerically?", topic: "solver" },
  { group: "numerics", q: "What solver does VTMS use?", topic: "solver" },
  { group: "numerics", q: "Does VTMS use SciPy?", topic: "solver" },
  { group: "architecture", q: "How is the application architected?", topic: "architecture", category: "Architecture" },
  { group: "architecture", q: "What is the tech stack?", topic: "architecture" },
  { group: "architecture", q: "What API endpoints exist?", topic: "backend-api" },
  { group: "architecture", q: "Does the browser calculate physics?", topic: "frontend" },
  { group: "architecture", q: "Where is VTMS deployed?", topic: "deployment" },
  { group: "architecture", q: "What do the automated tests cover?", topic: "automated-tests" },

  /* --- typos and spelling repair ---------------------------------------- */
  { group: "typo", q: "what about the raditor", topic: "radiator-heat-rejection" },
  { group: "typo", q: "how does the thermostate work", topic: "thermostat" },
  { group: "typo", q: "what is the coolent loop", contains: /coolant/i },
  { group: "typo", q: "engine temperture", contains: /temperature/i },
  { group: "typo", q: "whats s7", topic: "canonical-scenarios", contains: /S-07/ },
  { group: "typo", q: "tell me about the raditor", topic: "radiator-heat-rejection" },
  { group: "typo", q: "how is the simluation solved", contains: /RK45|solve_ivp/ },

  /* --- scenario lookup --------------------------------------------------- */
  { group: "scenario", q: "What is S-01?", category: "Scenario", contains: /S-01/ },
  { group: "scenario", q: "What is S-02?", category: "Scenario", contains: /S-02/ },
  { group: "scenario", q: "What is S-03?", category: "Scenario", contains: /S-03/ },
  { group: "scenario", q: "What is S-04?", category: "Scenario", contains: /S-04/ },
  { group: "scenario", q: "What is S-05?", category: "Scenario", contains: /S-05/ },
  { group: "scenario", q: "What is S-06?", category: "Scenario", contains: /S-06/ },
  { group: "scenario", q: "What is S-07?", category: "Scenario", contains: /S-07/ },
  { group: "scenario", q: "What is S-08?", category: "Scenario", contains: /S-08/ },
  { group: "scenario", q: "What is S-09?", category: "Scenario", contains: /S-09/ },
  { group: "scenario", q: "What happens to the fan-failure scenario?", category: "Scenario", contains: /S-05/ },
  { group: "scenario", q: "Tell me about the stuck thermostat case", category: "Scenario", contains: /S-06/ },
  { group: "scenario", q: "What is the pump degradation scenario?", category: "Scenario", contains: /S-07/ },
  { group: "scenario", q: "How long does S-03 run?", category: "Scenario", contains: /1200 s/ },
  { group: "scenario", q: "Which scenarios are degradations?", category: "Scenario", contains: /S-07[\s\S]*S-08[\s\S]*S-09/ },
  { group: "scenario", q: "Which scenarios are faults?", category: "Scenario", contains: /S-05[\s\S]*S-06/ },
  { group: "scenario", q: "Which scenarios are baselines?", category: "Scenario", contains: /S-01/ },
  { group: "scenario", q: "What are the canonical scenarios?", topic: "canonical-scenarios" },

  /* --- scenario comparison ---------------------------------------------- */
  { group: "comparison", q: "Compare S-05 and S-06", category: "Scenario", contains: /S-05[\s\S]*S-06/ },
  { group: "comparison", q: "Compare S-05 and S-06.", category: "Scenario", intent: "scenario_comparison" },
  { group: "comparison", q: "What is different between S-02 and S-03?", category: "Scenario", contains: /Ambient/ },
  { group: "comparison", q: "S-07 vs S-08", category: "Scenario", contains: /S-07[\s\S]*S-08/ },
  { group: "comparison", q: "Compare the fan failure and stuck thermostat cases.", category: "Scenario", contains: /S-05[\s\S]*S-06/ },
  { group: "comparison", q: "Is S-08 worse than S-07?", category: "Scenario", contains: /not a real-world severity/i },
  { group: "comparison", q: "How does S-01 differ from S-03?", category: "Scenario", contains: /S-01/ },
  { group: "comparison", q: "Why is highway cooling different from idle?", category: "Physics", contains: /ram/i },

  /* --- scenario rankings -------------------------------------------------- */
  { group: "ranking", q: "Which scenario finishes hottest?", category: "Scenario", contains: /S-05|S-06/ },
  { group: "ranking", q: "Which canonical scenario ends with the hottest engine?", category: "Scenario", contains: /final engine temperature/i },
  { group: "ranking", q: "Which scenario ends with the highest coolant temperature?", category: "Scenario", contains: /final coolant temperature/i },
  { group: "ranking", q: "Which scenario gets hottest?", category: "Scenario", contains: /canonical/i },
  { group: "ranking", q: "Which canonical scenario finishes coolest?", category: "Scenario", contains: /lowest/i },
  { group: "ranking", q: "Which scenario has the highest peak engine temperature?", category: "Scenario", contains: /peak engine temperature/i },

  /* --- capability, exclusion, boiling, damage, telemetry ------------------ */
  { group: "boundary", q: "Does VTMS model boiling?", intent: "exclusion", contains: /outside the model|deliberately constrained/i },
  { group: "boundary", q: "Does this tell me when my engine will overheat?", contains: /does not predict|deliberately constrained/i },
  { group: "boundary", q: "Will VTMS tell me if my engine is damaged?", contains: /deliberately constrained|does not predict/i },
  { group: "boundary", q: "Does VTMS model coolant pressure?", contains: /pressure/i },
  { group: "boundary", q: "Does VTMS model oil temperature?", contains: /oil/i },
  { group: "boundary", q: "Can VTMS do CFD?", contains: /CFD/i },
  { group: "boundary", q: "What does VTMS-V1 intentionally exclude?", topic: "model-exclusions" },
  { group: "boundary", q: "Do you have live telemetry from my car?", lacks: /\bwe have live telemetry\b/i },
  { group: "boundary", q: "Can you read my vehicle sensors right now?", lacks: /\byes\b/i },

  /* --- status and validation --------------------------------------------- */
  { group: "status", q: "How trustworthy are the results?", intent: "status", contains: /not physically validated/i },
  { group: "status", q: "Can I trust these numbers?", contains: /not physically validated|verification/i },
  { group: "status", q: "How accurate is VTMS?", contains: /not physically validated|generic/i },
  { group: "status", q: "Is VTMS validated?", contains: /not physically validated/i },
  { group: "status", q: "What is the current validation status?", contains: /not physically validated/i },
  { group: "status", q: "Is VTMS calibrated to a specific vehicle?", contains: /not calibrated to any specific vehicle/i },
  { group: "status", q: "What is the KIT plausibility comparison?", topic: "kit-plausibility", contains: /21\.40|plausibility/i },
  { group: "status", q: "What did the KIT comparison show?", contains: /plausibility|warm/i },
  { group: "status", q: "What is the Argonne controlled validation plan?", topic: "argonne", contains: /no argonne results exist yet/i },
  { group: "status", q: "What is the Argonne controlled validation plan?", topic: "argonne", lacks: /calibration (is |has )?complete/i },
  { group: "status", q: "Why is controlled validation still pending?", contains: /pending|Argonne/i },
  { group: "status", q: "How are calibration and holdout kept separate?", topic: "calibration-vs-holdout" },
  { group: "status", q: "What does verification cover?", topic: "verification" },

  /* --- digital twin ------------------------------------------------------- */
  { group: "twin", q: "Is VTMS a digital twin?", topic: "digital-twin", contains: /not a digital twin/i },
  { group: "twin", q: "is this a digital twin", topic: "digital-twin", contains: /not a digital twin/i },
  { group: "twin", q: "Do you have a digital twin of my car?", topic: "digital-twin", contains: /not a digital twin/i },
  { group: "twin", q: "Is VTMS synchronized with a real vehicle?", lacks: /\bis synchronized\b/i },
  { group: "twin", q: "What would it take to become a digital twin?", topic: "maturity-path" },

  /* --- creator ------------------------------------------------------------ */
  { group: "creator", q: "Who built VTMS?", topic: "creator", category: "Creator", contains: /Michael Palmer/ },
  { group: "creator", q: "Who is Michael Palmer?", topic: "creator", contains: /Michael Palmer/ },
  { group: "creator", q: "who created this project", topic: "creator" },
  { group: "creator", q: "who made this", topic: "creator" },
  { group: "creator", q: "Why was VTMS created?", topic: "why-vtms-was-built" },
  { group: "creator", q: "Where can I find the code?", topic: "creator-links", contains: /github\.com\/mpalmer79/ },
  { group: "creator", q: "What is his LinkedIn?", contains: /linkedin\.com\/in\/mpalmer1234/ },

  /* --- assistant self-description ----------------------------------------- */
  { group: "self", q: "Are you an AI?", topic: "assistant-itself", contains: /No external AI service|curated VTMS knowledge base/i },
  { group: "self", q: "Do you use ChatGPT?", topic: "assistant-itself" },
  { group: "self", q: "How do you work?", topic: "assistant-itself" },

  /* --- unknown and out-of-domain ------------------------------------------ */
  { group: "unknown", q: "What is the best pizza in New York?", kind: "fallback" },
  { group: "unknown", q: "Who won the 2026 World Cup?", kind: "fallback" },
  { group: "unknown", q: "Tell me a joke", kind: "fallback" },
  { group: "unknown", q: "What is the weather today?", kind: "fallback" },
  { group: "unknown", q: "Write me a poem about cars", kind: "fallback" },
  { group: "unknown", q: "How do I change my brake pads?", kind: "fallback" },
  { group: "unknown", q: "asdfgh qwerty", kind: "fallback" },
  { group: "unknown", q: "", kind: "fallback" },
  { group: "unknown", q: "   ?!  ", kind: "fallback" },

  /* --- ambiguity ----------------------------------------------------------- */
  { group: "ambiguous", q: "fan or pump", kind: "clarify" },
];

/* ------------------------------------------------------------- table-driven */

test("the suite drives at least 100 distinct queries", () => {
  const distinct = new Set(CASES.map((entry) => entry.q));
  assert.ok(
    CASES.length >= 100,
    `expected at least 100 query cases, found ${CASES.length}`,
  );
  assert.ok(distinct.size >= 100, `expected at least 100 distinct queries, found ${distinct.size}`);
});

for (const entry of CASES) {
  test(`[${entry.group}] ${entry.q || "(empty)"}`, () => {
    const response = respond(entry.q);

    if (entry.kind) {
      assert.equal(response.kind, entry.kind, `wrong response kind for: ${entry.q}`);
    }

    if (entry.kind === "fallback") {
      assert.equal((response as { answer: string }).answer, FALLBACK_ANSWER);
      return;
    }
    if (entry.kind === "clarify") return;

    if (entry.topic || entry.category || entry.intent || entry.contains) {
      assert.equal(response.kind, "answer", `expected an answer for: ${entry.q}`);
    }

    if (response.kind !== "answer") return;

    if (entry.topic) {
      assert.ok(
        response.sourceTopicIds.includes(entry.topic),
        `expected topic "${entry.topic}" for "${entry.q}", got [${response.sourceTopicIds.join(", ")}]`,
      );
    }
    if (entry.category) assert.equal(response.category, entry.category, entry.q);
    if (entry.intent) assert.equal(response.intent, entry.intent, entry.q);
    if (entry.contains) assert.match(allText(response), entry.contains, entry.q);
    if (entry.lacks) assert.doesNotMatch(allText(response), entry.lacks, entry.q);
  });
}

/* ----------------------------------------------------- truthfulness invariants */

const NEGATION = /\b(not|no|never|cannot|without|outside|pending|yet|future|would|only after|rather than|instead of|qualitative)\b/;

const SENSITIVE = [
  /\bdigital twin\b/,
  /\bphysically validated\b/,
  /\blive telemetry\b/,
  /\bboil[- ](over|ing)\b/,
  /\bdamage threshold\b/,
  /\boem[- ]calibrated\b/,
  /\bvehicle[- ]specific (accuracy|prediction|validation)\b/,
];

function assertNoBareClaims(text: string, label: string) {
  for (const sentence of text.toLowerCase().split(/(?<=[.;:])\s+/)) {
    for (const pattern of SENSITIVE) {
      if (!pattern.test(sentence)) continue;
      assert.match(sentence, NEGATION, `${label} states a prohibited claim without negation: "${sentence.trim()}"`);
    }
  }
}

test("no knowledge-base topic states a prohibited claim", () => {
  for (const topic of knowledgeTopics) {
    assertNoBareClaims([topic.shortAnswer, ...topic.detail].join(" "), `topic "${topic.id}"`);
  }
});

test("no composed answer in the whole case table states a prohibited claim", () => {
  for (const entry of CASES) {
    assertNoBareClaims(allText(respond(entry.q)), `answer to "${entry.q}"`);
  }
});

test("no composed answer offers a real-world severity or safety judgement", () => {
  // "worse", "dangerous", "unsafe" must never appear as the assistant's own verdict.
  const verdicts = /\b(is dangerous|is unsafe|will fail|will overheat|is worse than|more severe)\b/i;
  for (const entry of CASES) {
    assert.doesNotMatch(allText(respond(entry.q)), verdicts, `answer to "${entry.q}"`);
  }
});

test("every scenario comparison carries the model-output caveat", () => {
  for (const question of ["Compare S-05 and S-06", "Is S-08 worse than S-07?", "S-07 vs S-08"]) {
    const answer = composed(question);
    assert.ok(
      answer.notes.some((note) => /not a real-world severity/i.test(note)),
      `missing severity caveat for: ${question}`,
    );
  }
});

test("every quoted canonical number carries its provenance", () => {
  for (const question of ["What is S-05?", "Which scenario finishes hottest?", "How long does S-03 run?"]) {
    const answer = composed(question);
    assert.ok(
      answer.notes.some((note) => /canonical simulation output/i.test(note)),
      `missing provenance for: ${question}`,
    );
    assert.ok(
      answer.notes.some((note) => /not measured vehicle telemetry/i.test(note)),
      `missing telemetry disclaimer for: ${question}`,
    );
  }
});

test("no answer mixes current project status with superseded status text", () => {
  // The knowledge base carries baseline status prose; `assistant-status-overrides.ts`
  // supersedes it as the project advances. Every path that renders a topic must apply
  // the override, or one answer can assert both the old and the new state at once.
  const superseded = [
    /pending data acquisition/i,
    /awaiting qualified argonne/i,
    /argonne d3 acquisition pending/i,
  ];

  for (const entry of CASES) {
    const text = allText(respond(entry.q));
    for (const pattern of superseded) {
      assert.doesNotMatch(text, pattern, `superseded status text surfaced for "${entry.q}"`);
    }
  }

  // Same guard on the status answers reached through the composer's direct lookups.
  for (const question of [
    "How trustworthy are the results?",
    "Is VTMS validated?",
    "What is the current validation status?",
    "How accurate is VTMS?",
  ]) {
    const text = allText(respond(question));
    for (const pattern of superseded) {
      assert.doesNotMatch(text, pattern, `superseded status text surfaced for "${question}"`);
    }
  }
});

test("status answers still refuse to claim completed physical validation", () => {
  for (const question of [
    "How trustworthy are the results?",
    "Is VTMS validated?",
    "What is the current validation status?",
    "What is the Argonne controlled validation plan?",
  ]) {
    const text = allText(respond(question));
    assert.match(text, /not physically validated|no argonne (validation )?result/i, question);
    assert.doesNotMatch(text, /\bvalidation (is |has been )?complete\b/i, question);
    assert.doesNotMatch(text, /\bholdout (is |has been )?(complete|executed)\b/i, question);
  }
});

test("the creator is never given credentials the repository does not support", () => {
  const forbidden = /\b(mechanical engineer|oem thermal engineer|licensed professional engineer)\b/;
  for (const question of ["Who built VTMS?", "Who is Michael Palmer?", "Why was VTMS created?"]) {
    const text = allText(respond(question)).toLowerCase();
    assert.doesNotMatch(
      text.replace("not presented as a mechanical, oem, or licensed professional engineer", ""),
      forbidden,
      question,
    );
  }
});

/* --------------------------------------------------------- scenario integrity */

test("scenario facts are joined from the authoritative sources, not re-typed", () => {
  for (const card of scenarios) {
    const facts = scenarioFacts(card.id);
    assert.ok(facts, `missing facts for ${card.id}`);
    // Inputs must equal lib/scenarios.ts exactly.
    assert.equal(facts.conditions.ambientC, card.ambient);
    assert.equal(facts.conditions.rpm, card.rpm);
    assert.equal(facts.conditions.loadPercent, card.load);
    assert.equal(facts.conditions.speedKmh, card.speedKmh);
    assert.equal(facts.conditions.durationS, card.duration);

    // Outputs must equal the canonical preview fixture exactly.
    const preview = previewFor(card.id);
    assert.ok(preview, `missing canonical preview for ${card.id}`);
    assert.equal(facts.output?.engineEndC, preview.endState.engineC);
    assert.equal(facts.output?.coolantEndC, preview.endState.coolantC);
    assert.equal(facts.output?.enginePeakC, preview.peak.engineC);
    assert.equal(facts.output?.normalizedResidual, preview.energyBalance.normalizedResidual);
  }
});

test("rankings are ordered by the authoritative values", () => {
  const ranking = rankScenarios("engineEndC", "highest");
  assert.equal(ranking.entries.length, 9);
  for (let i = 1; i < ranking.entries.length; i += 1) {
    assert.ok(
      ranking.entries[i - 1].value >= ranking.entries[i].value,
      "ranking is not monotonically ordered",
    );
  }
  const lowest = rankScenarios("engineEndC", "lowest");
  assert.equal(lowest.entries[0].facts.id, ranking.entries[ranking.entries.length - 1].facts.id);
});

test("scenarios that genuinely tie are reported as tied, not ordered", () => {
  // S-05 and S-06 both remove radiator rejection at hot idle and reach the same state.
  const comparison = compareScenarios("S-05", "S-06");
  assert.ok(comparison);
  assert.match(comparison.outcome ?? "", /same modelled state/i);
});

test("a shared baseline is surfaced when two scenarios have one", () => {
  const comparison = compareScenarios("S-07", "S-08");
  assert.ok(comparison);
  assert.equal(comparison.sharedBaseline, "S-04");
});

test("every canonical scenario answers a direct lookup", () => {
  for (const facts of allScenarioFacts()) {
    const answer = composed(`What is ${facts.id}?`);
    assert.equal(answer.category, "Scenario");
    assert.match(answer.heading, new RegExp(facts.id));
  }
});

/* ---------------------------------------------------------- entity extraction */

test("entities are extracted from ordinary phrasing", () => {
  const cases: [string, string[]][] = [
    ["How does the radiator work?", ["radiator"]],
    ["what about at idle", ["idle"]],
    ["Compare S-05 and S-06", ["S-05", "S-06"]],
    ["thermostat and bypass", ["thermostat", "bypass"]],
    ["the KIT comparison", ["kit"]],
    ["Argonne D3 data", ["argonne"]],
    ["Is VTMS a digital twin?", ["digital-twin"]],
    ["Who is Michael Palmer?", ["michael-palmer"]],
    ["the fan failure case", ["S-05"]],
  ];

  for (const [question, expected] of cases) {
    const ids = extractEntities(question).entities.map((entity) => entity.id);
    for (const id of expected) {
      assert.ok(ids.includes(id), `expected entity "${id}" in "${question}", got [${ids.join(", ")}]`);
    }
  }
});

test("spelling repair is bounded to the VTMS vocabulary", () => {
  const repaired = (question: string) =>
    Object.fromEntries(extractEntities(question).repairs.map((repair) => [repair.from, repair.to]));

  assert.equal(repaired("raditor")["raditor"], "radiator");
  assert.equal(repaired("thermostate")["thermostate"], "thermostat");
  assert.equal(repaired("temperture")["temperture"], "temperature");
  // "coolent" is handled earlier still, by the terminology alias table.
  assert.equal(canonicalize("coolent"), "coolant");

  // Out-of-domain words must never be dragged into the vocabulary.
  for (const question of ["engineer", "pizza", "engineering", "radio", "coolness", "temper"]) {
    const repairs = extractEntities(question).repairs;
    assert.equal(repairs.length, 0, `"${question}" should not be repaired, got ${JSON.stringify(repairs)}`);
  }
});

test("edit distance is bounded and symmetric on the cases that matter", () => {
  assert.equal(boundedEditDistance("raditor", "radiator", 2), 1);
  assert.equal(boundedEditDistance("radiator", "raditor", 2), 1);
  assert.equal(boundedEditDistance("engineer", "engine", 1), 2); // over budget → max + 1
  assert.equal(boundedEditDistance("pizza", "radiator", 2), 3);
});

/* ------------------------------------------------------------ intent routing */

test("intents are routed deterministically", () => {
  const cases: [string, Intent][] = [
    ["What is VTMS?", "definition"],
    ["Why does the fan matter more at idle?", "explanation"],
    ["Compare S-05 and S-06", "scenario_comparison"],
    ["Which scenario finishes hottest?", "numerical_question"],
    ["Does VTMS model boiling?", "exclusion"],
    ["How trustworthy are the results?", "status"],
    ["What is S-07?", "scenario_lookup"],
    ["Who built VTMS?", "creator"],
    ["What is the tech stack?", "architecture"],
  ];

  for (const [question, expected] of cases) {
    const entities = extractEntities(question).entities;
    assert.equal(classifyIntent(question, entities).intent, expected, question);
  }
});

test("classification is stable across repeated calls", () => {
  for (const entry of CASES.slice(0, 40)) {
    const a = JSON.stringify(respond(entry.q));
    const b = JSON.stringify(respond(entry.q));
    assert.equal(a, b, `non-deterministic answer for "${entry.q}"`);
  }
});

/* --------------------------------------------------- multi-topic composition */

test("explanations may synthesize across more than one approved topic", () => {
  const answer = composed("Why does the fan matter more at idle than highway speed?");
  assert.ok(
    answer.sourceTopicIds.length >= 2,
    `expected synthesis across topics, got [${answer.sourceTopicIds.join(", ")}]`,
  );
  assert.ok(answer.sections.length >= 1, "expected supporting sections");
});

test("supporting sections only ever quote approved topic text", () => {
  const approved = new Set(
    knowledgeTopics.flatMap((topic) => [topic.shortAnswer, ...topic.detail, topic.title]),
  );
  const answer = composed("Why does the fan matter more at idle than highway speed?");
  for (const section of answer.sections) {
    assert.ok(approved.has(section.title), `unapproved section title: ${section.title}`);
    if (section.body) assert.ok(approved.has(section.body), `unapproved section body: ${section.body}`);
    for (const fact of section.facts) assert.ok(approved.has(fact), `unapproved section fact: ${fact}`);
  }
});

test("ranked candidates expose score, matched terms, and confidence", () => {
  const retrieval = rankTopics("How does the radiator reject heat?");
  assert.ok(retrieval.candidates.length >= 1);
  const [top] = retrieval.candidates;
  assert.ok(top.score > 0);
  assert.ok(top.confidence > 0 && top.confidence <= 1);
  assert.ok(top.matchedTerms.length > 0);
  for (let i = 1; i < retrieval.candidates.length; i += 1) {
    assert.ok(retrieval.candidates[i - 1].score >= retrieval.candidates[i].score, "candidates not ranked");
  }
});

/* ------------------------------------------------------ conversational context */

test("a short follow-up inherits the subject from the previous turn", () => {
  let context = emptyContext();

  const first = answerQuestion("How does the radiator work?", { context });
  context = first.context;
  assert.equal((first.response as ComposedAnswer).sourceTopicIds[0], "radiator-heat-rejection");

  const second = answerQuestion("What about at idle?", { context });
  context = second.context;
  const secondAnswer = second.response as ComposedAnswer;
  assert.equal(secondAnswer.kind, "answer");
  assert.ok(
    secondAnswer.sourceTopicIds.includes("radiator-heat-rejection"),
    "follow-up lost the radiator subject",
  );
  assert.ok(context.conditions.includes("idle"), "idle not retained in context");

  const third = answerQuestion("And if the fan fails?", { context });
  context = third.context;
  assert.ok(context.components.includes("fan"), "fan not retained in context");
  assert.ok(context.scenarioIds.includes("S-05"), "fan failure not resolved to S-05");
});

test("context is bounded and reset clears it", () => {
  let context = emptyContext();
  for (const question of [
    "How does the radiator work?",
    "What does the thermostat do?",
    "How does the pump behave?",
    "What is S-05?",
    "What is S-06?",
    "What is S-07?",
  ]) {
    context = answerQuestion(question, { context }).context;
  }

  assert.ok(context.recentTopicIds.length <= 3, "topic memory is unbounded");
  assert.ok(context.scenarioIds.length <= 2, "scenario memory is unbounded");
  assert.ok(context.components.length <= 2, "component memory is unbounded");

  const fresh = emptyContext();
  assert.deepEqual(fresh.recentTopicIds, []);
  assert.deepEqual(fresh.scenarioIds, []);
  assert.equal(fresh.evidenceConcept, null);
  assert.equal(fresh.lastIntent, null);
});

test("context can never turn an unrelated question into a VTMS answer", () => {
  let context = emptyContext();
  context = answerQuestion("How does the radiator work?", { context }).context;

  for (const question of [
    "What is the best pizza in New York?",
    "Who won the 2026 World Cup?",
    "Write me a poem about cars",
  ]) {
    const response = answerQuestion(question, { context }).response;
    assert.equal(response.kind, "fallback", `context leaked into: ${question}`);
  }
});

test("a subject change replaces the previous subject", () => {
  let context = emptyContext();
  context = answerQuestion("How does the radiator work?", { context }).context;
  context = answerQuestion("What does the thermostat do?", { context }).context;
  assert.equal(context.components[0], "thermostat", "component context did not move to the new subject");
});

/* ------------------------------------------------------------- disambiguation */

test("near-tied unrelated candidates ask for clarification instead of guessing", () => {
  const response = respond("fan or pump");
  assert.equal(response.kind, "clarify");
  if (response.kind !== "clarify") return;
  assert.equal(response.options.length, 2);
  assert.match(response.question, /Are you asking about/i);
  // Each option must lead somewhere real.
  for (const option of response.options) {
    assert.equal(respond(option.query).kind, "answer", `clarify option went nowhere: ${option.query}`);
  }
});

test("a clear winner is never turned into a clarification", () => {
  for (const question of ["How does the radiator reject heat?", "What is S-05?", "Who built VTMS?"]) {
    assert.notEqual(respond(question).kind, "clarify", question);
  }
});

/* ------------------------------------------------------------ run-aware readout */

const RUN_FIXTURE = {
  run_id: "run-test-1",
  classification: "computed_simulation" as const,
  result: {
    model_metadata: {
      model_id: "VTMS-V1",
      model_version: "1.0.0",
      equation_set: "EM-V1",
      reference_vehicle: "generic",
      coolant_property_set: "generic",
      parameter_set: "generic",
      validation_status: "numerical_verified_generic_uncalibrated",
      classification: "generic",
      digital_twin_status: "not_a_digital_twin",
    },
    scenario_metadata: {
      scenario_id: "S-03",
      name: "Hot Ambient Idle",
      duration_s: 1200,
      ambient_temp_c: 40,
      engine_speed_rpm: 1000,
      effective_load: 0.25,
      vehicle_speed_m_s: 0,
      initial_engine_temp_c: 40,
      initial_coolant_temp_c: 40,
      engine_heat_override_w: null,
      faults: {
        fan_failed: false,
        thermostat_mode: "normal" as const,
        thermostat_health: 1,
        pump_health: 1,
        radiator_health: 1,
        airflow_health: 1,
      },
    },
    parameter_snapshot: {},
    provenance_snapshot: {},
    time_series: [
      {
        time_s: 0, engine_structure_temp_c: 40, coolant_temp_c: 40, radiator_outlet_temp_c: 40,
        engine_heat_w: 1000, engine_to_coolant_w: 0, engine_to_ambient_w: 0, radiator_heat_w: 0,
        pump_flow_kg_s: 0.5, radiator_flow_kg_s: 0, bypass_flow_kg_s: 0.5, air_flow_kg_s: 0,
        thermostat_fraction: 0, fan_fraction: 0, radiator_effectiveness: 0, radiator_ntu: 0,
      },
      {
        time_s: 1200, engine_structure_temp_c: 101.1, coolant_temp_c: 96.5, radiator_outlet_temp_c: 80,
        engine_heat_w: 1000, engine_to_coolant_w: 900, engine_to_ambient_w: 100, radiator_heat_w: 900,
        pump_flow_kg_s: 0.5, radiator_flow_kg_s: 0.5, bypass_flow_kg_s: 0, air_flow_kg_s: 0.4,
        thermostat_fraction: 1, fan_fraction: 0.6, radiator_effectiveness: 0.5, radiator_ntu: 1,
      },
    ],
    events: [],
    energy_balance: {
      input_energy_j: 1000, rejected_energy_j: 900, stored_energy_change_j: 100,
      residual_j: 0.1, normalized_residual: 0.0002,
    },
    warnings: [],
    solver_diagnostics: {
      success: true, status: 0, message: "ok", function_evaluations: 100,
      jacobian_evaluations: 0, lu_decompositions: 0,
    },
  },
};

test("run ids are parsed only from computed-result routes", () => {
  assert.equal(runIdFromPathname("/results/run-abc"), "run-abc");
  assert.equal(runIdFromPathname("/results/demo-s03"), null);
  assert.equal(runIdFromPathname("/scenarios"), null);
  assert.equal(runIdFromPathname("/"), null);
});

test("the run readout is a direct reduction of the returned result", () => {
  const readout = readoutFromResponse(RUN_FIXTURE);
  assert.ok(readout);
  assert.equal(readout.finalEngineC, 101.1);
  assert.equal(readout.finalCoolantC, 96.5);
  assert.equal(readout.peakEngineC, 101.1);
  assert.equal(readout.scenarioId, "S-03");
  assert.equal(readout.durationS, 1200);
  assert.equal(readout.fanActivated, true);
  assert.equal(readout.energyBalancePass, true);
  assert.equal(readout.solverSuccess, true);
});

test("run readout questions are answered from the returned result", () => {
  const run = readoutFromResponse(RUN_FIXTURE);
  assert.ok(run);

  const cases: [string, RegExp][] = [
    ["What is the final coolant temperature?", /96\.5 °C/],
    ["Did energy balance pass?", /passed/i],
    ["What scenario is this?", /Hot Ambient Idle/],
    ["How long did this simulation run?", /1200 s/],
    ["Did the fan activate?", /commanded on/i],
  ];

  for (const [question, expected] of cases) {
    const outcome = answerQuestion(question, { context: emptyContext(), run });
    const response = outcome.response;
    assert.equal(response.kind, "answer", question);
    if (response.kind !== "answer") continue;
    assert.equal(response.category, "Run", question);
    assert.match(allText(response), expected, question);
    assert.ok(
      response.notes.some((note) => /not measured vehicle telemetry/i.test(note)),
      `run answer missing telemetry disclaimer: ${question}`,
    );
  }
});

test("without a run in view, readout questions do not invent one", () => {
  const response = respond("What is the final coolant temperature?");
  if (response.kind === "answer") {
    assert.notEqual(response.category, "Run", "answered a run question with no run in view");
  }
});

/* --------------------------------------------------------------- route prompts */

test("route-aware starters are offered for product routes", () => {
  const routes: [string, RegExp][] = [
    ["/system", /radiator|thermostat|airflow/i],
    ["/scenarios", /S-05|degradation|hottest/i],
    ["/validation", /KIT|controlled|calibration/i],
    ["/about", /built|created|Michael/i],
  ];

  for (const [pathname, expected] of routes) {
    const { prompts, routeSpecific } = quickQuestionsForRoute(pathname);
    assert.ok(routeSpecific, `${pathname} should offer route-specific prompts`);
    assert.equal(prompts.length, 3, pathname);
    assert.match(prompts.map((prompt) => prompt.label).join(" "), expected, pathname);
  }
});

test("/assistant keeps the five global starters", () => {
  const { prompts, routeSpecific } = quickQuestionsForRoute("/assistant");
  assert.equal(routeSpecific, false);
  assert.equal(prompts.length, 5);
  assert.deepEqual(prompts, PRESET_QUESTIONS);
});

test("there are exactly five presets with short labels and distinct glyphs", () => {
  assert.equal(PRESET_QUESTIONS.length, 5);
  assert.deepEqual(
    PRESET_QUESTIONS.map((prompt) => prompt.label),
    [
      "What is VTMS?",
      "How does the cooling system work?",
      "What happens when cooling fails?",
      "How trustworthy are the results?",
      "Is VTMS a digital twin?",
    ],
  );

  // Labels stay short enough for a mobile row.
  for (const prompt of PRESET_QUESTIONS) {
    assert.ok(prompt.label.length <= 34, `preset label too long: ${prompt.label}`);
  }
  assert.equal(new Set(PRESET_QUESTIONS.map((prompt) => prompt.glyph)).size, 5);
});

test("every starter prompt and route prompt resolves to a real answer", () => {
  const routes = ["/assistant", "/system", "/scenarios", "/validation", "/about", "/simulate", "/model"];
  for (const pathname of routes) {
    for (const prompt of quickQuestionsForRoute(pathname).prompts) {
      const response = respond(prompt.query);
      assert.notEqual(response.kind, "fallback", `dead starter on ${pathname}: ${prompt.query}`);
    }
  }
});

test("every follow-up the assistant offers resolves to a real answer", () => {
  for (const entry of CASES) {
    const response = respond(entry.q);
    for (const suggestion of response.suggestions) {
      assert.notEqual(
        respond(suggestion).kind,
        "fallback",
        `dead follow-up "${suggestion}" offered for "${entry.q}"`,
      );
    }
  }
});

test("every knowledge-base follow-up resolves", () => {
  for (const topic of knowledgeTopics) {
    for (const question of topic.followUpQuestions) {
      assert.notEqual(retrieveAnswer(question).kind, "fallback", `dead follow-up on ${topic.id}: ${question}`);
    }
  }
});

/* ------------------------------------------------------------ normalization */

test("normalization folds scenario identities and terminology", () => {
  assert.equal(canonicalize("S-03"), "s03");
  assert.equal(canonicalize("S03"), "s03");
  assert.equal(canonicalize("s 3"), "s03");
  assert.equal(canonicalize("what is the coolant temp?"), "what is the coolant temperature");
  assert.equal(canonicalize("Digital-Twin"), "digital twin");
});

/* ------------------------------------------------------------ no network access */

test("no assistant module performs a network request", () => {
  const forbidden = [
    /\bfetch\s*\(/,
    /XMLHttpRequest/,
    /\bWebSocket\b/,
    /EventSource/,
    /navigator\.sendBeacon/,
    /\bimport\s+.*\bfrom\s+["'](axios|node-fetch|undici|https?|node:https?)["']/,
    /require\(\s*["'](axios|node-fetch|undici|https?|node:https?)["']\s*\)/,
    /api\.openai\.com/,
    /api\.anthropic\.com/,
    /generativelanguage\.googleapis\.com/,
    /\bOPENAI|ANTHROPIC_API_KEY|GEMINI_API_KEY\b/,
  ];

  const libFiles = readdirSync(path.join(WEB_ROOT, "lib"))
    .filter((name) => name.startsWith("assistant-"))
    .map((name) => path.join(WEB_ROOT, "lib", name));

  const files = [
    ...libFiles,
    ...readdirSync(path.join(WEB_ROOT, "components", "assistant")).map((name) =>
      path.join(WEB_ROOT, "components", "assistant", name),
    ),
    path.join(WEB_ROOT, "app", "assistant", "page.tsx"),
  ];

  assert.ok(libFiles.length >= 8, `expected the assistant lib set to be discovered, found ${libFiles.length}`);

  for (const file of files) {
    const source = readFileSync(file, "utf8");
    for (const pattern of forbidden) {
      assert.doesNotMatch(source, pattern, `${path.relative(WEB_ROOT, file)} looks like it reaches the network`);
    }
  }
});

test("the assistant discloses that it is a local knowledge base", () => {
  assert.match(ASSISTANT_DISCLOSURE, /VTMS knowledge base/i);
  assert.match(ASSISTANT_DISCLOSURE, /No external AI service is contacted/i);
});

test("LinkedIn and GitHub destinations are correct", () => {
  assert.equal(CREATOR_LINKS.linkedin, "https://www.linkedin.com/in/mpalmer1234");
  assert.equal(CREATOR_LINKS.github, "https://github.com/mpalmer79");
  assert.equal(
    CREATOR_LINKS.repository,
    "https://github.com/mpalmer79/vehicle-thermal-management-simulation",
  );
});
