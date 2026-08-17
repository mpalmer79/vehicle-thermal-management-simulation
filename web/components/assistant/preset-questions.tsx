"use client";

import type { PromptGlyph, StarterPrompt } from "@/lib/assistant-prompts";

/** Small distinct mark per starter, so the five do not read as one repeated row. */
function PromptGlyphMark({ glyph }: { glyph: PromptGlyph }) {
  return (
    <svg className={`prompt-glyph ${glyph}`} viewBox="0 0 20 20" role="presentation" aria-hidden="true">
      {glyph === "model" && (
        <g>
          <rect className="pgm-line" x="3" y="4" width="14" height="3" rx="1.5" />
          <rect className="pgm-line" x="3" y="9" width="10" height="3" rx="1.5" />
          <rect className="pgm-line" x="3" y="14" width="6" height="3" rx="1.5" />
        </g>
      )}
      {glyph === "loop" && (
        <g>
          <path className="pgm-stroke" d="M5,13 L5,8 Q5,5 8,5 L12,5 Q15,5 15,8 L15,13" />
          <circle className="pgm-dot" cx="5" cy="15" r="2" />
          <circle className="pgm-dot" cx="15" cy="15" r="2" />
        </g>
      )}
      {glyph === "fault" && (
        <g>
          <path className="pgm-stroke" d="M10,3 L17,16 L3,16 Z" />
          <line className="pgm-bar" x1="10" x2="10" y1="8" y2="11.5" />
          <circle className="pgm-dot" cx="10" cy="13.6" r="1" />
        </g>
      )}
      {glyph === "evidence" && (
        <g>
          <line className="pgm-axis" x1="4" x2="4" y1="3" y2="16" />
          <line className="pgm-axis" x1="4" x2="17" y1="16" y2="16" />
          <path className="pgm-stroke" d="M4,14 C8,13 10,7 13,5.5 S16,4.6 17,4.4" />
        </g>
      )}
      {glyph === "twin" && (
        <g>
          <circle className="pgm-stroke" cx="7" cy="10" r="4.6" />
          <circle className="pgm-dash" cx="13" cy="10" r="4.6" />
        </g>
      )}
      {glyph === "scenario" && (
        <g>
          <rect className="pgm-stroke" x="3" y="4" width="6" height="5" rx="1.5" />
          <rect className="pgm-stroke" x="11" y="4" width="6" height="5" rx="1.5" />
          <rect className="pgm-stroke" x="3" y="11" width="6" height="5" rx="1.5" />
          <rect className="pgm-dash" x="11" y="11" width="6" height="5" rx="1.5" />
        </g>
      )}
      {glyph === "creator" && (
        <g>
          <circle className="pgm-stroke" cx="10" cy="7" r="3.2" />
          <path className="pgm-stroke" d="M4,16.5 Q10,11.5 16,16.5" />
        </g>
      )}
      {glyph === "system" && (
        <g>
          <circle className="pgm-stroke" cx="10" cy="10" r="3" />
          <line className="pgm-bar" x1="10" x2="10" y1="2.5" y2="5.5" />
          <line className="pgm-bar" x1="10" x2="10" y1="14.5" y2="17.5" />
          <line className="pgm-bar" x1="2.5" x2="5.5" y1="10" y2="10" />
          <line className="pgm-bar" x1="14.5" x2="17.5" y1="10" y2="10" />
        </g>
      )}
    </svg>
  );
}

/** Starter prompts: glyph plus a short label, submitting the fuller query. */
export function PresetQuestions({
  prompts,
  onSelect,
  label,
}: {
  prompts: StarterPrompt[];
  onSelect: (question: string) => void;
  label: string;
}) {
  if (prompts.length === 0) return null;

  return (
    <div className="assistant-prompts preset">
      <span className="eyebrow">{label}</span>
      <ul>
        {prompts.map((prompt, index) => (
          <li key={prompt.id} style={{ animationDelay: `${index * 40}ms` }}>
            <button onClick={() => onSelect(prompt.query)} type="button">
              <PromptGlyphMark glyph={prompt.glyph} />
              <span>{prompt.label}</span>
              <i aria-hidden="true">→</i>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Contextual follow-ups under an answer. Plain text, lighter treatment. */
export function FollowUpQuestions({
  questions,
  onSelect,
}: {
  questions: string[];
  onSelect: (question: string) => void;
}) {
  if (questions.length === 0) return null;

  return (
    <div className="assistant-prompts follow-up">
      <span className="eyebrow">ASK NEXT</span>
      <ul>
        {questions.map((question, index) => (
          <li key={question} style={{ animationDelay: `${index * 40}ms` }}>
            <button onClick={() => onSelect(question)} type="button">
              <span>{question}</span>
              <i aria-hidden="true">→</i>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
