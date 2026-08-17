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
        aria-label={panelOpen ? "Close the VTMS Assistant" : "Ask the VTMS Assistant"}
        className={panelOpen ? "assistant-launcher open" : "assistant-launcher"}
        onClick={() => setPanelOpen(!panelOpen)}
        type="button"
      >
        <span className="assistant-launcher-glyph" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation">
            <circle className="al-ring" cx="12" cy="12" r="9" />
            <path className="al-loop" d="M6.6,15 Q12,19.6 17.4,15" />
            <circle className="al-core" cx="12" cy="9.8" r="3.2" />
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
