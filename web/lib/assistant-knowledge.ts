/**
 * VTMS Knowledge Assistant — curated knowledge base.
 *
 * Every answer served by the assistant originates here. The content is written from
 * material that already exists in this repository (README, ARCHITECTURE, the VTMS-V1
 * engineering model surfaces, the validation governance docs, and the canonical
 * scenario definitions in `lib/scenarios.ts`).
 *
 * Rules for editing this file:
 *
 * 1. Never claim OEM calibration, vehicle-specific validation, completed controlled
 *    validation, digital-twin status, measured telemetry, or damage/boiling limits.
 *    VTMS-V1 is a generic, uncalibrated, numerically verified model.
 * 2. Never state a number that is not already reported in the repository.
 * 3. If a subject is not covered here, the assistant must fall back rather than guess.
 *
 * No network call of any kind is made to produce an answer.
 */

export type TopicCategory =
  | "Project"
  | "Physics"
  | "Numerics"
  | "Scenarios"
  | "Verification"
  | "Validation"
  | "Digital twin"
  | "Creator"
  | "Architecture";

export type RelatedRoute = {
  label: string;
  href: string;
  external?: boolean;
};

export type KnowledgeTopic = {
  /** Stable identifier. Referenced by tests and by follow-up context. */
  id: string;
  /** Rendered as the answer heading. */
  title: string;
  category: TopicCategory;
  /** Primary match terms. Multi-word entries are matched as phrases. */
  keywords: string[];
  /** Weaker match terms: alternate phrasings, informal wording, related vocabulary. */
  synonyms: string[];
  /** One or two sentences. This is the answer. */
  shortAnswer: string;
  /** Two to four compact supporting facts. */
  detail: string[];
  /** "Explore this" destinations. */
  relatedRoutes: RelatedRoute[];
  /** Topics that stay plausible when the visitor asks a short follow-up. */
  relatedTopics?: string[];
  /** Offered under the answer as tappable follow-ups. */
  followUpQuestions: string[];
};

const GITHUB_REPO = "https://github.com/mpalmer79/vehicle-thermal-management-simulation";

export const CREATOR_LINKS = {
  name: "Michael Palmer",
  linkedin: "https://www.linkedin.com/in/mpalmer1234",
  github: "https://github.com/mpalmer79",
  repository: GITHUB_REPO,
} as const;

/* Starter prompts live in `assistant-prompts.ts`, next to the route-aware ones. */

export const FALLBACK_ANSWER =
  "I don't have a reliable VTMS knowledge-base answer for that yet. Try asking about the thermal model, scenarios, validation, system architecture, or the project creator.";

/** Offered alongside the fallback so a visitor always has a way forward. */
export const FALLBACK_SUGGESTIONS = [
  "What is VTMS and what does it simulate?",
  "How does the radiator reject heat?",
  "How has VTMS been verified and validated?",
  "Who built VTMS?",
] as const;

export const ASSISTANT_DISCLOSURE =
  "Uses the VTMS knowledge base bundled with this site. No external AI service is contacted.";

export const knowledgeTopics: KnowledgeTopic[] = [
  /* ---------------------------------------------------------------- Project */
  {
    id: "what-is-vtms",
    title: "What VTMS is",
    category: "Project",
    keywords: ["what is vtms", "what does vtms simulate", "what vtms does", "vtms overview", "about vtms"],
    synonyms: ["what is this project", "what is this site", "what is this app", "explain vtms"],
    shortAnswer:
      "VTMS is a physics-based vehicle thermal-management simulation platform. It computes how engine and coolant temperatures evolve over time for a given operating condition, then visualizes the result as playback.",
    detail: [
      "The governing model is VTMS-V1, using the EM-V1 equation set.",
      "Two transient states are integrated: engine-structure temperature and bulk coolant temperature.",
      "Nine canonical scenarios (S-01 through S-09) cover baseline, fault, and degradation conditions.",
      "All physics runs in a Python engine behind FastAPI. The browser only visualizes returned results.",
    ],
    relatedRoutes: [
      { label: "Open the Simulation Lab", href: "/simulate" },
      { label: "Explore the thermal system", href: "/system" },
    ],
    relatedTopics: ["vtms-v1", "model-classification", "intended-purpose", "architecture"],
    followUpQuestions: [
      "What is VTMS-V1?",
      "Is VTMS calibrated to a specific vehicle?",
      "How does VTMS model engine and coolant temperature?",
    ],
  },
  {
    id: "vtms-v1",
    title: "VTMS-V1 and EM-V1",
    category: "Project",
    keywords: ["vtms v1", "em v1", "model id", "model identifier", "equation set", "model version"],
    synonyms: ["v1 model", "which model", "model name", "frozen model", "model spec", "specification"],
    shortAnswer:
      "VTMS-V1 is the frozen model configuration; EM-V1 is the governing equation set it implements. Both identifiers are attached to every simulation result so a run can be traced back to the physics that produced it.",
    detail: [
      "VTMS-V1 is a two-state lumped-parameter model, deliberately constrained in scope.",
      "The equations, solver settings, and canonical scenario inputs are frozen.",
      "The formal contract is the VTMS-V1 Engineering Model Specification 1.0.0.",
      "Vehicle-specific calibrated parameter sets are a VTMS-V2 target, not part of V1.",
    ],
    relatedRoutes: [{ label: "Review the model boundary", href: "/model" }],
    relatedTopics: ["what-is-vtms", "model-classification", "model-exclusions", "two-state-model"],
    followUpQuestions: [
      "What does VTMS-V1 intentionally exclude?",
      "Is VTMS calibrated to a specific vehicle?",
      "How is the model solved numerically?",
    ],
  },
  {
    id: "model-classification",
    title: "Current model classification",
    category: "Project",
    keywords: [
      "generic parameter set",
      "uncalibrated",
      "calibrated",
      "specific vehicle",
      "model classification",
      "model status",
      "model maturity",
    ],
    synonyms: ["real vehicle", "specific car", "oem model", "which vehicle", "generic model"],
    shortAnswer:
      "VTMS-V1 is a generic, physics-based, numerically verified model running on a generic parameter set. It is not calibrated to any specific vehicle and it is not an OEM model.",
    detail: [
      "Numerical verification is complete. Controlled physical validation is not.",
      "The parameter set is generic, so results are representative behavior rather than vehicle-specific prediction.",
      "One external plausibility comparison against independent KIT OBD-II telemetry has been run, with no parameter tuning.",
      "This status is stated on the interface rather than hidden.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["validation-status", "digital-twin", "kit-plausibility", "vtms-v1"],
    followUpQuestions: [
      "Is VTMS a digital twin?",
      "What is the KIT plausibility comparison?",
      "What would controlled validation require?",
    ],
  },
  {
    id: "intended-purpose",
    title: "Why the project exists",
    category: "Project",
    keywords: [
      "why does vtms exist",
      "why does the project exist",
      "project exist",
      "purpose of vtms",
      "intended purpose",
      "goal of the project",
      "what is vtms for",
      "project purpose",
    ],
    synonyms: ["motivation", "why build this", "what problem", "point of the project", "reason for vtms"],
    shortAnswer:
      "VTMS exists to make vehicle thermal behavior easier to explore, visualize, and test, while keeping the engineering claims honest — the model, the verification evidence, and the validation status are kept visibly separate.",
    detail: [
      "It explores where automotive systems, scientific computing, validation practice, and software engineering meet.",
      "Calculated quantities must come from governing equations, sourced properties, or explicitly identified assumptions.",
      "A stated design goal is exposing the engineering model in a browser without moving thermal calculations into it.",
      "A second goal is comparing predictions against independent telemetry without tuning the model first.",
    ],
    relatedRoutes: [
      { label: "Read the maturity roadmap", href: "/roadmap" },
      { label: "Meet the creator", href: "/about" },
    ],
    relatedTopics: ["what-is-vtms", "creator", "why-vtms-was-built", "validation-status"],
    followUpQuestions: ["Who built VTMS?", "What is on the roadmap?", "How has VTMS been verified and validated?"],
  },

  /* ---------------------------------------------------------------- Physics */
  {
    id: "two-state-model",
    title: "Engine and coolant temperature",
    category: "Physics",
    keywords: [
      "engine and coolant temperature",
      "two state",
      "two transient state",
      "thermal state",
      "how does vtms model temperature",
      "state equation",
    ],
    synonyms: ["governing equation", "how temperature is modelled", "core balance", "lumped parameter", "heat balance"],
    shortAnswer:
      "VTMS-V1 integrates two transient temperatures: effective engine-structure temperature and bulk engine-side coolant temperature. Radiator outlet temperature is derived algebraically rather than integrated as a third state.",
    detail: [
      "Engine structure: C_e dT_e/dt = Q_engine - Q_ec - Q_ea.",
      "Coolant: C_c dT_c/dt = Q_ec - Q_rad.",
      "Q_ec = UA_ec (T_e - T_c) moves heat from engine metal into coolant.",
      "Q_ea = UA_ea (T_e - T_a) is direct engine loss to ambient.",
    ],
    relatedRoutes: [
      { label: "Review the engineering model", href: "/model" },
      { label: "Explore the thermal system", href: "/system" },
    ],
    relatedTopics: ["engine-thermal-state", "coolant-thermal-state", "engine-to-coolant", "energy-balance"],
    followUpQuestions: [
      "How does the radiator reject heat?",
      "What does the thermostat do?",
      "How is the model solved numerically?",
    ],
  },
  {
    id: "engine-thermal-state",
    title: "Engine thermal state",
    category: "Physics",
    keywords: [
      "engine thermal state",
      "engine structure",
      "engine thermal mass",
      "engine temperature",
      "engine block temperature",
      "q engine",
    ],
    synonyms: ["engine metal", "engine heat", "combustion heat", "engine thermal storage", "engine node"],
    shortAnswer:
      "The engine is represented as one effective thermal mass. It receives combustion-derived wall heat and rejects energy to the coolant and directly to ambient.",
    detail: [
      "C_e dT_e/dt = Q_engine - Q_ec - Q_ea.",
      "Q_engine is the combustion-derived heat input for the selected speed and load.",
      "The model is lumped: there are no local cylinder-head hot spots and no spatial temperature field.",
    ],
    relatedRoutes: [{ label: "Inspect the engine node", href: "/system" }],
    relatedTopics: ["two-state-model", "engine-to-coolant", "coolant-thermal-state", "model-exclusions"],
    followUpQuestions: [
      "How does heat move from the engine to the coolant?",
      "What does VTMS-V1 intentionally exclude?",
      "What is the coolant thermal state?",
    ],
  },
  {
    id: "coolant-thermal-state",
    title: "Coolant thermal state",
    category: "Physics",
    keywords: [
      "coolant thermal state",
      "bulk coolant",
      "coolant temperature",
      "coolant loop",
      "coolant node",
      "coolant storage",
    ],
    synonyms: ["coolant heat", "coolant loop temperature", "coolant state", "engine side coolant"],
    shortAnswer:
      "Bulk engine-side coolant is the second transient state. It gains the heat handed over by the engine and loses heat through the radiator model.",
    detail: [
      "C_c dT_c/dt = Q_ec - Q_rad.",
      "The coolant is treated as one well-mixed bulk volume, not a distributed hydraulic network.",
      "Thermostat position decides how much of that coolant reaches the radiator versus the bypass branch.",
    ],
    relatedRoutes: [{ label: "Inspect the coolant loop", href: "/system" }],
    relatedTopics: ["two-state-model", "thermostat", "bypass-flow", "radiator-heat-rejection"],
    followUpQuestions: ["What does the thermostat do?", "What is the bypass branch for?", "How does the pump behave?"],
  },
  {
    id: "engine-to-coolant",
    title: "Engine-to-coolant heat transfer",
    category: "Physics",
    keywords: [
      "engine to coolant",
      "engine to the coolant",
      "heat move",
      "q ec",
      "ua ec",
      "heat transfer to coolant",
      "engine coolant heat transfer",
    ],
    synonyms: ["heat into coolant", "metal to coolant", "how heat reaches the coolant", "coolant pickup"],
    shortAnswer:
      "Heat moves from engine structure into coolant through a conductance term: Q_ec = UA_ec (T_e - T_c). The larger the temperature gap, the more heat is handed over.",
    detail: [
      "UA_ec is an effective engine-to-coolant conductance in the generic V1 parameter set.",
      "The same term appears as a loss in the engine balance and a gain in the coolant balance.",
      "This coupling is what makes the two states track each other during warm-up.",
    ],
    relatedRoutes: [{ label: "Review the engineering model", href: "/model" }],
    relatedTopics: ["two-state-model", "engine-thermal-state", "coolant-thermal-state", "energy-balance"],
    followUpQuestions: ["How is energy conservation checked?", "How does the radiator reject heat?", "What is VTMS-V1?"],
  },
  {
    id: "radiator-heat-rejection",
    title: "Radiator heat rejection",
    category: "Physics",
    keywords: ["radiator", "heat rejection", "q rad", "radiator outlet", "radiator model"],
    synonyms: ["how heat leaves", "cooling core", "heat exchanger", "reject heat to air", "radiator work"],
    shortAnswer:
      "The radiator is where heat leaves the coolant loop for the air stream. VTMS-V1 models it as a single-pass crossflow heat exchanger with both streams unmixed, using an effectiveness-NTU formulation.",
    detail: [
      "Radiator outlet temperature is solved algebraically instead of being carried as a third state.",
      "Rejection depends on coolant flow, air mass flow, and the coolant-to-ambient temperature difference.",
      "Air side combines ram airflow from vehicle speed with electric-fan volume flow.",
      "Radiator degradation is modelled as reduced UA — scenario S-08.",
    ],
    relatedRoutes: [
      { label: "Explore the thermal system", href: "/system" },
      { label: "Compare radiator scenarios", href: "/scenarios" },
    ],
    relatedTopics: ["epsilon-ntu", "ram-airflow", "cooling-fan", "degradation-scenarios"],
    followUpQuestions: [
      "What is the epsilon-NTU formulation?",
      "How does airflow reach the radiator?",
      "What happens if the radiator degrades?",
    ],
  },
  {
    id: "epsilon-ntu",
    title: "Effectiveness-NTU radiator formulation",
    category: "Physics",
    keywords: ["epsilon ntu", "effectiveness ntu", "ntu", "crossflow", "effectiveness correlation"],
    synonyms: ["ntu method", "heat exchanger effectiveness", "unmixed streams", "exchanger correlation"],
    shortAnswer:
      "Effectiveness-NTU expresses how much of the theoretically available heat transfer a heat exchanger actually achieves. VTMS-V1 uses the single-pass crossflow, both-streams-unmixed correlation.",
    detail: [
      "Effectiveness is the ratio of actual heat transfer to the maximum thermodynamically possible transfer.",
      "NTU is set by the radiator UA and the smaller of the two stream heat-capacity rates.",
      "This keeps the radiator algebraic, which is why V1 has two states rather than three.",
    ],
    relatedRoutes: [{ label: "Review the engineering model", href: "/model" }],
    relatedTopics: ["radiator-heat-rejection", "two-state-model", "solver"],
    followUpQuestions: ["How does the radiator reject heat?", "How is the model solved numerically?", "What is VTMS-V1?"],
  },
  {
    id: "thermostat",
    title: "Thermostat behaviour",
    category: "Physics",
    keywords: ["thermostat", "thermostat opening", "coolant routing", "thermostat fraction"],
    synonyms: ["valve", "opening temperature", "warm up control", "coolant valve", "routing control"],
    shortAnswer:
      "The thermostat is a temperature-driven deterministic split. It decides what fraction of coolant flow is routed through the radiator and what fraction stays on the bypass branch.",
    detail: [
      "During warm-up the radiator branch is largely shut, so the engine reaches operating temperature faster.",
      "As coolant temperature rises, the radiator fraction increases and heat rejection ramps up.",
      "Stuck-open and stuck-closed are explicit fault modes, not emergent behaviour.",
      "Stuck closed is scenario S-06.",
    ],
    relatedRoutes: [
      { label: "Explore the thermal system", href: "/system" },
      { label: "Run the stuck-closed scenario", href: "/scenarios" },
    ],
    relatedTopics: ["bypass-flow", "coolant-thermal-state", "fault-scenarios", "radiator-heat-rejection"],
    followUpQuestions: [
      "What is the bypass branch for?",
      "What happens if the thermostat sticks closed?",
      "How does the radiator reject heat?",
    ],
  },
  {
    id: "bypass-flow",
    title: "Bypass branch",
    category: "Physics",
    keywords: ["bypass", "bypass flow", "bypass branch", "bypass loop"],
    synonyms: ["short circuit loop", "coolant shortcut", "recirculation path", "non radiator path"],
    shortAnswer:
      "The bypass is the path coolant takes when it is not routed through the radiator. It keeps coolant circulating through the engine while the thermostat is holding the radiator branch shut.",
    detail: [
      "Bypass and radiator fractions are complementary: what does not go to the radiator returns via the bypass.",
      "Heavy bypass flow means little heat rejection, which is the mechanism behind warm-up and behind S-06.",
      "The bypass branch is drawn as its own path in the system schematic.",
    ],
    relatedRoutes: [{ label: "Explore the thermal system", href: "/system" }],
    relatedTopics: ["thermostat", "coolant-pump", "coolant-thermal-state", "fault-scenarios"],
    followUpQuestions: ["What does the thermostat do?", "How does the pump behave?", "What is scenario S-06?"],
  },
  {
    id: "coolant-pump",
    title: "Coolant pump",
    category: "Physics",
    keywords: ["pump", "coolant pump", "coolant flow rate", "pump flow", "circulation"],
    synonyms: ["water pump", "flow rate", "coolant circulation", "pump speed", "pump health"],
    shortAnswer:
      "Pump flow follows engine speed and pump health. It sets how quickly coolant carries heat from the engine to the radiator, so it affects the temperature difference around the loop rather than the total heat generated.",
    detail: [
      "Flow scales with engine speed, so idle scenarios circulate less coolant than highway scenarios.",
      "A pump-health factor lets the model represent reduced circulation deterministically.",
      "Pump degradation is scenario S-07.",
    ],
    relatedRoutes: [
      { label: "Explore the thermal system", href: "/system" },
      { label: "Run the pump degradation scenario", href: "/scenarios" },
    ],
    relatedTopics: ["bypass-flow", "radiator-heat-rejection", "degradation-scenarios"],
    followUpQuestions: [
      "What happens when the pump degrades?",
      "How does the radiator reject heat?",
      "What is the bypass branch for?",
    ],
  },
  {
    id: "cooling-fan",
    title: "Cooling fan",
    category: "Physics",
    keywords: ["fan", "cooling fan", "electric fan", "fan airflow", "forced airflow"],
    synonyms: ["fan on", "fan command", "fan volume flow", "fan failure", "forced convection"],
    shortAnswer:
      "The electric fan supplies forced airflow through the radiator when coolant temperature calls for it. It matters most at low vehicle speed, where there is little ram air to rely on.",
    detail: [
      "Total radiator airflow combines a calibrated ram-air contribution with electric-fan volume flow.",
      "Fan command is deterministic and temperature-driven, not stochastic.",
      "Scenario S-03 is fan-assisted hot-ambient idle; S-05 removes the fan entirely.",
    ],
    relatedRoutes: [
      { label: "Compare the fan scenarios", href: "/scenarios" },
      { label: "Explore the thermal system", href: "/system" },
    ],
    relatedTopics: ["ram-airflow", "radiator-heat-rejection", "fault-scenarios"],
    followUpQuestions: [
      "What happens during fan failure?",
      "How does ram airflow work?",
      "How does the radiator reject heat?",
    ],
  },
  {
    id: "ram-airflow",
    title: "Ram airflow and the air side",
    category: "Physics",
    keywords: ["airflow", "ram air", "air side", "air mass flow", "vehicle speed airflow"],
    synonyms: ["air flow", "wind", "air through the radiator", "moving air", "air stream"],
    shortAnswer:
      "Ram airflow is the air pushed through the radiator by vehicle motion. It is combined with fan airflow to give the total air-side flow the radiator model uses.",
    detail: [
      "At highway speed ram air dominates and the fan contributes comparatively little — that is scenario S-02.",
      "At idle there is no ram contribution, so the fan carries the air side — scenario S-03.",
      "The ram-air contribution is a calibrated term in the generic V1 parameter set, not a CFD result.",
      "Restricted air-side heat rejection is scenario S-09.",
    ],
    relatedRoutes: [
      { label: "Compare airflow scenarios", href: "/scenarios" },
      { label: "Explore the thermal system", href: "/system" },
    ],
    relatedTopics: ["cooling-fan", "radiator-heat-rejection", "degradation-scenarios", "ambient-temperature"],
    followUpQuestions: [
      "What does the cooling fan do?",
      "What happens if airflow is restricted?",
      "How does ambient temperature affect results?",
    ],
  },
  {
    id: "ambient-temperature",
    title: "Ambient temperature",
    category: "Physics",
    keywords: ["ambient", "ambient temperature", "outside air temperature", "ambient sink"],
    synonyms: ["air temperature", "outside temperature", "hot day", "cold day", "environment temperature"],
    shortAnswer:
      "Ambient temperature is the sink the whole system rejects heat into. It sets both the direct engine-to-ambient loss and the air-side inlet temperature at the radiator.",
    detail: [
      "Q_ea = UA_ea (T_e - T_a) is the direct engine loss to ambient.",
      "A hotter ambient reduces the temperature difference available at the radiator, so rejection falls.",
      "The canonical scenarios span 20 °C, 25 °C, 35 °C, and 40 °C ambient conditions.",
    ],
    relatedRoutes: [
      { label: "Set an ambient condition", href: "/simulate" },
      { label: "Compare canonical scenarios", href: "/scenarios" },
    ],
    relatedTopics: ["radiator-heat-rejection", "canonical-scenarios", "engine-thermal-state"],
    followUpQuestions: [
      "What are the canonical scenarios?",
      "How does the radiator reject heat?",
      "Can I run a custom condition?",
    ],
  },
  {
    id: "energy-balance",
    title: "Energy balance",
    category: "Physics",
    keywords: ["energy balance", "energy conservation", "conserve energy", "energy check"],
    synonyms: ["is energy conserved", "conservation check", "energy accounting", "first law"],
    shortAnswer:
      "Energy conservation is verified numerically rather than assumed. Every run accounts for heat generated, stored in the two thermal masses, and rejected to ambient, and the residual is checked.",
    detail: [
      "Energy-conservation verification is part of the automated test suite and is reported as passing.",
      "It is a numerical check on the implementation, not a physical validation of the parameter values.",
      "Result surfaces report the energy-balance status for the run being viewed.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["verification", "automated-tests", "two-state-model", "verification-and-validation"],
    followUpQuestions: [
      "What does verification cover?",
      "How is VTMS verified and validated?",
      "How is the model solved numerically?",
    ],
  },
  {
    id: "model-exclusions",
    title: "What VTMS-V1 excludes",
    category: "Physics",
    keywords: [
      "excluded",
      "not modelled",
      "out of scope",
      "system boundary",
      "limitation",
      "boiling",
      "oil temperature",
      "heater core",
    ],
    synonyms: ["what is missing", "does not model", "not included", "model limits", "pressure", "cfd"],
    shortAnswer:
      "V1 is deliberately constrained. Oil thermal behaviour, heater-core extraction, A/C condenser coupling, pressure and boiling physics, detailed hydraulic networks, local cylinder-head hot spots, CFD, and OEM-specific calibration are all outside the model boundary.",
    detail: [
      "Because boiling and pressure are not modelled, VTMS does not predict boil-over or any damage threshold.",
      "Because the model is lumped, it does not produce a spatial temperature map of the engine.",
      "Keeping the boundary narrow is what makes the two-state model verifiable.",
    ],
    relatedRoutes: [{ label: "Review the model boundary", href: "/model" }],
    relatedTopics: ["vtms-v1", "model-classification", "two-state-model", "digital-twin"],
    followUpQuestions: [
      "Is VTMS a digital twin?",
      "Is VTMS calibrated to a specific vehicle?",
      "What is the current validation status?",
    ],
  },

  /* --------------------------------------------------------------- Numerics */
  {
    id: "solver",
    title: "Numerical solution",
    category: "Numerics",
    keywords: ["solver", "rk45", "solve ivp", "scipy", "integration", "numerics", "integrator", "numerically", "solved numerically"],
    synonyms: ["how is it solved", "numerical method", "runge kutta", "time stepping", "ode solver"],
    shortAnswer:
      "The two state equations are integrated with SciPy's solve_ivp using the adaptive RK45 method, with frozen tolerances and one-second output sampling.",
    detail: [
      "Two coupled ordinary differential equations are integrated; radiator outlet stays algebraic.",
      "Solver tolerances and settings are frozen as part of the VTMS-V1 configuration.",
      "Solver convergence and numerical energy conservation are both checked by automated tests.",
      "Integration runs in Python on the server. Nothing is integrated in the browser.",
    ],
    relatedRoutes: [{ label: "Review the engineering model", href: "/model" }],
    relatedTopics: ["two-state-model", "energy-balance", "verification", "architecture"],
    followUpQuestions: [
      "How is energy conservation checked?",
      "What does verification cover?",
      "How is the application architected?",
    ],
  },

  /* -------------------------------------------------------------- Scenarios */
  {
    id: "canonical-scenarios",
    title: "Canonical scenarios S-01 to S-09",
    category: "Scenarios",
    keywords: ["canonical scenario", "s01", "s02", "s03", "s04", "scenario library", "nine scenario", "list of scenario"],
    synonyms: ["what scenario", "which scenario", "test case", "scenario suite", "preset condition", "baseline scenario"],
    shortAnswer:
      "Nine frozen canonical scenarios cover the model's tested operating range: four baselines, two faults, and three degradations.",
    detail: [
      "S-01 Cold Start / Fast Idle, S-02 Warm Highway, S-03 Hot Ambient Idle, S-04 Sustained Higher Load.",
      "S-05 Fan Failure and S-06 Thermostat Stuck Closed are the fault cases.",
      "S-07 Pump Degradation, S-08 Radiator Degradation, and S-09 Airflow Degradation are the degradation cases.",
      "Canonical inputs are frozen and protected at the API boundary, so an edited run is relabelled as CUSTOM.",
    ],
    relatedRoutes: [
      { label: "Browse the scenario library", href: "/scenarios" },
      { label: "Run one in the Simulation Lab", href: "/simulate" },
    ],
    relatedTopics: ["fault-scenarios", "degradation-scenarios", "custom-runs", "ambient-temperature"],
    followUpQuestions: [
      "What happens in the built-in fault scenarios?",
      "What do the degradation scenarios show?",
      "Can I run a custom condition?",
    ],
  },
  {
    id: "fault-scenarios",
    title: "Built-in fault scenarios",
    category: "Scenarios",
    keywords: [
      "fault scenario",
      "built in fault",
      "fan failure",
      "thermostat stuck closed",
      "s05",
      "s06",
      "failure mode",
    ],
    synonyms: ["what goes wrong", "broken fan", "stuck thermostat", "fault mode", "failure case", "what if it fails"],
    shortAnswer:
      "Two explicit fault scenarios are built in. S-05 removes forced airflow by failing the fan, and S-06 holds the thermostat closed so the radiator branch is blocked. Both start from the S-03 hot-ambient idle condition.",
    detail: [
      "S-05 Fan Failure: at idle there is no ram air, so losing the fan removes most of the air-side heat rejection.",
      "S-06 Thermostat Stuck Closed: coolant stays on the bypass branch and the radiator is effectively cut out of the loop.",
      "Both run at 40 °C ambient, 1000 rpm, 25 % load, for 1200 seconds.",
      "The model reports the resulting temperature trajectory. It does not predict damage, boiling, or a failure threshold — those are outside the V1 boundary.",
    ],
    relatedRoutes: [
      { label: "Browse the scenario library", href: "/scenarios" },
      { label: "Run a fault case", href: "/simulate" },
    ],
    relatedTopics: ["degradation-scenarios", "canonical-scenarios", "thermostat", "cooling-fan"],
    followUpQuestions: [
      "What do the degradation scenarios show?",
      "What does the thermostat do?",
      "What does VTMS-V1 exclude?",
    ],
  },
  {
    id: "degradation-scenarios",
    title: "Degradation scenarios",
    category: "Scenarios",
    keywords: [
      "degradation scenario",
      "pump degradation",
      "radiator degradation",
      "airflow degradation",
      "s07",
      "s08",
      "s09",
      "degraded",
    ],
    synonyms: ["wear", "reduced performance", "partial failure", "worn component", "reduced capacity"],
    shortAnswer:
      "Three degradation scenarios reduce a component's capability rather than removing it. S-07 reduces pump performance, S-08 reduces radiator UA, and S-09 restricts air-side heat rejection.",
    detail: [
      "All three are based on S-04 Sustained Higher Load: 35 °C ambient, 3000 rpm, 55 % load, 54 km/h, 1200 seconds.",
      "S-07 reduces coolant circulation, so heat is carried to the radiator more slowly.",
      "S-08 reduces radiator UA, which lowers effectiveness for the same flows.",
      "S-09 restricts airflow reaching the core, which lowers the air-side capacity rate.",
    ],
    relatedRoutes: [
      { label: "Browse the scenario library", href: "/scenarios" },
      { label: "Run a degradation case", href: "/simulate" },
    ],
    relatedTopics: ["fault-scenarios", "canonical-scenarios", "coolant-pump", "radiator-heat-rejection"],
    followUpQuestions: [
      "What happens in the built-in fault scenarios?",
      "How does the coolant pump behave?",
      "How does the radiator reject heat?",
    ],
  },
  {
    id: "custom-runs",
    title: "Custom runs and canonical protection",
    category: "Scenarios",
    keywords: [
      "custom run",
      "custom scenario",
      "custom condition",
      "my own condition",
      "canonical protection",
      "run my own",
    ],
    synonyms: ["change the inputs", "edit inputs", "own values", "custom simulation", "simulate custom"],
    shortAnswer:
      "You can run your own operating condition in the Simulation Lab. If you edit the physical inputs of a canonical scenario, the run is relabelled CUSTOM — a frozen S-01 to S-09 identity cannot be kept with altered inputs.",
    detail: [
      "Canonical scenario identities are protected on the server, not just in the browser.",
      "The Lab submits human-facing inputs such as km/h and load percent; the API converts them at the boundary.",
      "Completed runs are held in browser session storage and rendered from /results.",
    ],
    relatedRoutes: [{ label: "Open the Simulation Lab", href: "/simulate" }],
    relatedTopics: ["canonical-scenarios", "backend-api", "architecture"],
    followUpQuestions: [
      "What are the canonical scenarios?",
      "How is the application architected?",
      "What API endpoints exist?",
    ],
  },

  /* ----------------------------------------------------------- Verification */
  {
    id: "verification",
    title: "Numerical verification",
    category: "Verification",
    keywords: ["verification", "verified", "numerical verification", "verification check"],
    synonyms: ["is it correct", "does it solve correctly", "implementation check", "solver check"],
    shortAnswer:
      "Verification answers a software and mathematics question: does the implementation solve the frozen VTMS-V1 equations consistently? For VTMS-V1 that work is complete.",
    detail: [
      "Coverage includes energy conservation, solver convergence, component invariants, and fault direction.",
      "Canonical regression checks guard S-01 through S-09 against unintended change.",
      "21 engineering verification checks are reported as passing.",
      "Verification says nothing about whether the generic parameters match a real vehicle — that is validation.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["automated-tests", "verification-and-validation", "energy-balance", "validation-status"],
    followUpQuestions: [
      "How is verification different from validation?",
      "What do the automated tests cover?",
      "What is the current validation status?",
    ],
  },
  {
    id: "automated-tests",
    title: "Automated test suite",
    category: "Verification",
    keywords: [
      "automated test",
      "test suite",
      "test cover",
      "how many test",
      "regression test",
      "ci",
      "continuous integration",
    ],
    synonyms: ["testing", "pytest", "unit test", "test coverage", "github actions", "pipeline"],
    shortAnswer:
      "The repository runs an automated Python/API suite of 47 tests, plus 21 engineering verification checks, on every change.",
    detail: [
      "Coverage spans the engine, validation toolkit, controlled-validation governance, acceptance evaluator, calibration harness, and the API boundary.",
      "Canonical regression tests protect the frozen scenario behaviour.",
      "CI also runs a production dependency audit, ESLint, TypeScript, a Next.js production build, and API/web container smoke tests.",
      "The Python suite is executed on Python 3.11, 3.12, and 3.13.",
    ],
    relatedRoutes: [
      { label: "See the evidence ladder", href: "/validation" },
      { label: "Open the repository", href: GITHUB_REPO, external: true },
    ],
    relatedTopics: ["verification", "energy-balance", "verification-and-validation"],
    followUpQuestions: ["What does verification cover?", "How is energy conservation checked?", "Is VTMS validated?"],
  },

  /* ------------------------------------------------------------- Validation */
  {
    id: "verification-and-validation",
    title: "Verification and validation",
    category: "Validation",
    keywords: [
      "verified and validated",
      "verification and validation",
      "how has vtms been verified",
      "verification versus validation",
      "how is vtms validated",
    ],
    synonyms: ["evidence", "evidence ladder", "how do you know it works", "proof", "credibility", "trust the model"],
    shortAnswer:
      "The two are kept deliberately separate. Numerical verification is complete: the implementation solves the frozen equations consistently. Controlled physical validation is not complete — it is pending data acquisition.",
    detail: [
      "Stage 1, numerical verification: complete (energy conservation, convergence, component and regression checks).",
      "Stage 2, external plausibility: complete, using an independent KIT OBD-II warm-up trace with no parameter tuning.",
      "Stage 3, controlled calibration: active, awaiting qualified Argonne D3 data.",
      "Stage 4, blind holdout validation: future, and only after calibration is frozen.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["verification", "kit-plausibility", "argonne", "validation-status"],
    followUpQuestions: [
      "What is the KIT plausibility comparison?",
      "What is the Argonne controlled validation plan?",
      "Why is VTMS not physically validated yet?",
    ],
  },
  {
    id: "kit-plausibility",
    title: "KIT external plausibility comparison",
    category: "Validation",
    keywords: ["kit", "plausibility", "obd", "obd ii", "real world comparison", "measured versus predicted"],
    synonyms: ["real data", "external data", "road data", "telemetry comparison", "first comparison", "seat leon"],
    shortAnswer:
      "The first external comparison used an independent KIT Seat Leon OBD-II warm-up trace, with no VTMS parameters changed. VTMS reached a similar final operating-temperature region but warmed up substantially too quickly.",
    detail: [
      "Reported metrics: RMSE 21.40 °C, MAE 16.50 °C, mean bias +16.13 °C, final error -0.79 °C after 1020 s.",
      "60 °C arrival was about 276 s early and 80 °C arrival about 496 s early.",
      "The mismatch is preserved as evidence rather than tuned away.",
      "This is external plausibility evidence only. It is not controlled physical validation.",
    ],
    relatedRoutes: [{ label: "See the comparison charts", href: "/validation" }],
    relatedTopics: ["verification-and-validation", "argonne", "validation-status", "model-classification"],
    followUpQuestions: [
      "What is the Argonne controlled validation plan?",
      "Why is VTMS not physically validated yet?",
      "Is VTMS calibrated to a specific vehicle?",
    ],
  },
  {
    id: "argonne",
    title: "Argonne D3 controlled validation",
    category: "Validation",
    keywords: ["argonne", "d3", "controlled validation", "dynamometer", "controlled data"],
    synonyms: ["lab data", "national laboratory", "controlled experiment", "formal validation", "dyno"],
    shortAnswer:
      "Formal V1 validation is designed around controlled Argonne National Laboratory D3 dynamometer data. The governance is in place, but the data and official signal mapping are still pending — no Argonne results exist yet.",
    detail: [
      "The workflow is Acquire → Hash → Map → Calibrate → Freeze → Holdout → Report; it currently sits at stage 1 of 7.",
      "Every controlled run must carry an immutable manifest with dataset ID, raw-file SHA-256, validation role, and parameter-snapshot hash.",
      "A physical_evidence flag defaults to false, so synthetic traces cannot be relabelled as formal validation.",
      "VTMS-V1 stays frozen while the requested controlled data is pending.",
    ],
    relatedRoutes: [{ label: "See the controlled validation status", href: "/validation" }],
    relatedTopics: ["calibration-vs-holdout", "verification-and-validation", "validation-status", "kit-plausibility"],
    followUpQuestions: [
      "How are calibration and holdout kept separate?",
      "Why is VTMS not physically validated yet?",
      "What is the KIT plausibility comparison?",
    ],
  },
  {
    id: "calibration-vs-holdout",
    title: "Calibration versus holdout",
    category: "Validation",
    keywords: ["calibration", "holdout", "blind holdout", "calibration and holdout", "preregistered", "tuning"],
    synonyms: ["fitting", "fit parameters", "parameter tuning", "train test split", "separation"],
    shortAnswer:
      "Calibration and holdout datasets are reserved before any fitting begins. Only preregistered uncertain parameters may be fitted, and the holdout experiments stay untouched until calibration is frozen.",
    detail: [
      "Datasets carry an explicit validation role, so a calibration set cannot later be presented as validation evidence.",
      "Raw-file hashes and parameter-snapshot hashes lock what was used and what state the model was in.",
      "A synthetic bounded-calibration harness has already exercised calibrate → freeze → untouched holdout as a non-physical dry run.",
      "Passing a synthetic dry run is not physical validation and is not presented as such.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["argonne", "verification-and-validation", "validation-status"],
    followUpQuestions: [
      "What is the Argonne controlled validation plan?",
      "What is the current validation status?",
      "How is verification different from validation?",
    ],
  },
  {
    id: "validation-status",
    title: "Current validation status",
    category: "Validation",
    keywords: [
      "validation status",
      "physically validated",
      "is vtms validated",
      "why is vtms not validated",
      "validated against real",
    ],
    synonyms: ["accurate", "how accurate", "can i trust", "proven", "real world accuracy", "reliable"],
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. Controlled physical validation has not been performed, so predictions should be read as representative generic behaviour rather than vehicle-specific accuracy.",
    detail: [
      "The only real-world comparison so far is the KIT plausibility test, which showed warm-up that is substantially too fast.",
      "Controlled Argonne D3 validation is pending data acquisition and signal mapping.",
      "The parameter set is generic, so there is no vehicle-specific accuracy claim to make.",
      "This status is displayed in the application rather than hidden.",
    ],
    relatedRoutes: [{ label: "See the evidence ladder", href: "/validation" }],
    relatedTopics: ["verification-and-validation", "kit-plausibility", "argonne", "digital-twin"],
    followUpQuestions: [
      "Is VTMS a digital twin?",
      "What is the KIT plausibility comparison?",
      "What is the Argonne controlled validation plan?",
    ],
  },

  /* ------------------------------------------------------------ Digital twin */
  {
    id: "digital-twin",
    title: "VTMS-V1 is not a digital twin",
    category: "Digital twin",
    keywords: ["digital twin", "twin", "is vtms a digital twin"],
    synonyms: ["live vehicle", "real time vehicle", "synchronized vehicle", "connected vehicle", "mirror a vehicle"],
    shortAnswer:
      "No. VTMS-V1 is not a digital twin. It is a generic, uncalibrated, physics-based simulation with no connection to any physical vehicle and no live telemetry.",
    detail: [
      "A digital twin would require synchronized vehicle telemetry, state estimation, and vehicle-specific calibration. None of those exist here.",
      "VTMS has no live data feed. Every result comes from solving the frozen V1 equations for inputs you supply.",
      "The parameter set is generic, so the model does not represent one particular car.",
      "A connected, synchronized model is listed as a future maturity target, not a current capability.",
    ],
    relatedRoutes: [
      { label: "See the maturity roadmap", href: "/roadmap" },
      { label: "See the evidence ladder", href: "/validation" },
    ],
    relatedTopics: ["maturity-path", "model-classification", "validation-status"],
    followUpQuestions: [
      "What would it take to become a digital twin?",
      "Is VTMS calibrated to a specific vehicle?",
      "What is the current validation status?",
    ],
  },
  {
    id: "maturity-path",
    title: "Maturity path beyond V1",
    category: "Digital twin",
    keywords: ["roadmap", "maturity path", "vtms v2", "future work", "next version", "what would it take"],
    synonyms: ["what is next", "future plan", "upcoming", "later version", "evolution"],
    shortAnswer:
      "The stated path runs from V1 through V2 toward a connected model. Each step adds evidence or capability that V1 deliberately does not claim.",
    detail: [
      "VTMS-V1: finish Argonne D3 calibration and blind holdout validation, then publish formal controlled results.",
      "VTMS-V2: vehicle-specific calibrated parameter sets, direct OBD-II/CAN replay, and justified model extensions based on residual analysis.",
      "Connected model: synchronized physical-vehicle telemetry, state estimation, and continuous calibration.",
      "Only after those steps would digital-twin language be appropriate.",
    ],
    relatedRoutes: [{ label: "See the maturity roadmap", href: "/roadmap" }],
    relatedTopics: ["digital-twin", "argonne", "validation-status"],
    followUpQuestions: [
      "Is VTMS a digital twin?",
      "What is the Argonne controlled validation plan?",
      "What is the current validation status?",
    ],
  },

  /* ---------------------------------------------------------------- Creator */
  {
    id: "creator",
    title: "Michael Palmer",
    category: "Creator",
    keywords: [
      "who built vtms",
      "who is michael palmer",
      "michael palmer",
      "creator",
      "author",
      "who made this",
      "who wrote this",
    ],
    synonyms: ["developer", "owner", "behind the project", "who is he", "about the creator", "portfolio"],
    shortAnswer:
      "VTMS was created by Michael Palmer. He has more than 25 years of experience in automotive retail and dealership operations — sales, finance, management, dealer technology, implementation and training, and AI deployment — and is pursuing Computer Science through Southern New Hampshire University.",
    detail: [
      "The portfolio focus is software, AI, automation, and applied technical systems.",
      "VTMS sits at the intersection of automotive domain knowledge, software engineering, and numerical computation.",
      "He is not presented as a mechanical, OEM, or licensed professional engineer — VTMS is an applied engineering-computation project.",
    ],
    relatedRoutes: [
      { label: "Learn more about the creator", href: "/about" },
      { label: "GitHub profile", href: CREATOR_LINKS.github, external: true },
      { label: "LinkedIn profile", href: CREATOR_LINKS.linkedin, external: true },
    ],
    relatedTopics: ["why-vtms-was-built", "creator-links", "intended-purpose"],
    followUpQuestions: ["Why was VTMS created?", "Where can I find the code?", "Why does the project exist?"],
  },
  {
    id: "why-vtms-was-built",
    title: "Why VTMS was built",
    category: "Creator",
    keywords: ["why was vtms created", "why did he build", "why build vtms", "motivation for vtms"],
    synonyms: ["origin story", "how it started", "inspiration", "reason it was built"],
    shortAnswer:
      "VTMS grew from an interest in combining automotive domain experience with software engineering and physics-based computation — making vehicle thermal behaviour easier to explore, visualize, test, and eventually compare against controlled physical data.",
    detail: [
      "The automotive background supplies the domain questions; the software and computation side supplies the tooling.",
      "The project deliberately keeps engineering claims conservative: verification and validation are reported separately.",
      "VTMS-V1 is a generic physics-based simulation, not an OEM-calibrated model or a synchronized digital twin.",
    ],
    relatedRoutes: [{ label: "Learn more about the creator", href: "/about" }],
    relatedTopics: ["creator", "intended-purpose", "model-classification"],
    followUpQuestions: ["Who is Michael Palmer?", "Why does the project exist?", "Is VTMS a digital twin?"],
  },
  {
    id: "creator-links",
    title: "Where to find the project and the creator",
    category: "Creator",
    keywords: ["linkedin", "github", "profile link", "source code", "repository", "contact", "connect"],
    synonyms: ["where is the code", "find the code", "social", "find him", "open source", "repo", "link"],
    shortAnswer:
      "The source code and both profile links are public.",
    detail: [
      `LinkedIn: ${CREATOR_LINKS.linkedin}`,
      `GitHub: ${CREATOR_LINKS.github}`,
      `Project repository: ${GITHUB_REPO}`,
    ],
    relatedRoutes: [
      { label: "Learn more about the creator", href: "/about" },
      { label: "GitHub profile", href: CREATOR_LINKS.github, external: true },
      { label: "LinkedIn profile", href: CREATOR_LINKS.linkedin, external: true },
    ],
    relatedTopics: ["creator", "why-vtms-was-built", "architecture"],
    followUpQuestions: ["Who is Michael Palmer?", "How is the application architected?", "Why was VTMS created?"],
  },

  /* ----------------------------------------------------------- Architecture */
  {
    id: "architecture",
    title: "System architecture",
    category: "Architecture",
    keywords: ["architecture", "architected", "tech stack", "how is it built", "system design", "stack"],
    synonyms: ["technology", "built with", "how does it work technically", "components", "software design"],
    shortAnswer:
      "A Next.js frontend talks to a FastAPI boundary, which invokes the authoritative Python simulation engine. The browser never calculates VTMS thermal physics.",
    detail: [
      "Next.js and React handle presentation, playback, and the engineering visuals — all hand-written SVG and CSS.",
      "FastAPI validates the public request, translates it into the Python Scenario contract, and returns the serialized SimulationResult.",
      "The Python engine (NumPy/SciPy) is the single source of truth for every computed value.",
      "Computed runs are stored only in browser session storage; no database is required.",
    ],
    relatedRoutes: [
      { label: "Open the Simulation Lab", href: "/simulate" },
      { label: "Open the repository", href: GITHUB_REPO, external: true },
    ],
    relatedTopics: ["frontend", "backend-api", "deployment", "solver"],
    followUpQuestions: [
      "What API endpoints exist?",
      "Does the browser calculate physics?",
      "How is VTMS deployed?",
    ],
  },
  {
    id: "frontend",
    title: "Frontend boundary",
    category: "Architecture",
    keywords: ["frontend", "next js", "react", "browser calculate", "does the browser compute"],
    synonyms: ["web app", "client side", "ui", "user interface", "javascript"],
    shortAnswer:
      "The frontend is a Next.js/React application whose job is visualization only. It does not compute thermal physics — it renders the authoritative result returned by the API.",
    detail: [
      "Every diagram, chart, gauge, and animation is hand-written SVG and CSS; there is no charting or UI framework dependency.",
      "Configuration previews reflect what you entered, not a predicted temperature.",
      "Result summaries are deterministic readouts of returned arrays, never inferred diagnosis.",
      "All motion is disabled under prefers-reduced-motion.",
    ],
    relatedRoutes: [{ label: "Explore the thermal system", href: "/system" }],
    relatedTopics: ["architecture", "backend-api", "assistant-itself"],
    followUpQuestions: ["How is the application architected?", "What API endpoints exist?", "What is this assistant?"],
  },
  {
    id: "backend-api",
    title: "FastAPI simulation boundary",
    category: "Architecture",
    keywords: ["api", "fastapi", "endpoint", "backend", "api contract", "python engine"],
    synonyms: ["server", "rest", "http api", "service", "simulation service"],
    shortAnswer:
      "FastAPI is the boundary between the browser and the Python engine. It validates and translates public requests, runs the simulation, and returns the authoritative result.",
    detail: [
      "Endpoints: GET /health, GET /api/v1/model, GET /api/v1/scenarios, POST /api/v1/simulations.",
      "Human-facing units such as km/h and load percent are converted once at the server boundary.",
      "Canonical scenario identities are enforced server-side, so altered inputs cannot keep a frozen S-01 to S-09 identity.",
      "Responses carry runtime metadata and explicit no-store caching.",
    ],
    relatedRoutes: [{ label: "Open the Simulation Lab", href: "/simulate" }],
    relatedTopics: ["architecture", "custom-runs", "deployment"],
    followUpQuestions: ["How is the application architected?", "Can I run a custom condition?", "How is VTMS deployed?"],
  },
  {
    id: "deployment",
    title: "Deployment",
    category: "Architecture",
    keywords: ["deployment", "railway", "hosting", "deployed", "production"],
    synonyms: ["where is it hosted", "live site", "docker", "container", "infrastructure"],
    shortAnswer:
      "The web application and the API are deployed as two separate non-root containers on Railway, each with its own health check.",
    detail: [
      "Next.js uses standalone output for self-hosted production deployment.",
      "The web container exposes /api/health; the API container exposes /health.",
      "CI builds and boots both production images and smoke-tests those health endpoints.",
      "The browser-visible API URL is configuration, not a secret.",
    ],
    relatedRoutes: [{ label: "Open the repository", href: GITHUB_REPO, external: true }],
    relatedTopics: ["architecture", "backend-api", "automated-tests"],
    followUpQuestions: ["How is the application architected?", "What API endpoints exist?", "What do the tests cover?"],
  },
  {
    id: "assistant-itself",
    title: "About this assistant",
    category: "Architecture",
    keywords: [
      "this assistant",
      "are you an ai",
      "what are you",
      "how do you work",
      "chatgpt",
      "gpt",
      "claude",
      "llm",
      "language model",
    ],
    synonyms: ["are you a bot", "who are you", "chatbot", "do you use ai", "are you real"],
    shortAnswer:
      "I answer from a curated VTMS knowledge base that ships with this site. No external AI service is contacted, no hosted language model is running, and I have no internet access and no vehicle telemetry.",
    detail: [
      "Your question is normalized, tokenized, and scored against knowledge-base topics — deterministic matching, not generation.",
      "If nothing scores high enough, I say so instead of inventing an answer.",
      "Every fact I give comes from documentation already in this repository.",
    ],
    relatedRoutes: [{ label: "Open the full assistant", href: "/assistant" }],
    relatedTopics: ["architecture", "frontend", "what-is-vtms"],
    followUpQuestions: ["What is VTMS and what does it simulate?", "How is the application architected?", "Who built VTMS?"],
  },
];

export const topicById = (id: string): KnowledgeTopic | undefined =>
  knowledgeTopics.find((topic) => topic.id === id);
