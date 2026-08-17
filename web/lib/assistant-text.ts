/**
 * Shared text normalization for the VTMS Knowledge Assistant.
 *
 * Everything here is deterministic string work: no model, no network, no learned
 * weights. The same canonical form is applied to visitor questions and to every
 * knowledge-base term at module load, so the two are always compared alike.
 */

/** Words that carry no retrieval signal on their own. */
export const STOPWORDS = new Set([
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

export function singularize(token: string): string {
  if (PROTECTED_TOKENS.has(token)) return token;
  if (token.length <= 3 || !token.endsWith("s")) return token;
  // "bypass", "status", "analysis" are not plurals.
  if (/(ss|us|is)$/.test(token)) return token;
  return token.slice(0, -1);
}

/**
 * Reduce free text to a canonical space-separated token string.
 *
 * Scenario identities are folded first so `S-03`, `S03`, `s 3` and `s3` all become
 * `s03` and can be matched as a single token.
 */
export function canonicalize(text: string): string {
  let value = text
    .toLowerCase()
    .replace(/\bs[\s-]?0?(\d)\b/g, "s0$1")
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

export function contentTokens(canonical: string): string[] {
  return canonical.split(" ").filter((token) => token.length > 0 && !STOPWORDS.has(token));
}

/* ------------------------------------------------------------ fuzzy matching */

/**
 * Levenshtein distance with an early exit once the best possible result exceeds
 * `max`. Bounded work: the assistant only ever compares short single tokens.
 */
export function boundedEditDistance(a: string, b: string, max: number): number {
  if (a === b) return 0;
  if (Math.abs(a.length - b.length) > max) return max + 1;

  let previous = Array.from({ length: b.length + 1 }, (_, index) => index);

  for (let i = 1; i <= a.length; i += 1) {
    const current = [i];
    let rowBest = i;

    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const value = Math.min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + cost);
      current.push(value);
      if (value < rowBest) rowBest = value;
    }

    if (rowBest > max) return max + 1;
    previous = current;
  }

  return previous[b.length];
}

/**
 * Edit budget for a misspelling. Deliberately tight: one edit for ordinary words,
 * two only for long ones. This is what keeps `engineer` from collapsing into
 * `engine` (distance 2 at length 8) while still repairing `raditor`, `coolent`,
 * `thermostate`, and `temperture`.
 */
export function editBudget(token: string): number {
  if (token.length < 5) return 0;
  if (token.length <= 8) return 1;
  return 2;
}

/**
 * Repair one token against a closed vocabulary.
 *
 * Returns undefined unless exactly one vocabulary word sits at the minimum distance,
 * so an ambiguous near-miss is left alone rather than guessed. Callers must only pass
 * tokens that are not already known vocabulary.
 */
export function nearestVocabularyTerm(
  token: string,
  vocabulary: Iterable<string>,
): string | undefined {
  const budget = editBudget(token);
  if (budget === 0) return undefined;

  let best: string | undefined;
  let bestDistance = budget + 1;
  let tied = false;

  for (const candidate of vocabulary) {
    if (candidate.length < 5) continue;
    const distance = boundedEditDistance(token, candidate, budget);
    if (distance > budget) continue;

    if (distance < bestDistance) {
      best = candidate;
      bestDistance = distance;
      tied = false;
    } else if (distance === bestDistance && candidate !== best) {
      tied = true;
    }
  }

  return tied ? undefined : best;
}
