"use client";

import Link from "next/link";

import { type AssistantTurn } from "./assistant-context";

/**
 * One conversational turn.
 *
 * User turns are compact bubbles. Assistant turns are lighter structured surfaces: a
 * short heading, a concise answer, a few key facts, and the routes worth exploring.
 */
export function AssistantMessage({ turn }: { turn: AssistantTurn }) {
  if (turn.role === "user") {
    return (
      <li className="assistant-turn user">
        <p className="assistant-bubble">{turn.text}</p>
      </li>
    );
  }

  return (
    <li className="assistant-turn agent">
      <article className={turn.heading ? "assistant-answer" : "assistant-answer unmatched"}>
        {turn.heading ? (
          <h3>{turn.heading}</h3>
        ) : (
          <span className="assistant-answer-flag">No knowledge-base match</span>
        )}

        <p>{turn.text}</p>

        {turn.facts.length > 0 && (
          <ul className="assistant-facts">
            {turn.facts.map((fact) => (
              <li key={fact}>{fact}</li>
            ))}
          </ul>
        )}

        {turn.routes.length > 0 && (
          <div className="assistant-routes">
            {turn.routes.map((route) =>
              route.external ? (
                <a
                  className="assistant-route"
                  href={route.href}
                  key={route.href}
                  rel="noreferrer noopener"
                  target="_blank"
                >
                  {route.label} <span aria-hidden="true">↗</span>
                </a>
              ) : (
                <Link className="assistant-route" href={route.href} key={route.href}>
                  {route.label} <span aria-hidden="true">→</span>
                </Link>
              ),
            )}
          </div>
        )}
      </article>
    </li>
  );
}
