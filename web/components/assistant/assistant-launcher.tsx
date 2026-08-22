"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

import { useAssistant } from "./assistant-context";
import { AssistantPanel } from "./assistant-panel";

/**
 * Floating assistant entry point.
 *
 * Desktop: a launcher pinned to the lower-right that opens a contained side panel.
 * Mobile: the same launcher sits above the bottom navigation and opens a full-width
 * sheet that stops short of it, so the primary navigation is never obstructed.
 *
 * Hidden on /assistant, where the dedicated route already renders the conversation.
 */
export function AssistantLauncher() {
  const pathname = usePathname();
  const { panelOpen, setPanelOpen } = useAssistant();
  const onDedicatedRoute = pathname.startsWith("/assistant");

  useEffect(() => {
    if (!panelOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setPanelOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [panelOpen, setPanelOpen]);

  // Leaving for the dedicated route should not leave an orphaned panel behind.
  useEffect(() => {
    if (onDedicatedRoute) setPanelOpen(false);
  }, [onDedicatedRoute, setPanelOpen]);

  if (onDedicatedRoute) return null;

  return (
    <>
      <button
        aria-expanded={panelOpen}
        aria-label={panelOpen ? "Close the VTMS Assistant" : "Ask the VTMS AI Assistant"}
        className={panelOpen ? "assistant-launcher open" : "assistant-launcher"}
        onClick={() => setPanelOpen(!panelOpen)}
        type="button"
      >
        <span className="assistant-launcher-glyph" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation">
            <path
              d="M5.4 4.8h13.2a2.2 2.2 0 0 1 2.2 2.2v7.7a2.2 2.2 0 0 1-2.2 2.2h-6.1l-4.1 2.7v-2.7h-3a2.2 2.2 0 0 1-2.2-2.2V7a2.2 2.2 0 0 1 2.2-2.2Z"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.45"
              strokeLinejoin="round"
              opacity="0.72"
            />
            <text
              x="11.8"
              y="11.2"
              fill="currentColor"
              fontSize="6.1"
              fontWeight="900"
              textAnchor="middle"
              dominantBaseline="middle"
            >
              AI
            </text>
            <path
              d="M17.8 6.9v2.1M16.75 7.95h2.1"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.35"
              strokeLinecap="round"
            />
          </svg>
        </span>
        <span className="assistant-launcher-label">Ask VTMS</span>
      </button>

      {panelOpen && (
        <>
          <button
            aria-label="Close assistant"
            className="assistant-scrim"
            onClick={() => setPanelOpen(false)}
            tabIndex={-1}
            type="button"
          />
          <div className="assistant-sheet" role="dialog" aria-label="VTMS Knowledge Assistant" aria-modal="false">
            <AssistantPanel autoFocus onClose={() => setPanelOpen(false)} variant="panel" />
          </div>
        </>
      )}
    </>
  );
}
