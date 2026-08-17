"use client";

import { usePathname } from "next/navigation";
import { createContext, useCallback, useContext, useMemo, useState } from "react";

import {
  type AssistantResponse,
  answerQuestion,
} from "@/lib/assistant-compose";
import { type ConversationContext, emptyContext } from "@/lib/assistant-context";
import { readRunForPathname } from "@/lib/assistant-run-context";

/**
 * Conversation state for the VTMS Knowledge Assistant.
 *
 * One provider sits in the application shell so the floating panel and the /assistant
 * route share a single transcript for the browser session. Answers are composed
 * synchronously from the bundled knowledge base — there is nothing to await and no
 * request to make.
 *
 * On a computed-result route the provider also hands the composer the run that is
 * already in session storage, so readout questions ("what is the final coolant
 * temperature?") can be answered from that authoritative record.
 */

export type AssistantTurn =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; response: AssistantResponse };

type AssistantState = {
  turns: AssistantTurn[];
  conversation: ConversationContext;
  panelOpen: boolean;
  /** Suggestions attached to the most recent answer. */
  followUps: string[];
  ask: (question: string) => void;
  reset: () => void;
  setPanelOpen: (open: boolean) => void;
};

const AssistantContext = createContext<AssistantState | null>(null);

/** Deterministic ids: no Math.random or Date.now, so nothing can desynchronize. */
let turnCounter = 0;
const nextId = (prefix: string) => `${prefix}-${(turnCounter += 1)}`;

export function AssistantProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [turns, setTurns] = useState<AssistantTurn[]>([]);
  const [conversation, setConversation] = useState<ConversationContext>(emptyContext);
  const [panelOpen, setPanelOpen] = useState(false);

  const ask = useCallback(
    (question: string) => {
      const trimmed = question.trim();
      if (!trimmed) return;

      const run = readRunForPathname(pathname);
      const outcome = answerQuestion(trimmed, { context: conversation, run });

      setTurns((current) => [
        ...current,
        { id: nextId("q"), role: "user", text: trimmed },
        { id: nextId("a"), role: "assistant", response: outcome.response },
      ]);
      setConversation(outcome.context);
    },
    [conversation, pathname],
  );

  const reset = useCallback(() => {
    setTurns([]);
    setConversation(emptyContext());
  }, []);

  const followUps = useMemo(() => {
    const last = turns[turns.length - 1];
    if (!last || last.role !== "assistant") return [];
    return last.response.suggestions;
  }, [turns]);

  const value = useMemo<AssistantState>(
    () => ({ turns, conversation, panelOpen, followUps, ask, reset, setPanelOpen }),
    [turns, conversation, panelOpen, followUps, ask, reset],
  );

  return <AssistantContext.Provider value={value}>{children}</AssistantContext.Provider>;
}

export function useAssistant(): AssistantState {
  const value = useContext(AssistantContext);
  if (!value) throw new Error("useAssistant must be used inside AssistantProvider");
  return value;
}
