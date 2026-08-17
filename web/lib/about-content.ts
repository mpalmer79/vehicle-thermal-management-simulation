/**
 * Content for the /about route.
 *
 * Positioning is deliberately conservative: Michael Palmer is described through his
 * automotive retail, dealer technology, and software/AI work, and through the Computer
 * Science studies in progress. No engineering credential is claimed anywhere, because
 * none is claimed anywhere else in this repository.
 */

import { CREATOR_LINKS } from "./assistant-knowledge";

export { CREATOR_LINKS };

export type ProfileLink = {
  id: "linkedin" | "github";
  label: string;
  handle: string;
  href: string;
};

export const PROFILE_LINKS: ProfileLink[] = [
  { id: "linkedin", label: "LinkedIn", handle: "in/mpalmer1234", href: CREATOR_LINKS.linkedin },
  { id: "github", label: "GitHub", handle: "mpalmer79", href: CREATOR_LINKS.github },
];

export type ExperienceStage = {
  id: "automotive" | "dealer-tech" | "software-ai" | "vtms";
  eyebrow: string;
  metric: string;
  title: string;
  detail: string;
};

/** Rendered as a connected progression, not four paragraphs. */
export const EXPERIENCE_PATH: ExperienceStage[] = [
  {
    id: "automotive",
    eyebrow: "AUTOMOTIVE DOMAIN",
    metric: "25+ years",
    title: "Retail and dealership operations",
    detail: "Sales, finance, management, and day-to-day dealership operations.",
  },
  {
    id: "dealer-tech",
    eyebrow: "DEALER TECHNOLOGY",
    metric: "Systems",
    title: "Implementation and training",
    detail: "DMS and workflow platforms, rollout, and hands-on user training.",
  },
  {
    id: "software-ai",
    eyebrow: "SOFTWARE + AI",
    metric: "In progress",
    title: "Computer Science and applied AI",
    detail: "Software development, automation, and AI deployment. CS through SNHU.",
  },
  {
    id: "vtms",
    eyebrow: "VTMS",
    metric: "VTMS-V1",
    title: "Physics-based thermal simulation",
    detail: "A frozen two-state model, a verified Python engine, and a visual product layer.",
  },
];

export type BuildCategory = {
  id: "automotive-technology" | "software-ai" | "engineering-simulation";
  title: string;
  copy: string;
  points: string[];
};

export const WHAT_I_BUILD: BuildCategory[] = [
  {
    id: "automotive-technology",
    title: "Automotive Technology",
    copy: "Tools shaped by how dealerships and vehicle systems actually work.",
    points: ["Dealer workflow", "Implementation", "Training"],
  },
  {
    id: "software-ai",
    title: "Software & AI",
    copy: "Applications, automation, and AI-assisted development.",
    points: ["Full-stack web", "Automation", "AI deployment"],
  },
  {
    id: "engineering-simulation",
    title: "Engineering Simulation",
    copy: "Numerical models with verification and honest evidence reporting.",
    points: ["Physics models", "Numerical solvers", "Validation governance"],
  },
];

export const WHY_VTMS =
  "VTMS grew from an interest in combining automotive domain experience with software engineering and physics-based computation. The project is designed to make vehicle thermal behavior easier to explore, visualize, test, and eventually compare against controlled physical data.";

/** Shown prominently. This claim boundary is non-negotiable. */
export const CREDIBILITY_NOTE =
  "VTMS-V1 is currently a generic physics-based simulation and is not an OEM-calibrated vehicle model or synchronized digital twin.";

export const INTERSECTION = [
  "Automotive domain knowledge",
  "Software engineering",
  "Numerical computation",
  "Engineering curiosity",
  "AI-assisted development",
];
