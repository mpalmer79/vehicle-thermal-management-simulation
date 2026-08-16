# VTMS UI-5 Visual Productization Specification

## Purpose

UI-5 moves VTMS from a technically functional engineering application into a visually persuasive, portfolio-grade product experience.

The current application proves that the Python physics engine, FastAPI boundary, playback, scenario library, validation evidence, and Railway deployment work. The UI still relies too heavily on text, repeated cards, chips, and empty space. UI-5 must make the system understandable through visual explanation, media, data visualization, motion, and interactive engineering graphics rather than through more prose.

This is a presentation-layer redesign only. VTMS-V1 governing physics, canonical scenarios, API contracts, validation evidence, model status, numerical verification, and engineering provenance must not be altered or overstated.

## Core product goal

A new visitor should understand the product in less than 30 seconds without reading several paragraphs.

The interface should visually answer:

1. What is VTMS?
2. What physical system is being modeled?
3. What moves through the system?
4. What can the user change?
5. What does a simulation result mean?
6. What evidence supports the model?
7. What is still unvalidated or pending?

## Non-negotiable visual direction

- Keep the UI-4 off-white, warm ivory, and light-neutral foundation.
- Do not return to a black or near-black primary background.
- Keep dark navy or charcoal typography for legibility.
- Use teal, cyan, coral, amber, green, and selective purple as functional engineering colors.
- Use more illustration, diagrams, sparklines, charts, visual state indicators, and motion.
- Reduce long explanatory copy.
- Avoid large empty cards containing only a heading, one sentence, chips, and a link.
- Avoid turning every section into another rectangular card.
- Avoid decorative stock photography that does not explain the thermal system.
- Prefer purpose-built engineering visuals over generic vehicle photos.
- Keep the application credible as an engineering product, not a gaming dashboard or marketing template.

## Primary UX problem to solve

The current product has a repeated pattern:

```text
large card
  heading
  explanatory sentence
  several chips
  text link
```

That pattern is especially visible in the Scenario Library. It creates a text-heavy and visually repetitive experience.

UI-5 must replace repetition with visual hierarchy and visual storytelling.

## Design principle: show before explaining

Whenever a paragraph can be replaced by a diagram, thumbnail, mini chart, animated flow, state indicator, or compact data visualization, prefer the visual representation.

Supporting text should explain what the user cannot infer from the visual, not repeat it.

## Existing architecture to preserve

UI-5 should work with the current application rather than replacing it.

Important existing components include:

- `web/components/app-shell.tsx`
- `web/components/playback-workspace.tsx`
- `web/components/scenario-card.tsx`
- `web/components/signal-chart.tsx`
- `web/components/simulation-form.tsx`
- `web/components/status-pill.tsx`
- `web/components/stored-run-result.tsx`
- `web/components/thermal-loop.tsx`

Important existing routes include:

- `/`
- `/simulate`
- `/system`
- `/scenarios`
- `/validation`
- `/results/[runId]`
- `/model`
- `/roadmap`

Do not move thermal calculations into React. The browser continues to visualize authoritative results returned by the FastAPI/Python engine.

## UI-5 product hierarchy

The major pages should no longer feel like the same page with different text.

Each should have a distinct visual identity:

| Route | Primary visual role |
|---|---|
| Overview | Explain the system and invite exploration |
| Simulation Lab | Configure the operating condition visually |
| System Explorer | Explore the thermal circuit and live component state |
| Scenario Library | Browse scenario behavior through visual previews |
| Results | Understand the simulation outcome through playback and visual diagnostics |
| Validation | Understand the evidence ladder and measured-vs-predicted behavior |

## 1. Overview redesign

### Current problem

The Overview still opens with substantial text, status pills, a facts card, and additional explanatory cards. It communicates accurately but requires reading before the product becomes visually interesting.

### New hero composition

Use a split layout on desktop and a stacked composition on mobile.

Left side:

- product label
- concise headline
- one short supporting sentence
- primary CTA
- secondary CTA
- compact verification and validation state

Right side:

A large custom `ThermalSystemHero` visual that communicates the engine cooling loop at a glance.

### ThermalSystemHero

Create a reusable SVG or React/SVG engineering illustration containing:

- stylized engine block or engine thermal mass
- engine-side coolant loop
- thermostat junction
- bypass branch
- radiator
- cooling fan
- ambient/ram airflow
- directional coolant arrows
- directional air arrows
- compact values from the existing S-03 fixture when appropriate

Color language:

- coral/orange: engine heat
- cyan: coolant transport
- teal/green: radiator heat rejection
- amber: thermostat/control state
- muted purple: bypass branch
- blue/teal airflow arrows

The illustration should feel like a modern engineering infographic, not a literal photorealistic engine bay.

### Motion

Use restrained motion to show function:

- coolant-flow dots or short moving dash segments
- subtle fan rotation while active
- airflow particles or arrow movement
- very slow heat glow/pulse at the engine
- values easing when the selected playback time changes

Honor `prefers-reduced-motion` and provide a static state when motion is reduced.

### Copy reduction

The current hero paragraph should be reduced to approximately one concise sentence. Additional explanation can appear lower on the page or through component labels.

### Below the hero

Replace the current three text-heavy feature cards with a visual three-step product path:

```text
SIMULATE -> WATCH THE SYSTEM -> REVIEW THE EVIDENCE
```

Each step should include:

- a strong icon or compact illustration
- maximum one sentence
- direct CTA
- distinct visual treatment

Do not use three identical large white text cards.

## 2. Scenario Library redesign

### Current problem

`ScenarioCard` is currently mostly text, metadata chips, and links. Every scenario looks structurally identical, producing visual monotony.

### New ScenarioCardV2

Each card must include a visual preview area occupying roughly 35 to 45 percent of the card.

The preview can combine:

- scenario-specific mini thermal illustration
- tiny sparkline or thermal trend
- airflow/fan icon state
- fault/degradation visual overlay

Required visible information:

- scenario ID
- scenario name
- category
- one short behavior label
- 3 to 4 compact operating facts
- one primary action

The long `purpose` sentence should be shortened substantially or moved into an accessible detail expansion.

### Scenario-specific visual language

Examples:

S-01 Cold Start / Fast Idle
- cool blue engine/coolant at start
- rising temperature sparkline
- thermostat initially closed
- behavior label: `Warm-up transient`

S-02 Warm Highway
- strong directional ram-air arrows
- flatter steady temperature trace
- behavior label: `Ram-air dominated`

S-03 Hot Ambient Idle
- warm ambient field
- visible fan-assisted airflow
- behavior label: `Fan-assisted idle`

S-05 Fan Failure
- fan icon with clear failure treatment
- rising red temperature sparkline
- behavior label: `Loss of forced airflow`

S-06 Thermostat Stuck Closed
- closed thermostat gate visual
- blocked radiator path
- bypass emphasized

S-07 Pump Degradation
- reduced coolant-flow animation/symbol

S-08 Radiator Degradation
- radiator with reduced rejection indicator

S-09 Airflow Degradation
- weakened airflow arrows

### Layout

Desktop:
- visually rich 2 or 3 column grid depending viewport
- cards may vary slightly in height only when intentional

Mobile:
- full-width cards
- horizontal or top media preview
- no excessive blank vertical space

### CTA language

Replace weak text-only action emphasis with a clear button or button-link:

`Simulate this scenario`

For S-03 retain a secondary result preview action if useful.

## 3. System Explorer redesign

### Current problem

`ThermalLoop` is technically useful but still behaves like stacked component cards rather than a system-level visual model.

### New InteractiveThermalSchematic

Create a reusable system schematic based on the V1 model boundary.

Required nodes:

- engine structure
- coolant bulk state
- thermostat
- bypass
- radiator
- fan/airflow
- ambient sink

Required connections:

- engine heat to coolant
- thermostat split to radiator and bypass
- coolant return path
- radiator heat rejection to ambient
- fan/ram airflow through radiator

### Interactions

- Clicking/tapping a component selects it.
- Selected component receives a stronger outline and local detail panel.
- The detail panel shows current authoritative values from the selected time point.
- Optional compact equation or role summary can be shown, but avoid large explanatory paragraphs.
- Playback remains synchronized with the same fixture/result data source already used by `PlaybackWorkspace`.

### Flow magnitude

Use line thickness, opacity, dash speed, or particle density to indicate relative flow magnitude.

Do not fabricate exact physical geometry. This is a system schematic, not CFD or CAD.

## 4. Simulation Lab redesign

### Current problem

The Simulation Lab is functional but still reads primarily as a form.

### New structure

Use a two-zone composition on desktop:

Left:
- controls

Right:
- sticky visual scenario preview

On mobile:
- controls remain primary
- compact visual preview sits near the top and updates as inputs change

### Visual Scenario Preview

The preview should reflect only the user-entered configuration and supported deterministic fault state. It must not perform thermal calculations in the browser.

Allowed preview behavior:

- change ambient visual tone based on ambient input
- change fan icon state based on selected fault, not simulated command
- indicate thermostat fault state
- indicate vehicle-speed/ram-air intensity symbolically
- indicate pump/radiator/airflow health as configuration states

Do not predict temperatures before the FastAPI model runs.

### Form reduction

- group related controls visually
- use sliders only where they improve understanding and keep numeric fields available
- show units prominently
- use compact segmented controls for discrete fault modes where appropriate
- avoid giant empty form sections

### Run action

Make the run action persistent and obvious on mobile without obscuring content.

## 5. Results redesign

### Goal

Results should feel like a visual engineering playback workspace, not a report made of cards.

### Results hero summary

At the top show:

- scenario name
- COMPLETE state
- model ID
- run ID
- final engine temperature
- final coolant temperature
- peak temperature if available from returned result
- energy balance status

Use compact visual gauges or thermometers for final engine/coolant state rather than plain text-only boxes.

### Temperature visualization

Preserve the existing chart data source.

Improve visual hierarchy with:

- clear temperature axis
- clear time axis
- engine, coolant, radiator outlet curves
- selected-time cursor
- selected-time point markers
- gradient or subtle fill only when it improves legibility
- optional threshold bands for known model/control thresholds only when those thresholds already exist in the engineering model

Do not add unsupported danger thresholds.

### Playback

Preserve Play/Pause and scrub behavior.

Enhance it with:

- larger mobile hit targets
- elapsed/current time clearly associated with slider
- optional speed selector only if simple and reliable
- animated synchronized component state

### Thermal flow visual

Use the new `InteractiveThermalSchematic` for result playback rather than a stack of mostly rectangular nodes when practical.

### Insight module

Add a deterministic summary generated only from already-returned result data.

Examples of safe deterministic insights:

- final engine and coolant temperature
- maximum engine/coolant temperature
- thermostat opening state at final time
- whether fan activated
- whether energy balance passed
- time of model warning event if one exists

Do not generate unsupported mechanical diagnosis.

If a summary rule becomes complex, calculate it server-side or from returned result arrays using transparent deterministic logic. Do not use AI to infer mechanical failure.

## 6. Validation redesign

The Validation page already has real charts and should become the visual evidence center.

### Evidence ladder

Turn the verification/plausibility/calibration/holdout sequence into a horizontal timeline on desktop and a compact vertical stepper on mobile.

Use distinct states:

- complete
- active/pending
- future

### KIT comparison

Give the measured-vs-predicted chart more visual prominence.

Add a concise visual takeaway next to it:

`Warm-up too fast, final region similar`

Preserve the actual reported metrics and the explicit statement that this is plausibility evidence, not controlled validation.

### Controlled validation status

Represent the Argonne workflow visually:

```text
Acquire -> Hash -> Map -> Calibrate -> Freeze -> Holdout -> Report
```

Show the current stage as pending data acquisition/signal mapping.

Do not imply Argonne validation has occurred.

## 7. Media strategy

UI-5 should not rely on random stock images.

Use these media types:

### A. Custom SVG engineering illustrations

Preferred for:
- hero thermal system
- scenario thumbnails
- component states
- fault-state diagrams

Benefits:
- responsive
- crisp
- lightweight
- themeable
- animatable
- no licensing ambiguity

### B. Existing validation charts

Keep real evidence charts and make them more prominent.

### C. Mini data visualizations

Use small SVG sparklines for scenario cards and compact state previews.

### D. Optional static product imagery

If a decorative automotive image is ever added, it must be secondary to engineering content and must not imply a specific OEM vehicle is modeled by the generic V1 parameter set.

## 8. Motion system

Motion is part of the product explanation, not decoration.

### Required motion

- page-section reveal with restrained opacity/translate
- scenario-card media animation on hover/focus where appropriate
- animated coolant/airflow direction
- fan rotation when active in playback
- chart line reveal or transition on load
- value easing/counting when playback time changes
- playback cursor movement

### Motion limits

- avoid parallax-heavy marketing effects
- avoid constant large background animation
- avoid bouncing controls
- avoid motion that makes numerical values harder to read
- honor `prefers-reduced-motion`

### Dependency policy

Prefer native CSS, SVG animation, and React for simple motion. If an animation package materially simplifies maintainable interaction, inspect compatibility first and add only one focused dependency. Do not add a broad UI framework solely for UI-5.

## 9. Component inventory

Create or refactor toward these components as appropriate:

- `ThermalSystemHero`
- `InteractiveThermalSchematic`
- `ThermalFlowPath`
- `ThermalNode`
- `ScenarioCardV2`
- `ScenarioVisual`
- `MiniSparkline`
- `TemperatureGauge`
- `ResultSnapshot`
- `EvidenceTimeline`
- `ValidationTakeaway`
- `MotionReveal`
- `ScenarioConfigPreview`

Names may change if the existing codebase suggests a cleaner structure. Reuse existing components when that produces less duplication.

## 10. Text-density requirements

UI-5 must reduce visible prose.

Targets:

- hero supporting copy: maximum 2 short lines on desktop
- scenario card descriptive copy: maximum 1 short sentence
- major section intro: maximum 2 short sentences
- avoid paragraphs longer than approximately 45 to 60 words in the primary product flow
- detailed engineering explanations may remain on Model/Documentation-oriented surfaces where users intentionally seek depth

Do not remove required engineering provenance or limitations. Instead move secondary detail into expandable disclosures, tooltips, inspector panels, or documentation links.

## 11. Accessibility

- Maintain semantic headings.
- All interactive SVG components must be keyboard accessible where interaction is exposed.
- Do not rely on color alone for fault, validation, or pass/fail state.
- Maintain contrast on off-white backgrounds.
- Provide accessible text equivalents for meaningful graphics.
- Respect reduced-motion preference.
- Ensure mobile tap targets are at least comfortably finger-sized.

## 12. Responsive requirements

Primary QA widths:

- 360 px
- 390 px
- 430 px
- 768 px
- 1024 px
- 1440 px

The current mobile bottom navigation should remain usable.

Prevent content from appearing trapped behind the bottom navigation.

Avoid horizontal scrolling on Scenario Library, Results, and System Explorer.

## 13. Engineering integrity requirements

UI-5 must not:

- alter VTMS-V1 equations
- alter canonical scenario inputs
- alter solver settings
- change current generic parameter values
- claim controlled physical validation
- label the current model a digital twin
- move thermal calculations into React
- infer mechanical damage thresholds that are not in the model
- hide the current generic/uncalibrated status
- mutate returned SimulationResult data to make visuals look better

The visual layer may summarize returned results deterministically, but it must preserve authoritative values.

## 14. Implementation approach

### Phase A: audit and foundation

1. Run current tests and web checks before editing.
2. Inspect current route/component structure.
3. Identify CSS that can be consolidated instead of adding another stack of override files.
4. Create reusable visual primitives first.
5. Preserve current functional behavior.

### Phase B: highest-impact visual surfaces

Implement in this order:

1. Overview hero and product path
2. ScenarioCardV2 and Scenario Library
3. InteractiveThermalSchematic and System Explorer
4. Results visual playback
5. Simulation Lab configuration preview
6. Validation visual hierarchy

### Phase C: motion and responsive polish

Add motion after the static hierarchy works.

Do not use animation to compensate for poor layout.

### Phase D: QA

Run:

```text
npm run lint
npm run typecheck
npm run build
```

Run the repository Python/API suite to prove the presentation refactor did not change engineering behavior.

If existing production container checks are available, run them too.

Perform browser QA at the target viewport widths.

## 15. Acceptance criteria

UI-5 is complete only when all of the following are true:

### Visual communication

- Overview contains a dominant engineering visual above the fold.
- Scenario Library cards contain real visual previews, not just icons added to text cards.
- System Explorer reads as a connected thermal system, not a vertical collection of component boxes.
- Results show the outcome visually before requiring the user to read detailed values.
- Validation presents the evidence hierarchy visually.

### Text reduction

- Major product pages contain materially less visible prose.
- No page solves the redesign by adding more explanatory cards.

### Motion

- Coolant/airflow direction is communicated through purposeful motion or visual flow.
- Playback feels alive and synchronized.
- Reduced-motion behavior remains usable.

### Technical integrity

- API boundary unchanged unless a presentation-safe additional derived summary endpoint is explicitly justified.
- Existing simulations still run from the public frontend through FastAPI.
- Canonical scenario protections remain intact.
- All Python/API tests pass.
- ESLint passes.
- TypeScript passes.
- Next.js production build passes.
- Production containers still boot and pass health checks.

## 16. Explicit anti-patterns

Do not produce any of the following:

- another dashboard made mostly of white rounded rectangles
- large decorative gradients with little information
- generic stock car photography as the main visual solution
- a wall of icon cards
- unverified technical claims in marketing copy
- fake live telemetry
- fake sensor gauges
- fake heat maps not derived from modeled quantities
- an engine-bay illustration that implies detailed spatial temperature predictions
- moving numbers that do not correspond to authoritative result values

## 17. Definition of success

A user should be able to scroll the public VTMS application and understand its purpose primarily through visuals, interaction, and data presentation.

The desired reaction is not simply "this looks nicer." It should be:

> "I can see the thermal system, I understand what the simulation is doing, I can see how the operating scenario changes the system, and I can distinguish model behavior from validation evidence."

That is the UI-5 standard.