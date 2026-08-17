/**
 * Deterministic answer composer.
 *
 * This is the layer that makes the assistant feel like it understood the question
 * rather than merely matched it. It is *not* text generation: every sentence it emits
 * is either
 *
 *   (a) a verbatim string from the knowledge base,
 *   (b) a verbatim string from an authoritative scenario/run record, or
 *   (c) a fixed structural label or a formatted number.
 *
 * There is no template that can assert a new claim about the world. Comparative
 * statements are arithmetic over values the Python engine already produced, and every
 * ordering carries the standing caveat that it is model output, not a severity ranking.
 */

import {
  ASSISTANT_DISCLOSURE,
  FALLBACK_ANSWER,
  FALLBACK_SUGGESTIONS,
  type KnowledgeTopic,
  type RelatedRoute,
  type TopicCategory,
  topicById,
} from "./assistant-knowledge";
import {
  CANONICAL_OUTPUT_PROVENANCE,
  RANKING_CAVEAT,
  type ScenarioFacts,
  compareScenarios,
  conditionSummary,
  degrees,
  faultSummary,
  outputFacts,
  rankScenarios,
  scenarioFacts,
  scenariosInCategory,
  seconds,
} from "./assistant-scenarios";
import { type ConversationContext, advanceContext, emptyContext } from "./assistant-context";
import { type Entity, scenarioIdsIn } from "./assistant-entities";
import { type Intent, classifyIntent } from "./assistant-intent";
import { MIN_CONFIDENCE, rankTopics, type Candidate } from "./assistant-retrieval";
import { type RunReadout, classifyRunQuestion } from "./assistant-run-context";
import { canonicalize } from "./assistant-text";

export type AnswerCategory = TopicCategory | "Scenario" | "Run";

export type AnswerSection = { title: string; body?: string; facts: string[] };

export type AnswerFigure = { label: string; value: string; note?: string };

export type ComposedAnswer = {
  kind: "answer";
  intent: Intent;
  category: AnswerCategory;
  heading: string;
  /** The direct answer. Always verbatim from an approved source. */
  lead: string;
  facts: string[];
  sections: AnswerSection[];
  figures: AnswerFigure[];
  /** Provenance/caveat lines attached when authoritative numbers are quoted. */
  notes: string[];
  routes: RelatedRoute[];
  suggestions: string[];
  /** Knowledge-base topics that contributed, for context and tests. */
  sourceTopicIds: string[];
  entities: Entity[];
  repairs: { from: string; to: string }[];
};

export type ClarifyResponse = {
  kind: "clarify";
  question: string;
  options: { label: string; query: string }[];
  suggestions: string[];
};

export type FallbackResponse = {
  kind: "fallback";
  answer: string;
  suggestions: string[];
};

export type AssistantResponse = ComposedAnswer | ClarifyResponse | FallbackResponse;

export type AnswerOptions = {
  context?: ConversationContext;
  /** Present only on a computed-result route where a run is in session storage. */
  run?: RunReadout | null;
};

export type AnswerOutcome = {
  response: AssistantResponse;
  context: ConversationContext;
};

const SCENARIO_ROUTES: RelatedRoute[] = [
  { label: "Browse the scenario library", href: "/scenarios" },
  { label: "Run one in the Simulation Lab", href: "/simulate" },
];

const dedupe = (values: string[]) => [...new Set(values.filter(Boolean))];

function suggestionsFrom(candidates: Candidate[], extra: string[] = []): string[] {
  const fromTopics = candidates.flatMap((candidate) => candidate.topic.followUpQuestions);
  return dedupe([...extra, ...fromTopics]).slice(0, 3);
}

function routesFrom(candidates: Candidate[]): RelatedRoute[] {
  const seen = new Set<string>();
  const routes: RelatedRoute[] = [];
  for (const candidate of candidates) {
    for (const route of candidate.topic.relatedRoutes) {
      if (seen.has(route.href)) continue;
      seen.add(route.href);
      routes.push(route);
    }
  }
  return routes.slice(0, 3);
}

/** Secondary topics contribute one labelled block each, verbatim. */
function supportingSections(candidates: Candidate[]): AnswerSection[] {
  return candidates.map((candidate) => ({
    title: candidate.topic.title,
    body: candidate.topic.shortAnswer,
    facts: candidate.topic.detail.slice(0, 2),
  }));
}

/* --------------------------------------------------------------- scenario answers */

function scenarioAnswer(facts: ScenarioFacts, intent: Intent): ComposedAnswer {
  return {
    kind: "answer",
    intent,
    category: "Scenario",
    heading: `${facts.id} · ${facts.name}`,
    lead: `${facts.behavior}. ${facts.purpose}.`,
    facts: [conditionSummary(facts), faultSummary(facts), ...outputFacts(facts)],
    sections: [],
    figures: facts.output
      ? [
          { label: "Final engine", value: degrees(facts.output.engineEndC) },
          { label: "Final coolant", value: degrees(facts.output.coolantEndC) },
          { label: "Duration", value: seconds(facts.conditions.durationS) },
        ]
      : [],
    notes: facts.output ? [CANONICAL_OUTPUT_PROVENANCE] : [],
    routes: SCENARIO_ROUTES,
    suggestions: [
      `Compare ${facts.id} and ${facts.basedOn ?? "S-03"}.`,
      "Which canonical scenario finishes hottest?",
      "What are the canonical scenarios?",
    ].slice(0, 3),
    sourceTopicIds: ["canonical-scenarios"],
    entities: [],
    repairs: [],
  };
}

function scenarioComparisonAnswer(aId: string, bId: string, intent: Intent): ComposedAnswer | null {
  const comparison = compareScenarios(aId, bId);
  if (!comparison) return null;

  const { a, b, differences, sharedBaseline, outcome } = comparison;

  const facts: string[] = [];
  if (sharedBaseline) {
    facts.push(`Both are based on ${sharedBaseline}, so the operating condition is held constant and only the fault differs.`);
  }
  for (const difference of differences) {
    facts.push(`${difference.label} — ${a.id}: ${difference.a} · ${b.id}: ${difference.b}`);
  }
  if (outcome) facts.push(outcome);

  return {
    kind: "answer",
    intent,
    category: "Scenario",
    heading: `${a.id} vs ${b.id}`,
    lead: `${a.id} is ${a.behavior.toLowerCase()}; ${b.id} is ${b.behavior.toLowerCase()}.`,
    facts,
    sections: [
      { title: `${a.id} · ${a.name}`, body: conditionSummary(a), facts: outputFacts(a).slice(0, 2) },
      { title: `${b.id} · ${b.name}`, body: conditionSummary(b), facts: outputFacts(b).slice(0, 2) },
    ],
    figures: [],
    notes: [CANONICAL_OUTPUT_PROVENANCE, RANKING_CAVEAT],
    routes: SCENARIO_ROUTES,
    suggestions: [`What is ${a.id}?`, `What is ${b.id}?`, "Which canonical scenario finishes hottest?"],
    sourceTopicIds: ["canonical-scenarios", "fault-scenarios"],
    entities: [],
    repairs: [],
  };
}

function rankingAnswer(
  metric: Parameters<typeof rankScenarios>[0],
  direction: "highest" | "lowest",
  intent: Intent,
): ComposedAnswer {
  const ranking = rankScenarios(metric, direction);
  const top = ranking.entries[0];
  const rest = ranking.entries.slice(1, 4);

  return {
    kind: "answer",
    intent,
    category: "Scenario",
    heading: `Canonical scenarios by ${ranking.label}`,
    lead: `${top.facts.id} ${top.facts.name} has the ${direction} ${ranking.label} of the nine canonical scenarios, at ${top.display}.`,
    facts: rest.map((entry) => `${entry.facts.id} ${entry.facts.name} — ${entry.display}`),
    sections: [],
    figures: ranking.entries
      .slice(0, 3)
      .map((entry) => ({ label: entry.facts.id, value: entry.display, note: entry.facts.behavior })),
    notes: [CANONICAL_OUTPUT_PROVENANCE, RANKING_CAVEAT],
    routes: SCENARIO_ROUTES,
    suggestions: [`What is ${top.facts.id}?`, "What are the canonical scenarios?", "What do the degradation scenarios show?"],
    sourceTopicIds: ["canonical-scenarios"],
    entities: [],
    repairs: [],
  };
}

/** Knowledge topic that explains each scenario group. */
const CATEGORY_TOPIC: Record<ScenarioFacts["category"], string> = {
  Baseline: "canonical-scenarios",
  Fault: "fault-scenarios",
  Degradation: "degradation-scenarios",
};

function scenarioSetAnswer(
  category: ScenarioFacts["category"],
  intent: Intent,
): ComposedAnswer {
  const set = scenariosInCategory(category);
  const explainer = topicById(CATEGORY_TOPIC[category]);

  return {
    kind: "answer",
    intent,
    category: "Scenario",
    heading: `${category} scenarios`,
    lead: `${set.length} of the nine canonical scenarios are in the ${category.toLowerCase()} group.`,
    facts: set.map((facts) => `${facts.id} ${facts.name} — ${facts.behavior}.`),
    sections: explainer
      ? [{ title: explainer.title, body: explainer.shortAnswer, facts: explainer.detail.slice(0, 2) }]
      : [],
    figures: [],
    notes: [],
    routes: SCENARIO_ROUTES,
    suggestions: [
      `What is ${set[0]?.id ?? "S-01"}?`,
      "What are the canonical scenarios?",
      "Which canonical scenario finishes hottest?",
    ],
    sourceTopicIds: dedupe(["canonical-scenarios", explainer?.id ?? ""]),
    entities: [],
    repairs: [],
  };
}

/* -------------------------------------------------------------------- run answers */

function runAnswer(run: RunReadout, kind: ReturnType<typeof classifyRunQuestion>): ComposedAnswer | null {
  if (!kind) return null;

  const base = {
    kind: "answer" as const,
    intent: "numerical_question" as Intent,
    category: "Run" as AnswerCategory,
    sections: [],
    routes: [{ label: "Back to this result", href: `/results/${run.runId}` }],
    suggestions: ["Did energy balance pass?", "What scenario is this?", "How long did this simulation run?"],
    sourceTopicIds: [] as string[],
    entities: [] as Entity[],
    repairs: [] as { from: string; to: string }[],
    notes: [
      "Read directly from the computed result already returned by the VTMS-V1 Python engine for this run. Not measured vehicle telemetry.",
    ],
  };

  switch (kind) {
    case "final_temperature":
      return {
        ...base,
        heading: "Final state of this run",
        lead: `This run ends at ${degrees(run.finalEngineC)} engine and ${degrees(run.finalCoolantC)} coolant.`,
        facts: [`Scenario: ${run.scenarioName} (${run.scenarioId}).`, `Duration: ${seconds(run.durationS)}.`],
        figures: [
          { label: "Final engine", value: degrees(run.finalEngineC) },
          { label: "Final coolant", value: degrees(run.finalCoolantC) },
        ],
      };
    case "peak_temperature":
      return {
        ...base,
        heading: "Peak state of this run",
        lead: `Peak values were ${degrees(run.peakEngineC)} engine and ${degrees(run.peakCoolantC)} coolant.`,
        facts: [`Scenario: ${run.scenarioName} (${run.scenarioId}).`],
        figures: [
          { label: "Peak engine", value: degrees(run.peakEngineC) },
          { label: "Peak coolant", value: degrees(run.peakCoolantC) },
        ],
      };
    case "energy_balance":
      return {
        ...base,
        heading: "Energy balance for this run",
        lead: run.energyBalancePass
          ? "Energy conservation passed for this run."
          : "Energy conservation did not meet the reporting tolerance for this run.",
        facts: [
          `Normalized residual: ${run.normalizedResidual.toExponential(2)}.`,
          "This is a numerical check on the solver, not physical validation of the parameter values.",
        ],
        figures: [{ label: "Energy balance", value: run.energyBalancePass ? "Pass" : "Outside tolerance" }],
      };
    case "scenario_identity":
      return {
        ...base,
        heading: "What this run is",
        lead: `${run.scenarioName} (${run.scenarioId}), computed by ${run.modelId} using the ${run.equationSet} equation set.`,
        facts: [`Run ID: ${run.runId}.`, `Duration: ${seconds(run.durationS)}.`],
        figures: [],
      };
    case "duration":
      return {
        ...base,
        heading: "Run duration",
        lead: `This simulation covers ${seconds(run.durationS)} of modelled time.`,
        facts: [`Scenario: ${run.scenarioName} (${run.scenarioId}).`],
        figures: [{ label: "Duration", value: seconds(run.durationS) }],
      };
    case "fan":
      return {
        ...base,
        heading: "Fan activity in this run",
        lead: run.fanActivated
          ? "The fan was commanded on at some point during this run."
          : "The fan command stayed at zero for the whole run.",
        facts: [`Scenario: ${run.scenarioName} (${run.scenarioId}).`],
        figures: [{ label: "Fan activated", value: run.fanActivated ? "Yes" : "No" }],
      };
    case "solver":
      return {
        ...base,
        heading: "Solver status for this run",
        lead: run.solverSuccess ? "The RK45 integration completed successfully." : "The solver reported a warning for this run.",
        facts: [`Scenario: ${run.scenarioName} (${run.scenarioId}).`],
        figures: [],
      };
    default:
      return null;
  }
}

/* ------------------------------------------------------- knowledge-base answers */

function topicAnswer(
  primary: Candidate,
  supporting: Candidate[],
  intent: Intent,
  entities: Entity[],
  repairs: { from: string; to: string }[],
): ComposedAnswer {
  const topic = primary.topic;
  const useSections =
    supporting.length > 0 &&
    (intent === "explanation" || intent === "comparison" || intent === "follow_up");

  const facts =
    intent === "definition" || intent === "follow_up"
      ? topic.detail.slice(0, 3)
      : topic.detail.slice(0, 4);

  return {
    kind: "answer",
    intent,
    category: topic.category,
    heading: topic.title,
    lead: topic.shortAnswer,
    facts,
    sections: useSections ? supportingSections(supporting) : [],
    figures: [],
    notes: [],
    routes: routesFrom([primary, ...supporting]),
    suggestions: suggestionsFrom([primary, ...supporting]),
    sourceTopicIds: [primary.topic.id, ...supporting.map((candidate) => candidate.topic.id)],
    entities,
    repairs,
  };
}

/** Status answers always pair completed evidence with what is still pending. */
function statusAnswer(primary: Candidate, entities: Entity[], repairs: { from: string; to: string }[]): ComposedAnswer {
  const standing = topicById("validation-status");
  const ladder = topicById("verification-and-validation");
  const topic = primary.topic;

  const sections: AnswerSection[] = [];
  if (ladder && ladder.id !== topic.id) {
    sections.push({ title: "Where the evidence stands", body: ladder.shortAnswer, facts: ladder.detail.slice(0, 4) });
  }

  return {
    kind: "answer",
    intent: "status",
    category: "Validation",
    heading: topic.title,
    lead: topic.shortAnswer,
    facts: topic.detail.slice(0, 3),
    sections,
    figures: [],
    notes: standing && standing.id !== topic.id ? [standing.shortAnswer] : [],
    routes: [{ label: "See the evidence ladder", href: "/validation" }],
    suggestions: suggestionsFrom([primary], ["Is VTMS a digital twin?"]),
    sourceTopicIds: dedupe([topic.id, ladder?.id ?? "", standing?.id ?? ""]),
    entities,
    repairs,
  };
}

/** Capability and exclusion questions are answered from the model boundary. */
function boundaryAnswer(
  intent: Intent,
  primary: Candidate | undefined,
  entities: Entity[],
  repairs: { from: string; to: string }[],
): ComposedAnswer | null {
  const exclusions = topicById("model-exclusions");
  if (!exclusions) return null;

  const topic = primary && primary.topic.id !== exclusions.id ? primary.topic : undefined;

  return {
    kind: "answer",
    intent,
    category: "Physics",
    heading: intent === "exclusion" ? "Outside the VTMS-V1 boundary" : "What VTMS-V1 can answer",
    lead: exclusions.shortAnswer,
    facts: exclusions.detail.slice(0, 3),
    sections: topic ? [{ title: topic.title, body: topic.shortAnswer, facts: topic.detail.slice(0, 2) }] : [],
    figures: [],
    notes: [],
    routes: [{ label: "Review the model boundary", href: "/model" }],
    suggestions: ["What is VTMS and what does it simulate?", "Is VTMS a digital twin?", "What is the current validation status?"],
    sourceTopicIds: dedupe([exclusions.id, topic?.id ?? ""]),
    entities,
    repairs,
  };
}

function clarify(first: Candidate, second: Candidate): ClarifyResponse {
  return {
    kind: "clarify",
    question: `Are you asking about “${first.topic.title}” or “${second.topic.title}”?`,
    options: [
      { label: first.topic.title, query: first.topic.keywords[0] ?? first.topic.title },
      { label: second.topic.title, query: second.topic.keywords[0] ?? second.topic.title },
    ],
    suggestions: dedupe([
      ...first.topic.followUpQuestions.slice(0, 1),
      ...second.topic.followUpQuestions.slice(0, 1),
    ]).slice(0, 3),
  };
}

const fallback = (): FallbackResponse => ({
  kind: "fallback",
  answer: FALLBACK_ANSWER,
  suggestions: [...FALLBACK_SUGGESTIONS],
});

/* ---------------------------------------------------------------------- entry */

const CATEGORY_WORDS: [RegExp, ScenarioFacts["category"]][] = [
  [/\bdegradation\b/, "Degradation"],
  [/\bfault\b/, "Fault"],
  [/\bbaseline\b/, "Baseline"],
];

/**
 * Answer a question.
 *
 * The pipeline is: extract entities → classify intent → rank knowledge topics →
 * select a composition template → emit an answer built only from approved material.
 * The updated conversation context is returned alongside the response so the caller
 * can carry it into the next turn.
 */
export function answerQuestion(question: string, options: AnswerOptions = {}): AnswerOutcome {
  const context = options.context ?? emptyContext();
  const trimmed = question.trim();

  if (!trimmed) return { response: fallback(), context };

  const retrieval = rankTopics(trimmed, { conversation: context });
  const { entities, repairs, candidates, scored, repairedQuery } = retrieval;
  const analysis = classifyIntent(trimmed, entities);
  const canonical = canonicalize(trimmed);

  // A run in view answers readout questions about itself before anything else.
  if (options.run) {
    const runAnswerKind = classifyRunQuestion(canonical);
    const composed = runAnswer(options.run, runAnswerKind);
    if (composed) {
      return {
        response: composed,
        context: advanceContext(context, { entities, intent: composed.intent, topicIds: [] }),
      };
    }
  }

  const askedScenarioIds = scenarioIdsIn(entities);
  // A short follow-up with no scenario of its own inherits the one in context.
  const scenarioIds =
    askedScenarioIds.length > 0
      ? askedScenarioIds
      : analysis.isFollowUp
        ? context.scenarioIds.slice(0, 1)
        : [];

  const finish = (response: AssistantResponse, topicIds: string[]): AnswerOutcome => ({
    response,
    context: advanceContext(context, { entities, intent: analysis.intent, topicIds }),
  });

  /* Scenario intelligence ------------------------------------------------- */

  if (analysis.intent === "numerical_question") {
    // A named scenario answers about itself; otherwise the question is a ranking
    // across the canonical suite.
    if (scenarioIds.length === 1) {
      const facts = scenarioFacts(scenarioIds[0]);
      if (facts) {
        const composed = scenarioAnswer(facts, analysis.intent);
        return finish(composed, composed.sourceTopicIds);
      }
    }
    if (analysis.ranking) {
      const composed = rankingAnswer(analysis.ranking.metric, analysis.ranking.direction, analysis.intent);
      return finish(composed, composed.sourceTopicIds);
    }
  }

  if (analysis.intent === "scenario_comparison" && scenarioIds.length >= 2) {
    const composed = scenarioComparisonAnswer(scenarioIds[0], scenarioIds[1], analysis.intent);
    if (composed) return finish(composed, composed.sourceTopicIds);
  }

  if (analysis.intent === "scenario_lookup" || analysis.intent === "scenario_comparison") {
    for (const [pattern, category] of CATEGORY_WORDS) {
      if (pattern.test(` ${repairedQuery} `)) {
        const composed = scenarioSetAnswer(category, analysis.intent);
        return finish(composed, composed.sourceTopicIds);
      }
    }

    if (scenarioIds.length === 1) {
      const facts = scenarioFacts(scenarioIds[0]);
      if (facts) {
        const composed = scenarioAnswer(facts, analysis.intent);
        return finish(composed, composed.sourceTopicIds);
      }
    }
  }

  /* Boundary questions ---------------------------------------------------- */

  if (analysis.intent === "exclusion" || analysis.intent === "capability") {
    const composed = boundaryAnswer(analysis.intent, candidates[0], entities, repairs);
    if (composed) return finish(composed, composed.sourceTopicIds);
  }

  /* Knowledge-base answers ------------------------------------------------ */

  // A genuine follow-up: the visitor named a VTMS entity but left the subject implicit
  // ("what about at idle?"). Carry the subject forward and let the new entity's topics
  // supply the supporting blocks. Requires a domain entity, so an unrelated question
  // can never inherit a subject this way.
  if (candidates.length === 0 && analysis.isFollowUp && entities.length > 0) {
    const carried = context.recentTopicIds.map((id) => topicById(id)).find(Boolean);
    if (carried) {
      const primary: Candidate = { topic: carried, score: MIN_CONFIDENCE, matchedTerms: [], confidence: 0.5 };
      const supportingTopics = scored
        .filter((candidate) => candidate.topic.id !== carried.id && candidate.score >= MIN_SUPPORT_SCORE)
        .slice(0, 2);
      const composed = topicAnswer(primary, supportingTopics, "follow_up", entities, repairs);
      return finish(composed, composed.sourceTopicIds);
    }
  }

  if (candidates.length === 0) {
    // Status questions have a definite answer even when the wording matches no
    // keyword: the model's standing is always reportable.
    if (analysis.intent === "status") {
      const standing = topicById("validation-status");
      if (standing) {
        const composed = statusAnswer(
          { topic: standing, score: MIN_SUPPORT_SCORE, matchedTerms: [], confidence: 0.5 },
          entities,
          repairs,
        );
        return finish(composed, composed.sourceTopicIds);
      }
    }
    return finish(fallback(), []);
  }

  if (retrieval.ambiguous && candidates.length >= 2) {
    return finish(clarify(candidates[0], candidates[1]), []);
  }

  const primary = candidates[0];

  if (analysis.intent === "status") {
    const composed = statusAnswer(primary, entities, repairs);
    return finish(composed, composed.sourceTopicIds);
  }

  // Synthesis: keep supporting topics that are clearly relevant and clearly weaker,
  // so an explanation can draw on two or three approved sources at once.
  const supporting = scored
    .filter(
      (candidate) =>
        candidate.topic.id !== primary.topic.id &&
        candidate.score >= MIN_SUPPORT_SCORE &&
        candidate.score < primary.score,
    )
    .slice(0, 2);

  const composed = topicAnswer(primary, supporting, analysis.intent, entities, repairs);
  return finish(composed, composed.sourceTopicIds);
}

/**
 * Supporting topics may sit below the answer floor: they never answer on their own,
 * they only add an approved block underneath a primary answer that already qualified.
 */
const MIN_SUPPORT_SCORE = 2.5;

export { ASSISTANT_DISCLOSURE };
export type { KnowledgeTopic, RelatedRoute };
