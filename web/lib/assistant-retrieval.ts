/**
 * VTMS Knowledge Assistant local deterministic retrieval.
 *
 * A question is canonicalized, spell-repaired against a closed VTMS vocabulary, and
 * scored against every knowledge-base topic. Unlike the first implementation this
 * returns a ranked candidate list rather than a single winner, so the answer composer
 * can synthesize across two or three related topics when the intent calls for it, and
 * can ask for clarification when the top candidates are near-tied and unrelated.
 *
 * There is no model, no generation, and no network access. Every fact ultimately comes
 * from a curated knowledge-base entry or an explicit current-project status override.
 */

import {
  FALLBACK_ANSWER,
  FALLBACK_SUGGESTIONS,
  type KnowledgeTopic,
  knowledgeTopics,
} from "./assistant-knowledge";
import { type Entity, extractEntities } from "./assistant-entities";
import { canonicalize, contentTokens } from "./assistant-text";
import type { ConversationContext } from "./assistant-context";
import { withCurrentProjectStatus } from "./assistant-status-overrides";

export { canonicalize };

/* ------------------------------------------------------------------- scoring */

const WEIGHT = {
  keywordPhrase: 7,
  keywordToken: 4,
  synonymPhrase: 5,
  synonymToken: 3,
  titleToken: 0.75,
  entity: 2.5,
  contextTopic: 1.5,
  contextRelated: 1,
} as const;

export const MIN_CONFIDENCE = 4;
export const AMBIGUITY_MARGIN = 1.0;

const ENTITY_TOPIC_HINTS: Record<string, string[]> = {
  engine: ["engine-thermal-state", "engine-to-coolant"],
  coolant: ["coolant-thermal-state", "two-state-model"],
  radiator: ["radiator-heat-rejection", "epsilon-ntu"],
  thermostat: ["thermostat"],
  bypass: ["bypass-flow"],
  pump: ["coolant-pump"],
  fan: ["cooling-fan"],
  airflow: ["ram-airflow"],
  ambient: ["ambient-temperature"],
  verification: ["verification", "automated-tests"],
  validation: ["validation-status", "verification-and-validation"],
  kit: ["kit-plausibility"],
  argonne: ["argonne"],
  calibration: ["calibration-vs-holdout"],
  holdout: ["calibration-vs-holdout"],
  "digital-twin": ["digital-twin"],
  "vtms-v1": ["vtms-v1"],
  "em-v1": ["vtms-v1"],
  "michael-palmer": ["creator"],
  idle: ["cooling-fan", "ram-airflow"],
  highway: ["ram-airflow", "radiator-heat-rejection"],
  "cold-start": ["thermostat", "two-state-model"],
  "high-load": ["engine-thermal-state"],
};

type IndexedTopic = {
  topic: KnowledgeTopic;
  keywordPhrases: string[];
  keywordTokens: string[];
  synonymPhrases: string[];
  synonymTokens: string[];
  titleTokens: string[];
};

function indexTerms(terms: string[]): { phrases: string[]; tokens: string[] } {
  const phrases: string[] = [];
  const tokens: string[] = [];

  for (const term of terms) {
    const canonical = canonicalize(term);
    if (!canonical) continue;
    if (canonical.includes(" ")) phrases.push(canonical);
    else tokens.push(canonical);
  }

  return { phrases, tokens };
}

/**
 * Built once at module load. Current-project overrides are applied before indexing so
 * the Assistant 2.0 composer cannot regress to stale validation status after the
 * Argonne data-receipt milestone.
 */
const INDEX: IndexedTopic[] = knowledgeTopics.map((baseTopic) => {
  const topic = withCurrentProjectStatus(baseTopic);
  const keywords = indexTerms(topic.keywords);
  const synonyms = indexTerms(topic.synonyms);

  return {
    topic,
    keywordPhrases: keywords.phrases,
    keywordTokens: keywords.tokens,
    synonymPhrases: synonyms.phrases,
    synonymTokens: synonyms.tokens,
    titleTokens: contentTokens(canonicalize(topic.title)),
  };
});

const INDEX_BY_ID = new Map(INDEX.map((entry) => [entry.topic.id, entry]));

function scoreTopic(
  entry: IndexedTopic,
  canonicalQuery: string,
  queryTokens: Set<string>,
): { score: number; matched: string[] } {
  const padded = ` ${canonicalQuery} `;
  const matched: string[] = [];
  let score = 0;

  for (const phrase of entry.keywordPhrases) {
    if (padded.includes(` ${phrase} `)) {
      score += WEIGHT.keywordPhrase;
      matched.push(phrase);
    }
  }
  for (const token of entry.keywordTokens) {
    if (queryTokens.has(token)) {
      score += WEIGHT.keywordToken;
      matched.push(token);
    }
  }
  for (const phrase of entry.synonymPhrases) {
    if (padded.includes(` ${phrase} `)) {
      score += WEIGHT.synonymPhrase;
      matched.push(phrase);
    }
  }
  for (const token of entry.synonymTokens) {
    if (queryTokens.has(token)) {
      score += WEIGHT.synonymToken;
      matched.push(token);
    }
  }
  for (const token of entry.titleTokens) {
    if (queryTokens.has(token)) score += WEIGHT.titleToken;
  }

  return { score, matched };
}

/* -------------------------------------------------------------------- public */

export type Candidate = {
  topic: KnowledgeTopic;
  score: number;
  matchedTerms: string[];
  confidence: number;
};

export type RetrievalContext = {
  conversation?: ConversationContext;
  lastTopicId?: string | null;
};

export type Retrieval = {
  candidates: Candidate[];
  scored: Candidate[];
  entities: Entity[];
  repairs: { from: string; to: string }[];
  canonicalQuery: string;
  repairedQuery: string;
  ambiguous: boolean;
};

const confidenceOf = (score: number) => Math.min(1, Math.round((score / 14) * 100) / 100);

function relatedness(a: KnowledgeTopic, b: KnowledgeTopic): boolean {
  if (a.relatedTopics?.includes(b.id)) return true;
  if (b.relatedTopics?.includes(a.id)) return true;
  return false;
}

export function rankTopics(question: string, context: RetrievalContext = {}): Retrieval {
  const canonicalQuery = canonicalize(question);
  const { entities, repairs, repairedQuery } = extractEntities(question);
  const queryTokens = new Set(contentTokens(repairedQuery));

  if (!repairedQuery || queryTokens.size === 0) {
    return { candidates: [], scored: [], entities, repairs, canonicalQuery, repairedQuery, ambiguous: false };
  }

  const entityTopicBoost = new Map<string, number>();
  for (const entity of entities) {
    for (const topicId of ENTITY_TOPIC_HINTS[entity.id] ?? []) {
      entityTopicBoost.set(topicId, (entityTopicBoost.get(topicId) ?? 0) + WEIGHT.entity);
    }
  }

  const contextIds = new Set(
    [...(context.conversation?.recentTopicIds ?? []), context.lastTopicId ?? ""].filter(Boolean),
  );
  const contextRelated = new Set<string>();
  for (const id of contextIds) {
    for (const related of INDEX_BY_ID.get(id)?.topic.relatedTopics ?? []) contextRelated.add(related);
  }

  const scored: Candidate[] = [];
  const baseScores = INDEX.map((entry) => scoreTopic(entry, repairedQuery, queryTokens));
  const hasDomainSignal =
    entities.length > 0 || baseScores.some((result) => result.score > 0) || entityTopicBoost.size > 0;

  INDEX.forEach((entry, index) => {
    const { score: base, matched } = baseScores[index];
    const entityBoost = entityTopicBoost.get(entry.topic.id) ?? 0;
    const carriesContext =
      hasDomainSignal && (contextIds.has(entry.topic.id) || contextRelated.has(entry.topic.id));
    if (base <= 0 && entityBoost <= 0 && !carriesContext) return;

    let score = base + entityBoost;
    if (contextIds.has(entry.topic.id)) score += WEIGHT.contextTopic;
    else if (contextRelated.has(entry.topic.id)) score += WEIGHT.contextRelated;

    scored.push({
      topic: entry.topic,
      score,
      matchedTerms: matched,
      confidence: confidenceOf(score),
    });
  });

  scored.sort((left, right) => right.score - left.score || left.topic.id.localeCompare(right.topic.id));

  const candidates = scored.filter((candidate) => candidate.score >= MIN_CONFIDENCE);

  const [first, second] = candidates;
  const ambiguous = Boolean(
    first &&
      second &&
      first.score - second.score <= AMBIGUITY_MARGIN &&
      !relatedness(first.topic, second.topic) &&
      queryTokens.size <= 4,
  );

  return { candidates, scored, entities, repairs, canonicalQuery, repairedQuery, ambiguous };
}

export type RetrievalMatch = {
  kind: "match";
  topic: KnowledgeTopic;
  score: number;
  suggestions: string[];
};

export type RetrievalFallback = {
  kind: "fallback";
  answer: string;
  suggestions: string[];
};

export type RetrievalResult = RetrievalMatch | RetrievalFallback;

export function retrieveAnswer(question: string, context: RetrievalContext = {}): RetrievalResult {
  const { candidates } = rankTopics(question, context);
  const best = candidates[0];

  if (!best) {
    return { kind: "fallback", answer: FALLBACK_ANSWER, suggestions: [...FALLBACK_SUGGESTIONS] };
  }

  return {
    kind: "match",
    topic: best.topic,
    score: best.score,
    suggestions: best.topic.followUpQuestions.slice(0, 3),
  };
}
