/**
 * VTMS Knowledge Assistant — local deterministic retrieval.
 *
 * This module contains the entire "intelligence" of the assistant: a question is
 * normalized, tokenized, and scored against the bundled knowledge base. The highest
 * scoring topic wins if it clears a confidence floor; otherwise the assistant says it
 * does not know.
 *
 * There is no model, no generation, and no network access. Every answer is a verbatim
 * knowledge-base entry from `assistant-knowledge.ts`.
 */

import {
  FALLBACK_ANSWER,
  FALLBACK_SUGGESTIONS,
  type KnowledgeTopic,
  knowledgeTopics,
} from "./assistant-knowledge";

/* -------------------------------------------------------------- normalization */

/** Words that carry no retrieval signal on their own. */
const STOPWORDS = new Set([
  "a", "an", "and", "any", "are", "as", "at", "be", "been", "but", "by", "can", "did", "do",
  "doe", "for", "from", "get", "give", "had", "has", "have", "how", "i", "if", "in", "into",
  "is", "it", "its", "just", "me", "much", "my", "of", "on", "one", "or", "so", "some", "tell",
  "than", "that", "the", "their", "them", "then", "there", "these", "they", "this", "to",
  "up", "use", "used", "very", "was", "we", "were", "what", "when", "where", "which", "who",
  "why", "will", "with", "would", "you", "your",
]);

/** Single-token terminology normalization applied before scoring. */
const TOKEN_ALIASES: Record<string, string> = {
  temp: "temperature",
  temps: "temperature",
  rad: "radiator",
  rads: "radiator",
  thermo: "thermostat",
  sim: "simulation",
  sims: "simulation",
  simulate: "simulation",
  simulating: "simulation",
  simulated: "simulation",
  coolent: "coolant",
  celcius: "celsius",
  repo: "repository",
  js: "javascript",
  py: "python",
};

/** Tokens that end in "s" but are not plurals. */
const PROTECTED_TOKENS = new Set(["vtms", "physics", "numerics", "celsius", "gas"]);

/** Multi-word phrase normalization applied to the whole canonical string. */
const PHRASE_ALIASES: [RegExp, string][] = [
  [/\be ntu\b/g, "epsilon ntu"],
  [/\beps ntu\b/g, "epsilon ntu"],
  [/\bwho (made|created|wrote|designed|develop|developed)\b/g, "who built"],
  [/\bdigital twins\b/g, "digital twin"],
  [/\bwater pump\b/g, "coolant pump"],
  [/\bair flow\b/g, "airflow"],
];

function singularize(token: string): string {
  if (PROTECTED_TOKENS.has(token)) return token;
  if (token.length <= 3 || !token.endsWith("s")) return token;
  // "bypass", "status", "analysis" are not plurals.
  if (/(ss|us|is)$/.test(token)) return token;
  return token.slice(0, -1);
}

/**
 * Reduce free text to a canonical space-separated token string. The same function is
 * applied to knowledge-base keywords at module load, so queries and keywords are always
 * compared in the same form.
 */
export function canonicalize(text: string): string {
  let value = text
    .toLowerCase()
    // Scenario identities: "S-03", "S03", "s 3" all become "s03".
    .replace(/\bs[\s-]?0?(\d)\b/g, "s0$1")
    // Everything that is not a letter or digit becomes a separator.
    .replace(/[^a-z0-9]+/g, " ")
    .trim();

  for (const [pattern, replacement] of PHRASE_ALIASES) {
    value = value.replace(pattern, replacement);
  }

  return value
    .split(" ")
    .filter(Boolean)
    .map((token) => singularize(TOKEN_ALIASES[token] ?? token))
    .join(" ");
}

function contentTokens(canonical: string): string[] {
  return canonical.split(" ").filter((token) => token.length > 0 && !STOPWORDS.has(token));
}

/* ------------------------------------------------------------------- scoring */

const WEIGHT = {
  keywordPhrase: 7,
  keywordToken: 4,
  synonymPhrase: 5,
  synonymToken: 3,
  titleToken: 0.75,
  contextSelf: 1.5,
  contextRelated: 1,
} as const;

/**
 * Confidence floor. One exact single-word keyword hit is exactly enough; anything
 * weaker falls back rather than guessing.
 */
export const MIN_CONFIDENCE = 4;

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

/** Built once at module load; the knowledge base is static. */
const INDEX: IndexedTopic[] = knowledgeTopics.map((topic) => {
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

function scoreTopic(entry: IndexedTopic, canonicalQuery: string, queryTokens: Set<string>): number {
  const padded = ` ${canonicalQuery} `;
  let score = 0;

  for (const phrase of entry.keywordPhrases) {
    if (padded.includes(` ${phrase} `)) score += WEIGHT.keywordPhrase;
  }
  for (const token of entry.keywordTokens) {
    if (queryTokens.has(token)) score += WEIGHT.keywordToken;
  }
  for (const phrase of entry.synonymPhrases) {
    if (padded.includes(` ${phrase} `)) score += WEIGHT.synonymPhrase;
  }
  for (const token of entry.synonymTokens) {
    if (queryTokens.has(token)) score += WEIGHT.synonymToken;
  }
  for (const token of entry.titleTokens) {
    if (queryTokens.has(token)) score += WEIGHT.titleToken;
  }

  return score;
}

/* -------------------------------------------------------------------- public */

export type RetrievalContext = {
  /** Topic matched by the previous question in this browser session, if any. */
  lastTopicId?: string | null;
};

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

function fallback(): RetrievalFallback {
  return { kind: "fallback", answer: FALLBACK_ANSWER, suggestions: [...FALLBACK_SUGGESTIONS] };
}

/**
 * Resolve a visitor question against the bundled knowledge base.
 *
 * `context.lastTopicId` supports short conversational follow-ups ("what about
 * airflow?") by giving a small boost to the previously matched topic and the topics it
 * declares as related. The boost is deliberately small: it can break a tie, but it can
 * never promote an unrelated topic past the confidence floor on its own.
 */
export function retrieveAnswer(question: string, context: RetrievalContext = {}): RetrievalResult {
  const canonicalQuery = canonicalize(question);
  if (!canonicalQuery) return fallback();

  const queryTokens = new Set(contentTokens(canonicalQuery));
  if (queryTokens.size === 0) return fallback();

  const contextTopic = context.lastTopicId
    ? INDEX.find((entry) => entry.topic.id === context.lastTopicId)
    : undefined;
  const relatedToContext = new Set(contextTopic?.topic.relatedTopics ?? []);

  let best: { entry: IndexedTopic; score: number } | null = null;

  for (const entry of INDEX) {
    const base = scoreTopic(entry, canonicalQuery, queryTokens);
    if (base <= 0) continue;

    let score = base;
    if (contextTopic) {
      if (entry.topic.id === contextTopic.topic.id) score += WEIGHT.contextSelf;
      else if (relatedToContext.has(entry.topic.id)) score += WEIGHT.contextRelated;
    }

    if (!best || score > best.score) best = { entry, score };
  }

  if (!best || best.score < MIN_CONFIDENCE) return fallback();

  return {
    kind: "match",
    topic: best.entry.topic,
    score: best.score,
    suggestions: best.entry.topic.followUpQuestions.slice(0, 3),
  };
}
