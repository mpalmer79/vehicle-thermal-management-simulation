"use client";

import { usePathname } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

import { ASSISTANT_DISCLOSURE } from "@/lib/assistant-knowledge";
import { quickQuestionsForRoute } from "@/lib/assistant-prompts";

import { useAssistant } from "./assistant-context";
import { AssistantMessage } from "./assistant-message";
import { FollowUpQuestions, PresetQuestions } from "./preset-questions";

/**
 * The conversational surface itself.
 *
 * `panel` renders inside the floating launcher sheet; `page` renders the /assistant
 * route. Both share one transcript through the assistant context, so a visitor can open
 * a question in the panel and continue it on the dedicated route.
 *
 * The starter prompts are route-aware: on a product route the assistant offers three
 * questions about that page, while /assistant keeps the five global starters.
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
  const pathname = usePathname();
  const { turns, followUps, ask, reset } = useAssistant();
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const transcriptRef = useRef<HTMLDivElement | null>(null);

  const starters = useMemo(() => quickQuestionsForRoute(pathname), [pathname]);

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
              {starters.routeSpecific
                ? "Questions about this page, or ask anything about the model, scenarios, evidence, or architecture."
                : "Ask about the thermal model, scenarios, evidence, architecture, or the creator."}
            </p>
            <PresetQuestions label={starters.label} onSelect={submit} prompts={starters.prompts} />
          </div>
        ) : (
          <>
            <ul aria-live="polite" className="assistant-turns" role="log">
              {turns.map((turn) => (
                <AssistantMessage key={turn.id} onSelect={submit} turn={turn} />
              ))}
            </ul>
            <FollowUpQuestions onSelect={submit} questions={followUps} />
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
