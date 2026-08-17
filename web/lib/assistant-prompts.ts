/**
 * Starter prompts for the VTMS Knowledge Assistant.
 *
 * Two kinds:
 *
 * - `PRESET_QUESTIONS` — the five global starters. Each carries a short visible
 *   `label` for the button and a fuller `query` that is what actually gets submitted,
 *   so the mobile sheet stays readable without weakening retrieval.
 * - `quickQuestionsForRoute` — route-aware suggestions. The assistant already knows the
 *   current pathname locally; using it to offer relevant questions costs nothing and
 *   needs no network.
 */

export type PromptGlyph =
  | "model"
  | "loop"
  | "fault"
  | "evidence"
  | "twin"
  | "scenario"
  | "creator"
  | "system";

export type StarterPrompt = {
  id: string;
  /** Short text shown on the control. */
  label: string;
  /** The question actually submitted to the assistant. */
  query: string;
  glyph: PromptGlyph;
};

export const PRESET_QUESTIONS: StarterPrompt[] = [
  {
    id: "what-is-vtms",
    label: "What is VTMS?",
    query: "What is VTMS and what does it simulate?",
    glyph: "model",
  },
  {
    id: "cooling-system",
    label: "How does the cooling system work?",
    query: "How does VTMS model engine and coolant temperature?",
    glyph: "loop",
  },
  {
    id: "cooling-fails",
    label: "What happens when cooling fails?",
    query: "What happens in the built-in fault scenarios?",
    glyph: "fault",
  },
  {
    id: "trustworthy",
    label: "How trustworthy are the results?",
    query: "How has VTMS been verified and validated?",
    glyph: "evidence",
  },
  {
    id: "digital-twin",
    label: "Is VTMS a digital twin?",
    query: "Is VTMS a digital twin?",
    glyph: "twin",
  },
];

/** Route-specific starters, keyed by the first path segment. */
const ROUTE_PROMPTS: Record<string, StarterPrompt[]> = {
  "/system": [
    { id: "sys-rad", label: "How does the radiator reject heat?", query: "How does the radiator reject heat?", glyph: "loop" },
    { id: "sys-thermo", label: "What does the thermostat do?", query: "What does the thermostat do?", glyph: "system" },
    { id: "sys-air", label: "How do fan and ram airflow work?", query: "How do fan and ram airflow work together?", glyph: "system" },
  ],
  "/scenarios": [
    { id: "scn-compare", label: "Compare S-05 and S-06.", query: "Compare S-05 and S-06.", glyph: "scenario" },
    { id: "scn-degrade", label: "Which scenarios model degradation?", query: "Which scenarios are degradations?", glyph: "scenario" },
    { id: "scn-hottest", label: "Which canonical scenario finishes hottest?", query: "Which canonical scenario finishes hottest?", glyph: "fault" },
  ],
  "/validation": [
    { id: "val-kit", label: "What did the KIT comparison show?", query: "What is the KIT plausibility comparison?", glyph: "evidence" },
    { id: "val-pending", label: "Why is controlled validation still pending?", query: "What is the Argonne controlled validation plan?", glyph: "evidence" },
    { id: "val-holdout", label: "How are calibration and holdout separated?", query: "How are calibration and holdout kept separate?", glyph: "evidence" },
  ],
  "/about": [
    { id: "abt-who", label: "Who built VTMS?", query: "Who built VTMS?", glyph: "creator" },
    { id: "abt-why", label: "Why was VTMS created?", query: "Why was VTMS created?", glyph: "creator" },
    { id: "abt-links", label: "Where can I find Michael's work?", query: "Where can I find the code?", glyph: "creator" },
  ],
  "/simulate": [
    { id: "sim-custom", label: "Can I run a custom condition?", query: "Can I run a custom condition?", glyph: "system" },
    { id: "sim-scenarios", label: "What are the canonical scenarios?", query: "What are the canonical scenarios?", glyph: "scenario" },
    { id: "sim-arch", label: "Where does the physics actually run?", query: "Does the browser calculate physics?", glyph: "model" },
  ],
  "/model": [
    { id: "mdl-states", label: "How are the two states solved?", query: "How is the model solved numerically?", glyph: "model" },
    { id: "mdl-ntu", label: "What is the epsilon-NTU formulation?", query: "What is the epsilon-NTU formulation?", glyph: "loop" },
    { id: "mdl-exclude", label: "What does VTMS-V1 exclude?", query: "What does VTMS-V1 intentionally exclude?", glyph: "system" },
  ],
  "/results": [
    { id: "res-final", label: "What is the final coolant temperature?", query: "What is the final coolant temperature?", glyph: "loop" },
    { id: "res-energy", label: "Did energy balance pass?", query: "Did energy balance pass?", glyph: "evidence" },
    { id: "res-scenario", label: "What scenario is this?", query: "What scenario is this?", glyph: "scenario" },
  ],
};

/**
 * Starters for a pathname.
 *
 * `/assistant` keeps the global five, so the dedicated route always presents the same
 * front door. Every other known route contributes its own three.
 */
export function quickQuestionsForRoute(pathname: string): {
  prompts: StarterPrompt[];
  label: string;
  routeSpecific: boolean;
} {
  const segment = `/${pathname.split("/").filter(Boolean)[0] ?? ""}`;
  const routePrompts = pathname.startsWith("/assistant") ? undefined : ROUTE_PROMPTS[segment];

  if (routePrompts) return { prompts: routePrompts, label: "ASK ABOUT THIS PAGE", routeSpecific: true };
  return { prompts: PRESET_QUESTIONS, label: "START HERE", routeSpecific: false };
}
