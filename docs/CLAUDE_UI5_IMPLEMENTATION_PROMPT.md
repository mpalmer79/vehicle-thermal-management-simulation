# Claude Code Prompt: VTMS UI-5 Visual Productization

Use this prompt from the repository root.

---

You are implementing **VTMS UI-5: Visual Productization** in the existing repository.

Before changing code, read these files completely:

1. `docs/UI5_VISUAL_PRODUCTIZATION_SPEC.md`
2. `ARCHITECTURE.md`
3. `README.md`
4. `docs/UI_UX_PRODUCT_SPEC.md`
5. `docs/INFORMATION_ARCHITECTURE.md`
6. `web/app/page.tsx`
7. `web/app/scenarios/page.tsx`
8. `web/app/system/page.tsx`
9. `web/app/simulate/page.tsx`
10. `web/app/validation/page.tsx`
11. `web/components/playback-workspace.tsx`
12. `web/components/scenario-card.tsx`
13. `web/components/thermal-loop.tsx`
14. `web/components/signal-chart.tsx`
15. `web/components/simulation-form.tsx`
16. `web/components/app-shell.tsx`
17. `web/lib/scenarios.ts`
18. `web/lib/vtms-types.ts`
19. `web/package.json`
20. the active global/UI CSS files under `web/app/`

Then inspect the rest of the `web/` tree before editing so you understand what can be reused.

## Objective

The current VTMS application is technically functional and deployed, but visually it is still too text-heavy and card-heavy. The Scenario Library in particular looks like repeated white rectangles containing headings, descriptions, metadata chips, and text links. The same underlying issue appears across Overview, System, Results, and parts of Validation.

Transform VTMS into a visually persuasive, portfolio-grade engineering product.

This is not a cosmetic color pass. It is a visual communication redesign.

The user should be able to understand the cooling system, scenario differences, simulation playback, and validation state through diagrams, media, motion, charts, and visual state changes without reading long paragraphs.

## Absolute design direction

Keep the existing UI-4 light visual foundation:

- off-white / warm ivory backgrounds
- dark navy / charcoal typography
- teal and cyan engineering accents
- coral/orange engine heat
- green radiator/verification states
- amber control/pending states
- selective purple for bypass/degradation

Do not return to black or near-black page backgrounds.

Do not solve UI-5 by adding more rounded white cards.

Do not solve it by adding random stock automotive photos.

Do not turn VTMS into a generic SaaS dashboard.

The visual character should be:

- modern automotive engineering
- technical but approachable
- premium
- visually explanatory
- dynamic
- credible
- mobile-first

## Engineering integrity is non-negotiable

Do not change:

- VTMS-V1 governing equations
- solver settings
- canonical S-01 through S-09 inputs
- generic model parameters
- FastAPI simulation contracts
- validation metrics
- validation evidence
- current validation status
- model classification

Do not move thermal calculations into React.

Do not fabricate live telemetry.

Do not fabricate vehicle-specific geometry or spatial heat maps.

Do not imply the current generic model is OEM calibrated.

Do not call VTMS-V1 a digital twin.

Do not invent danger, damage, boiling, or failure thresholds that are not already represented in the engineering model.

All displayed dynamic engineering values must come from existing fixture or authoritative SimulationResult data.

## Workflow

### 1. Establish a clean baseline

Before editing:

- run the Python/API test suite
- run web lint
- run web typecheck
- run the production Next.js build
- note the current pass count

Create a dedicated implementation branch if one does not already exist.

### 2. Audit before refactoring

Identify:

- which current components can be reused
- where CSS has accumulated through `globals.css`, `ui2.css`, `ui4.css`, and `ui4-polish.css`
- whether UI-5 is an appropriate point to consolidate theme/layout styles without destabilizing the product
- which route-level copy can be shortened
- what data is already available for visual treatment

Do not delete working behavior simply because the component will be visually redesigned.

### 3. Build reusable visual primitives first

Refactor or create a clean visual component layer. Suggested components include:

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

Use names that fit the repository if better names become obvious after inspection.

Prefer reusable SVG/React engineering visuals over raster assets.

## Page-by-page implementation

### OVERVIEW `/`

Current problem:

The hero is still mostly copy plus a model facts card, and the lower section is still three text-heavy feature cards.

Required redesign:

1. Keep the headline concept `See where the heat goes.` unless a very small copy refinement materially improves it.
2. Reduce hero supporting copy to one concise sentence.
3. Keep the main CTA to Simulation Lab and the secondary validation CTA.
4. Replace the current right-side model facts emphasis with a dominant custom thermal-system visual.
5. Create a `ThermalSystemHero` using SVG/React with:
   - engine thermal mass
   - engine-side coolant
   - thermostat
   - bypass branch
   - radiator
   - fan
   - ambient/ram airflow
   - directional coolant flow
   - directional air flow
6. Use restrained animation:
   - coolant flow movement
   - fan rotation when shown active
   - airflow movement
   - subtle engine heat pulse
7. Keep model identity and status visible, but compact.
8. Replace the three identical text feature cards with a visual product path:

   `SIMULATE -> WATCH THE SYSTEM -> REVIEW THE EVIDENCE`

   Each step should have a visual/icon treatment, one concise sentence maximum, and a CTA.

### SCENARIOS `/scenarios`

This is a highest-priority redesign.

Current `ScenarioCard` is approximately:

- ID/category
- title
- purpose sentence
- fact chips
- links

Replace it with a truly visual `ScenarioCardV2`.

Each scenario card must have a media/visual region occupying about 35 to 45 percent of the card.

Create scenario-specific visual behavior. Do not use the same decorative illustration on every card.

Examples:

- S-01: cold colors, rising warm-up sparkline, thermostat closed/open transition symbolism
- S-02: strong ram-air arrows, steady-state trend
- S-03: hot ambient field, fan-assisted idle
- S-04: higher thermal input and moving airflow
- S-05: failed fan state and rising temperature trend
- S-06: blocked thermostat/radiator flow with bypass emphasized
- S-07: reduced coolant circulation
- S-08: reduced radiator heat rejection
- S-09: restricted airflow

Do not invent result data if a scenario result fixture is not available. If actual scenario traces are not available in the frontend, use symbolic configuration visuals or sparklines derived from repository canonical summary data only if such data is already present and trustworthy. Otherwise, use a compact configuration visual rather than fake time-series data.

Required card content:

- scenario ID
- title
- category
- short behavior label
- compact operating conditions
- one strong primary CTA: `Simulate this scenario`
- optional secondary result preview where a real fixture exists

Reduce visible prose.

Mobile cards must not contain large empty white regions.

### SYSTEM `/system`

Replace the sense of stacked component boxes with a connected engineering schematic.

Build `InteractiveThermalSchematic` around the existing authoritative playback point.

Required nodes:

- engine
- coolant
- thermostat
- bypass
- radiator
- fan/airflow
- ambient sink

Required connections:

- engine to coolant heat flow
- thermostat split
- bypass path
- radiator path
- coolant return relationship
- radiator heat rejection
- fan/ram airflow

Interaction:

- tap/click component to select
- selected node receives visual emphasis
- inspector shows current values and a concise role summary
- playback remains synchronized

Use relative line thickness, opacity, dash speed, or particle density to communicate flow magnitude.

Do not imply this schematic is CAD, CFD, or real engine-bay geometry.

### SIMULATION LAB `/simulate`

Keep all current authoritative submission behavior.

Reframe the page as a visual configuration workspace rather than just a form.

Desktop:

- control panel left
- sticky configuration preview right

Mobile:

- compact preview near top
- grouped controls below
- persistent obvious Run Simulation action if practical

Create `ScenarioConfigPreview` that visualizes configuration only.

Allowed preview behavior before execution:

- ambient tone
- vehicle-speed/ram-air symbolic intensity
- selected fan failure state
- thermostat fault state
- pump health
- radiator health
- airflow health

Do not show predicted temperatures before running FastAPI.

Keep numeric inputs where precision matters. Sliders may supplement, not replace, numeric entry if useful.

### RESULTS `/results/[runId]`

Preserve current authoritative result retrieval and browser session behavior.

Make the result understandable visually at the top.

Required top-level summary:

- scenario name
- COMPLETE
- model ID
- run ID
- final engine temperature
- final coolant temperature
- peak engine/coolant temperature if safely derived from returned time series
- energy-balance status

Use compact visual temperature gauges/thermometers instead of only text boxes.

Improve `SignalChart` presentation while preserving authoritative source data:

- clear temperature axis
- clear time axis
- engine curve
- coolant curve
- radiator outlet curve
- selected-time cursor
- point markers
- excellent mobile readability

Keep Play/Pause and scrubbing.

Increase mobile hit targets.

Use the new thermal schematic for synchronized playback if practical.

Add a deterministic `ResultSnapshot` or insight section derived only from returned data, for example:

- final temperatures
- maximum temperatures
- whether fan activated
- final thermostat state
- energy-balance pass
- warning timing when warnings/events exist

Do not provide unsupported mechanical diagnosis.

### VALIDATION `/validation`

This page already contains real validation visuals. Make them the focus.

1. Convert the evidence ladder into a visual timeline/stepper.
2. Make measured-vs-predicted more prominent.
3. Add a concise visual takeaway:

   `Warm-up too fast, final region similar`

4. Preserve exact KIT metrics and the statement that this is plausibility evidence, not controlled validation.
5. Represent Argonne controlled-validation flow visually:

   `Acquire -> Hash -> Map -> Calibrate -> Freeze -> Holdout -> Report`

6. Show current state accurately as pending data/signal mapping.
7. Do not imply Argonne validation has happened.

## Motion requirements

Motion should explain state and flow.

Implement restrained:

- coolant direction animation
- air-flow animation
- fan rotation when appropriate
- chart transition/reveal
- value transitions during playback
- subtle section entrance
- scenario media hover/focus movement

Honor `prefers-reduced-motion`.

Avoid:

- parallax-heavy marketing effects
- large looping background videos
- bouncing controls
- constant animation unrelated to engineering meaning

## Dependency policy

The current frontend is intentionally small and currently depends primarily on Next.js and React.

Prefer native CSS, SVG, and React for straightforward animation.

If you believe one focused animation or visualization dependency is materially justified:

1. explain why before adding it
2. verify compatibility with the current Next.js/React versions
3. add only the minimum dependency
4. rerun the production security audit

Do not introduce a broad component/UI framework for UI-5.

## Text-density target

Reduce visible prose significantly.

- hero support: maximum 1 concise sentence
- scenario description: maximum 1 short sentence
- section intro: maximum 2 short sentences
- no giant paragraphs in the primary user flow

Keep engineering provenance and limitations, but move secondary detail into:

- component inspectors
- expandable disclosures
- tooltips where accessible
- documentation links

Do not hide limitations.

## Accessibility

- semantic headings
- keyboard-accessible interactive SVG components
- visible focus states
- contrast appropriate for light UI
- state not communicated by color alone
- accessible names/descriptions for engineering visuals
- reduced-motion support
- touch-friendly mobile controls

## Responsive QA

Verify at minimum:

- 360 px
- 390 px
- 430 px
- 768 px
- 1024 px
- 1440 px

Preserve the mobile bottom navigation.

No horizontal scrolling.

Ensure long pages have enough bottom padding so content never sits behind fixed navigation.

## Important anti-patterns

Reject your own implementation if it becomes:

- more cards with the same amount of text
- an icon-card wall
- a generic SaaS landing page
- a stock-photo automotive site
- a dark dashboard again
- a fake telemetry dashboard
- a fake 3D engine bay
- a collection of gauges with invented thresholds

## Implementation strategy

Do not attempt a blind one-file rewrite.

Work in coherent passes:

### Pass 1

- visual primitives
- Overview
- Scenario Library

Run checks.

### Pass 2

- InteractiveThermalSchematic
- System Explorer
- Results integration

Run checks.

### Pass 3

- Simulation Lab preview
- Validation timeline/evidence hierarchy
- motion polish
- responsive polish

Run checks.

### Pass 4

Perform visual QA and fix layout defects.

If browser/screenshot tooling is already available in your environment, use it to inspect the actual rendered pages at mobile and desktop widths. Do not add permanent test dependencies solely to make temporary screenshots unless justified.

## Required final verification

Before declaring UI-5 complete, run the repository's complete gate, including:

- Python/API tests
- web dependency/security audit used by the project
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- API container smoke test if available
- web container smoke test if available

Then provide:

1. concise summary of major visual changes
2. files/components created or materially changed
3. any new dependency and why it was necessary
4. before/after text-density observations
5. responsive QA performed
6. exact test/build results
7. any remaining visual concerns you recommend for a later pass

Do not merge directly to `main` until the full gate passes.

The UI-5 standard is not simply "prettier." The finished product must let a visitor visually understand the thermal system, scenario differences, simulation behavior, and evidence maturity with substantially less reading.

---