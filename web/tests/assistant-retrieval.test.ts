/**
 * Deterministic coverage for the VTMS Knowledge Assistant.
 *
 * Run with `npm test` (Node's built-in test runner with TypeScript type stripping).
 * These tests are the guard rail on assistant truthfulness: they assert that preset
 * questions resolve to the intended topics, that the sensitive status answers stay
 * conservative, that unknown questions fall back instead of inventing content, and that
 * no assistant module can reach the network.
 */

import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  ASSISTANT_DISCLOSURE,
  CREATOR_LINKS,
  FALLBACK_ANSWER,
  PRESET_QUESTIONS,
  knowledgeTopics,
} from "../lib/assistant-knowledge";
import { canonicalize, retrieveAnswer } from "../lib/assistant-retrieval";

const WEB_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function matchTopicId(question: string, lastTopicId: string | null = null): string {
  const result = retrieveAnswer(question, { lastTopicId });
  assert.equal(result.kind, "match", `expected a knowledge-base match for: ${question}`);
  return result.kind === "match" ? result.topic.id : "";
}

function answerText(question: string): string {
  const result = retrieveAnswer(question);
  assert.equal(result.kind, "match", `expected a knowledge-base match for: ${question}`);
  if (result.kind !== "match") return "";
  return [result.topic.shortAnswer, ...result.topic.detail].join(" ").toLowerCase();
}

/* ------------------------------------------------------------ preset questions */

test("there are exactly five preset questions", () => {
  assert.equal(PRESET_QUESTIONS.length, 5);
});

test("each preset question maps to its intended topic", () => {
  const expected: [string, string][] = [
    ["What is VTMS and what does it simulate?", "what-is-vtms"],
    ["How does VTMS model engine and coolant temperature?", "two-state-model"],
    ["What happens in the built-in fault scenarios?", "fault-scenarios"],
    ["How has VTMS been verified and validated?", "verification-and-validation"],
    ["Is VTMS a digital twin?", "digital-twin"],
  ];

  // The table must stay in step with the exported presets.
  assert.deepEqual(expected.map(([question]) => question), [...PRESET_QUESTIONS]);

  for (const [question, topicId] of expected) {
    assert.equal(matchTopicId(question), topicId, `preset misrouted: ${question}`);
  }
});

test("every preset answer offers follow-up suggestions", () => {
  for (const question of PRESET_QUESTIONS) {
    const result = retrieveAnswer(question);
    assert.equal(result.kind, "match");
    if (result.kind !== "match") continue;
    assert.ok(result.suggestions.length >= 2 && result.suggestions.length <= 3);
  }
});

/* --------------------------------------------------------- truthfulness guards */

test("digital twin questions return the NOT-a-digital-twin status", () => {
  for (const question of [
    "Is VTMS a digital twin?",
    "is this a digital twin",
    "Do you have a digital twin of my car?",
  ]) {
    assert.equal(matchTopicId(question), "digital-twin", question);
  }

  const text = answerText("Is VTMS a digital twin?");
  assert.match(text, /not a digital twin/);
  assert.match(text, /no live data feed|no live telemetry|no connection to any physical vehicle/);
});

test("validation questions never claim completed physical validation", () => {
  const text = answerText("Is VTMS validated?");
  assert.match(text, /not physically validated/);
  assert.doesNotMatch(text, /validation (is )?complete\b/);
  assert.doesNotMatch(text, /oem[- ]calibrated/);
});

test("no knowledge-base answer claims prohibited status", () => {
  // Sensitive subjects may only ever be mentioned inside a negated or deferred
  // statement — "is not a digital twin", "does not predict damage" — never as a claim.
  const sensitive = [
    /\bdigital twin\b/,
    /\bphysically validated\b/,
    /\blive telemetry\b/,
    /\bboil[- ](over|ing)\b/,
    /\bdamage threshold\b/,
    /\boem[- ]calibrated\b/,
    /\bvehicle[- ]specific (accuracy|prediction|validation)\b/,
  ];
  const negation = /\b(not|no|never|cannot|without|outside|pending|yet|future|would|only after|rather than|instead of)\b/;

  for (const topic of knowledgeTopics) {
    const sentences = [topic.shortAnswer, ...topic.detail]
      .join(" ")
      .toLowerCase()
      .split(/(?<=[.;:])\s+/);

    for (const sentence of sentences) {
      for (const pattern of sensitive) {
        if (!pattern.test(sentence)) continue;
        assert.match(
          sentence,
          negation,
          `topic "${topic.id}" states a prohibited claim without negation: "${sentence.trim()}"`,
        );
      }
    }
  }
});

test("the model classification answer states the generic uncalibrated status", () => {
  const text = answerText("Is VTMS calibrated to a specific vehicle?");
  assert.match(text, /not calibrated to any specific vehicle/);
});

test("Argonne answers do not report results that have not occurred", () => {
  const text = answerText("What is the Argonne controlled validation plan?");
  assert.match(text, /pending/);
  assert.match(text, /no argonne results exist yet/);
});

/* -------------------------------------------------------------------- fallback */

test("unknown questions fall back instead of inventing an answer", () => {
  for (const question of [
    "What is the best pizza in New York?",
    "Who won the 2026 World Cup?",
    "Tell me a joke",
    "What is my current engine temperature right now in my car outside?",
    "",
    "   ?!  ",
  ]) {
    const result = retrieveAnswer(question);
    assert.equal(result.kind, "fallback", `expected fallback for: ${question}`);
    if (result.kind !== "fallback") continue;
    assert.equal(result.answer, FALLBACK_ANSWER);
    assert.ok(result.suggestions.length > 0, "fallback must offer suggestions");
  }
});

/* --------------------------------------------------------------------- creator */

test("creator questions return Michael Palmer information", () => {
  for (const question of [
    "Who built VTMS?",
    "Who is Michael Palmer?",
    "who created this project",
    "who made this",
  ]) {
    assert.equal(matchTopicId(question), "creator", question);
  }

  const result = retrieveAnswer("Who built VTMS?");
  assert.equal(result.kind, "match");
  if (result.kind !== "match") return;

  assert.match(result.topic.shortAnswer, /Michael Palmer/);
  assert.match(result.topic.shortAnswer, /25 years/);
  assert.match(result.topic.shortAnswer, /Southern New Hampshire University/);
  // The about route must be offered so the visitor can go deeper.
  assert.ok(result.topic.relatedRoutes.some((route) => route.href === "/about"));
});

test("the creator is never described with credentials the repository does not support", () => {
  const forbidden = /\b(mechanical engineer|oem thermal engineer|licensed professional engineer|professional engineer|p\.?e\.?)\b/;
  for (const topic of knowledgeTopics.filter((entry) => entry.category === "Creator")) {
    const text = [topic.shortAnswer, ...topic.detail].join(" ").toLowerCase();
    assert.doesNotMatch(text.replace("not presented as a mechanical, oem, or licensed professional engineer", ""), forbidden, topic.id);
  }
});

test("LinkedIn and GitHub destinations are correct", () => {
  assert.equal(CREATOR_LINKS.linkedin, "https://www.linkedin.com/in/mpalmer1234");
  assert.equal(CREATOR_LINKS.github, "https://github.com/mpalmer79");
  assert.equal(
    CREATOR_LINKS.repository,
    "https://github.com/mpalmer79/vehicle-thermal-management-simulation",
  );

  const result = retrieveAnswer("What is his LinkedIn and GitHub?");
  assert.equal(result.kind, "match");
  if (result.kind !== "match") return;
  const detail = result.topic.detail.join(" ");
  assert.ok(detail.includes(CREATOR_LINKS.linkedin));
  assert.ok(detail.includes(CREATOR_LINKS.github));
});

/* --------------------------------------------------------- topic coverage */

test("core subject areas resolve to their topics", () => {
  const expected: [string, string][] = [
    ["How does the radiator work?", "radiator-heat-rejection"],
    ["What is the epsilon-NTU formulation?", "epsilon-ntu"],
    ["What does the thermostat do?", "thermostat"],
    ["What is the bypass branch for?", "bypass-flow"],
    ["How does the coolant pump behave?", "coolant-pump"],
    ["What does the cooling fan do?", "cooling-fan"],
    ["How does ram airflow work?", "ram-airflow"],
    ["How does ambient temperature affect results?", "ambient-temperature"],
    ["How is energy conservation checked?", "energy-balance"],
    ["What solver does VTMS use?", "solver"],
    ["What are the canonical scenarios?", "canonical-scenarios"],
    ["What do the degradation scenarios show?", "degradation-scenarios"],
    ["What does verification cover?", "verification"],
    ["What is the KIT plausibility comparison?", "kit-plausibility"],
    ["How are calibration and holdout kept separate?", "calibration-vs-holdout"],
    ["How is the application architected?", "architecture"],
    ["What API endpoints exist?", "backend-api"],
    ["Does the browser calculate physics?", "frontend"],
    ["Where is VTMS deployed?", "deployment"],
  ];

  for (const [question, topicId] of expected) {
    assert.equal(matchTopicId(question), topicId, `misrouted: ${question}`);
  }
});

test("every follow-up question offered by a topic resolves to a real answer", () => {
  for (const topic of knowledgeTopics) {
    for (const question of topic.followUpQuestions) {
      const result = retrieveAnswer(question, { lastTopicId: topic.id });
      assert.equal(result.kind, "match", `dead-end follow-up on "${topic.id}": ${question}`);
    }
  }
});

test("fallback suggestions all resolve", () => {
  for (const question of [
    "What is VTMS and what does it simulate?",
    "How does the radiator reject heat?",
    "How has VTMS been verified and validated?",
    "Who built VTMS?",
  ]) {
    assert.equal(retrieveAnswer(question).kind, "match", question);
  }
});

/* ------------------------------------------------------- contextual follow-ups */

test("a short follow-up keeps the previous subject area in scope", () => {
  const first = matchTopicId("How does the radiator work?");
  assert.equal(first, "radiator-heat-rejection");

  // Asked cold and asked in context, "what about airflow?" must land on the air side.
  assert.equal(matchTopicId("What about airflow?"), "ram-airflow");
  assert.equal(matchTopicId("What about airflow?", first), "ram-airflow");
});

test("context can break a tie but cannot promote an unrelated topic", () => {
  const result = retrieveAnswer("What is the best pizza in New York?", {
    lastTopicId: "radiator-heat-rejection",
  });
  assert.equal(result.kind, "fallback");
});

/* -------------------------------------------------------------- normalization */

test("normalization folds scenario identities and common terminology", () => {
  assert.equal(canonicalize("S-03"), "s03");
  assert.equal(canonicalize("S03"), "s03");
  assert.equal(canonicalize("what is the coolant temp?"), "what is the coolant temperature");
  assert.equal(canonicalize("Digital-Twin"), "digital twin");
  assert.equal(matchTopicId("Tell me about S-05"), "fault-scenarios");
  assert.equal(matchTopicId("what is s01"), "canonical-scenarios");
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

  const files = [
    path.join(WEB_ROOT, "lib", "assistant-knowledge.ts"),
    path.join(WEB_ROOT, "lib", "assistant-retrieval.ts"),
    ...readdirSync(path.join(WEB_ROOT, "components", "assistant")).map((name) =>
      path.join(WEB_ROOT, "components", "assistant", name),
    ),
    path.join(WEB_ROOT, "app", "assistant", "page.tsx"),
  ];

  assert.ok(files.length >= 5, "expected the assistant source set to be discovered");

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
