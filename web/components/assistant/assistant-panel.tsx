"use client";

import { useEffect, useRef, useState } from "react";

import { ASSISTANT_DISCLOSURE, PRESET_QUESTIONS } from "@/lib/assistant-knowledge";

import { useAssistant } from "./assistant-context";
import { AssistantMessage } from "./assistant-message";
import { PresetQuestions } from "./preset-questions";

/**
 * The conversational surface itself.
 *
 * `panel` renders inside the floating launcher sheet; `page` renders the /assistant
 * route. Both share one transcript through the assistant context, so a visitor can open
 * a question in the panel and continue it on the dedicated route.
 */
export function AssistantPanel({
  variant = "panel",
  onClose,
  autoFocus = false,
}: {
  variant?: "panel" | "page";
  onClose?: () => void;
  autoFocus?: boolean;
}) {
  const { turns, ask, reset } = useAssistant();
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const transcriptRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

  useEffect(() => {
    const node = transcriptRef.current;
    if (!node || turns.length === 0) return;
    node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
  }, [turns.length]);

  const submit = (question: string) => {
    ask(question);
    setDraft("");
    inputRef.current?.focus();
  };

  const lastTurn = turns[turns.length - 1];
  const followUps = lastTurn && lastTurn.role === "assistant" ? lastTurn.suggestions : [];

  return (
    <section className={`assistant-surface ${variant}`} aria-label="VTMS Knowledge Assistant">
      <header className="assistant-head">
        <div className="assistant-identity">
          <span className="assistant-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" role="presentation">
              <circle className="am-ring" cx="16" cy="16" r="12" />
              <path className="am-loop" d="M9,20 Q16,26 23,20" />
              <circle className="am-core" cx="16" cy="13" r="4.4" />
            </svg>
          </span>
          <div>
            <strong>VTMS Assistant</strong>
            <small>Local knowledge base</small>
          </div>
        </div>

        <div className="assistant-head-actions">
          {turns.length > 0 && (
            <button className="assistant-reset" onClick={reset} type="button">
              Clear
            </button>
          )}
          {onClose && (
            <button className="assistant-close" onClick={onClose} type="button" aria-label="Close assistant">
              <span aria-hidden="true">×</span>
            </button>
          )}
        </div>
      </header>

      <div className="assistant-transcript" ref={transcriptRef}>
        {turns.length === 0 ? (
          <div className="assistant-intro">
            <p>
              Ask about the thermal model, the canonical scenarios, verification and validation
              evidence, the system architecture, or the person who built it.
            </p>
            <PresetQuestions label="START HERE" onSelect={submit} questions={PRESET_QUESTIONS} />
          </div>
        ) : (
          <>
            <ul aria-live="polite" className="assistant-turns" role="log">
              {turns.map((turn) => (
                <AssistantMessage key={turn.id} turn={turn} />
              ))}
            </ul>
            <PresetQuestions
              label="ASK NEXT"
              onSelect={submit}
              questions={followUps}
              variant="follow-up"
            />
          </>
        )}
      </div>

      <form
        className="assistant-composer"
        onSubmit={(event) => {
          event.preventDefault();
          submit(draft);
        }}
      >
        <input
          aria-label="Ask the VTMS Assistant a question"
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask about VTMS…"
          ref={inputRef}
          type="text"
          value={draft}
        />
        <button className="button primary" disabled={draft.trim().length === 0} type="submit">
          Ask
        </button>
      </form>

      <p className="assistant-disclosure">{ASSISTANT_DISCLOSURE}</p>
    </section>
  );
}
