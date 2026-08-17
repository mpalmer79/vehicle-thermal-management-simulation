"use client";

import Link from "next/link";

import type { AnswerCategory, ComposedAnswer } from "@/lib/assistant-compose";
import type { RelatedRoute } from "@/lib/assistant-knowledge";

import type { AssistantTurn } from "./assistant-context";

/** Categories worth badging. Project answers are the default and need no chip. */
const CATEGORY_TONE: Partial<Record<AnswerCategory, string>> = {
  Physics: "physics",
  Scenario: "scenario",
  Validation: "validation",
  Verification: "validation",
  Architecture: "architecture",
  Creator: "creator",
  "Digital twin": "validation",
  Numerics: "physics",
  Run: "run",
};

function CategoryChip({ category }: { category: AnswerCategory }) {
  const tone = CATEGORY_TONE[category];
  if (!tone) return null;
  return <span className={`assistant-category ${tone}`}>{category.toUpperCase()}</span>;
}

function Routes({ routes }: { routes: RelatedRoute[] }) {
  if (routes.length === 0) return null;
  return (
    <div className="assistant-routes">
      {routes.map((route) =>
        route.external ? (
          <a className="assistant-route" href={route.href} key={route.href} rel="noreferrer noopener" target="_blank">
            {route.label} <span aria-hidden="true">↗</span>
          </a>
        ) : (
          <Link className="assistant-route" href={route.href} key={route.href}>
            {route.label} <span aria-hidden="true">→</span>
          </Link>
        ),
      )}
    </div>
  );
}

function Answer({ answer }: { answer: ComposedAnswer }) {
  return (
    <article className="assistant-answer">
      <header className="assistant-answer-head">
        <h3>{answer.heading}</h3>
        <CategoryChip category={answer.category} />
      </header>

      <p>{answer.lead}</p>

      {answer.figures.length > 0 && (
        <dl className="assistant-figures">
          {answer.figures.map((figure) => (
            <div key={figure.label}>
              <dt>{figure.label}</dt>
              <dd>{figure.value}</dd>
              {figure.note && <small>{figure.note}</small>}
            </div>
          ))}
        </dl>
      )}

      {answer.facts.length > 0 && (
        <ul className="assistant-facts">
          {answer.facts.map((fact) => (
            <li key={fact}>{fact}</li>
          ))}
        </ul>
      )}

      {answer.sections.map((section) => (
        <section className="assistant-subsection" key={section.title}>
          <strong>{section.title}</strong>
          {section.body && <p>{section.body}</p>}
          {section.facts.length > 0 && (
            <ul className="assistant-facts">
              {section.facts.map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>
          )}
        </section>
      ))}

      {answer.notes.map((note) => (
        <p className="assistant-note" key={note}>
          {note}
        </p>
      ))}

      <Routes routes={answer.routes} />
    </article>
  );
}

/**
 * One conversational turn.
 *
 * User turns are compact bubbles. Assistant turns are lighter structured surfaces: a
 * heading with a category indicator, the direct answer, optional authoritative figures,
 * key facts, supporting blocks when the composer synthesized across topics, provenance
 * notes, and the routes worth exploring.
 */
export function AssistantMessage({
  turn,
  onSelect,
}: {
  turn: AssistantTurn;
  onSelect: (question: string) => void;
}) {
  if (turn.role === "user") {
    return (
      <li className="assistant-turn user">
        <p className="assistant-bubble">{turn.text}</p>
      </li>
    );
  }

  const { response } = turn;

  if (response.kind === "answer") {
    return (
      <li className="assistant-turn agent">
        <Answer answer={response} />
      </li>
    );
  }

  if (response.kind === "clarify") {
    return (
      <li className="assistant-turn agent">
        <article className="assistant-answer clarify">
          <header className="assistant-answer-head">
            <h3>One more thing</h3>
            <span className="assistant-category clarify">CLARIFY</span>
          </header>
          <p>{response.question}</p>
          <div className="assistant-choices">
            {response.options.map((option) => (
              <button key={option.label} onClick={() => onSelect(option.query)} type="button">
                {option.label}
              </button>
            ))}
          </div>
        </article>
      </li>
    );
  }

  return (
    <li className="assistant-turn agent">
      <article className="assistant-answer unmatched">
        <span className="assistant-answer-flag">No knowledge-base match</span>
        <p>{response.answer}</p>
      </article>
    </li>
  );
}
