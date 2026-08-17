/**
 * Bounded conversation context.
 *
 * The assistant remembers a small, fixed amount of the current browser session so short
 * follow-ups ("what about at idle?", "and if the fan fails?") stay in the right subject
 * area. Every list is capped, and the context is a weak signal by construction: it can
 * break a tie or supply a missing subject for a genuine follow-up, but it can never
 * turn an unrelated question into a VTMS match.
 */

import type { Entity } from "./assistant-entities";
import type { Intent } from "./assistant-intent";

const MAX_TOPICS = 3;
const MAX_SCENARIOS = 2;
const MAX_COMPONENTS = 2;
const MAX_CONDITIONS = 2;

export type ConversationContext = {
  recentTopicIds: string[];
  scenarioIds: string[];
  components: string[];
  conditions: string[];
  evidenceConcept: string | null;
  lastIntent: Intent | null;
};

export const emptyContext = (): ConversationContext => ({
  recentTopicIds: [],
  scenarioIds: [],
  components: [],
  conditions: [],
  evidenceConcept: null,
  lastIntent: null,
});

const prepend = (list: string[], values: string[], limit: number): string[] => {
  const merged = [...values, ...list.filter((item) => !values.includes(item))];
  return merged.slice(0, limit);
};

/**
 * Fold a completed turn into the context.
 *
 * Entities named in the current question replace older ones of the same kind, so the
 * subject moves with the conversation instead of accumulating indefinitely.
 */
export function advanceContext(
  context: ConversationContext,
  turn: {
    entities: Entity[];
    intent: Intent;
    topicIds: string[];
  },
): ConversationContext {
  const kind = (name: Entity["kind"]) =>
    turn.entities.filter((entity) => entity.kind === name).map((entity) => entity.id);

  const evidence = kind("evidence");

  return {
    recentTopicIds: prepend(context.recentTopicIds, turn.topicIds, MAX_TOPICS),
    scenarioIds: prepend(context.scenarioIds, kind("scenario"), MAX_SCENARIOS),
    components: prepend(context.components, kind("component"), MAX_COMPONENTS),
    conditions: prepend(context.conditions, kind("condition"), MAX_CONDITIONS),
    evidenceConcept: evidence[0] ?? context.evidenceConcept,
    lastIntent: turn.intent,
  };
}

/** Context carried into retrieval scoring. Reset clears all of it. */
export const contextTopicIds = (context: ConversationContext): string[] => context.recentTopicIds;
