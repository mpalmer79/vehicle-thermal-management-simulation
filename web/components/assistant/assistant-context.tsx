"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import { type RelatedRoute } from "@/lib/assistant-knowledge";
import { retrieveAnswer } from "@/lib/assistant-retrieval";

/**
 * Conversation state for the VTMS Knowledge Assistant.
 *
 * One provider sits in the application shell so the floating panel and the /assistant
 * route share a single transcript for the browser session. Answers are resolved
 * synchronously from the bundled knowledge base — there is nothing to await and no
 * request to make.
 */

export type AssistantTurn =
  | { id: string; role: "user"; text: string }
  | {
      id: string;
      role: "assistant";
      /** Topic title, or undefined for the fallback response. */
      heading?: string;
      text: string;
      facts: string[];
      routes: RelatedRoute[];
      suggestions: string[];
    };

type AssistantState = {
  turns: AssistantTurn[];
  /** Last matched topic, used to keep short follow-ups in context. */
  lastTopicId: string | null;
  panelOpen: boolean;
  ask: (question: string) => void;
  reset: () => void;
  setPanelOpen: (open: boolean) => void;
};

const AssistantContext = createContext<AssistantState | null>(null);

/** Deterministic ids: no Math.random or Date.now, so nothing can desynchronize. */
let turnCounter = 0;
const nextId = (prefix: string) => `${prefix}-${(turnCounter += 1)}`;

export function AssistantProvider({ children }: { children: React.ReactNode }) {
  const [turns, setTurns] = useState<AssistantTurn[]>([]);
  const [lastTopicId, setLastTopicId] = useState<string | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);

  const ask = useCallback(
    (question: string) => {
      const trimmed = question.trim();
      if (!trimmed) return;

      const result = retrieveAnswer(trimmed, { lastTopicId });

      const answer: AssistantTurn =
        result.kind === "match"
          ? {
              id: nextId("a"),
              role: "assistant",
              heading: result.topic.title,
              text: result.topic.shortAnswer,
              facts: result.topic.detail,
              routes: result.topic.relatedRoutes,
              suggestions: result.suggestions,
            }
          : {
              id: nextId("a"),
              role: "assistant",
              text: result.answer,
              facts: [],
              routes: [],
              suggestions: result.suggestions,
            };

      setTurns((current) => [...current, { id: nextId("q"), role: "user", text: trimmed }, answer]);
      setLastTopicId(result.kind === "match" ? result.topic.id : null);
    },
    [lastTopicId],
  );

  const reset = useCallback(() => {
    setTurns([]);
    setLastTopicId(null);
  }, []);

  const value = useMemo<AssistantState>(
    () => ({ turns, lastTopicId, panelOpen, ask, reset, setPanelOpen }),
    [turns, lastTopicId, panelOpen, ask, reset],
  );

  return <AssistantContext.Provider value={value}>{children}</AssistantContext.Provider>;
}

export function useAssistant(): AssistantState {
  const value = useContext(AssistantContext);
  if (!value) throw new Error("useAssistant must be used inside AssistantProvider");
  return value;
}
