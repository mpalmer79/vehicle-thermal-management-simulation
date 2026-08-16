# VTMS UI/UX Product Specification

## Vehicle Thermal Management Simulation Platform

**Project:** VTMS  
**Current release:** VTMS-V1  
**Document status:** UI/UX foundation baseline  
**Scope:** Web application foundation for the existing VTMS-V1 physics engine and validation toolkit  
**Engineering authority:** The Python simulation core remains the only source of thermal calculations

---

## 1. Product intent

VTMS should feel like a modern automotive engineering workstation rather than a generic analytics dashboard.

The interface exists to help a user understand a transient thermal system:

1. what operating conditions were applied,
2. where heat is generated,
3. where heat moves,
4. how coolant and airflow transport energy,
5. how the thermostat, fan, pump, radiator, and faults affect the response,
6. whether the numerical solution is trustworthy,
7. and how simulation predictions compare with independent measurements.

The UI must preserve the engineering discipline already established in VTMS-V1. It must not turn numerical precision into implied physical accuracy, hide assumptions, or present the project as a vehicle-specific digital twin before the required maturity exists.

The product should be impressive to a portfolio visitor while remaining useful to an engineer who wants to inspect the model.

---

## 2. Product principles

### 2.1 Physics first

The web client never reimplements thermal equations. All authoritative values come from the Python engine through the future API layer.

### 2.2 Show the system, not only the numbers

The primary visual identity is the thermal system itself. Temperature, heat flow, coolant flow, air flow, thermostat state, fan command, and radiator effectiveness should be attached to recognizable system components.

A row of KPI cards is supporting information, not the product centerpiece.

### 2.3 Progressive disclosure

A visitor should be able to run a canonical scenario in seconds. An engineering user should be able to inspect detailed signals, provenance, solver diagnostics, and assumptions without those details overwhelming the first screen.

### 2.4 Separate simulation from evidence

The application must visually distinguish:

- simulated quantities,
- measured quantities,
- derived estimates,
- calibrated parameters,
- assumed parameters,
- numerical verification,
- external plausibility evidence,
- and future controlled validation.

### 2.5 Never imply live telemetry when replaying results

VTMS-V1 simulations are computed results. A timeline animation is a **simulation playback**, not a live engine stream. The UI must use that terminology until real connected vehicle telemetry exists.

### 2.6 Honest model maturity

Persistent product language should identify VTMS-V1 as a generic physics-based model with numerical verification and pending controlled physical validation.

### 2.7 Mobile must be functional

Desktop is the primary engineering workspace, but the application must remain usable on a phone. No essential action may depend on hover, wide tables, or tiny controls.

---

## 3. Primary audiences

### 3.1 Portfolio visitor

Needs to understand the project quickly and see that it is a real engineering simulation rather than a decorative dashboard.

Primary needs:

- understand what VTMS models,
- launch a canonical scenario,
- see the thermal system respond,
- understand the engineering credibility,
- inspect validation evidence,
- and reach the technical documentation.

### 3.2 Engineering reviewer

Needs traceability and technical depth.

Primary needs:

- inspect scenario inputs,
- inspect transient state and component outputs,
- inspect energy balance,
- inspect parameter provenance,
- compare scenarios,
- inspect warnings and solver diagnostics,
- and understand limitations.

### 3.3 Future connected-vehicle user

Not a V1 implementation target, but the architecture should leave room for:

- OBD-II/CAN replay,
- synchronized state estimation,
- vehicle-specific calibration,
- connected telemetry,
- and digital-twin workflows.

---

## 4. Product vocabulary

The UI should use consistent terminology.

| Term | Meaning in VTMS |
|---|---|
| Simulation | Deterministic model execution using VTMS physics |
| Simulation playback | UI animation through an already computed time series |
| Scenario | Complete set of operating conditions, initial conditions, and fault state |
| Canonical scenario | One of the frozen S-01 through S-09 engineering cases |
| Run | One execution of a scenario |
| External plausibility evidence | Comparison with independent real-world data that is not the formal controlled validation source |
| Verification | Evidence that software correctly solves the frozen equations |
| Validation | Comparison between prediction and physical measurement |
| Model status | Current engineering maturity and calibration state |
| Digital twin | Reserved for future synchronized vehicle-specific capability |

Avoid these terms in V1 unless explicitly discussing future maturity:

- live vehicle,
- real-time twin,
- production calibrated,
- OEM accurate,
- predictive maintenance diagnosis,
- validated vehicle model.

---

## 5. Primary information architecture

The primary navigation should contain six destinations.

1. **Overview**
2. **Simulation Lab**
3. **System Explorer**
4. **Scenarios**
5. **Validation**
6. **Model**

A secondary **Roadmap** destination can live in the project menu or footer rather than occupying primary navigation.

Recommended routes:

```text
/
/simulate
/system
/scenarios
/results/[runId]
/validation
/model
/roadmap
```

The `results/[runId]` route is reached from a simulation rather than treated as a permanent top-level navigation item.

---

## 6. Global application shell

### 6.1 Desktop

The desktop shell should use:

- compact left navigation rail,
- top context bar,
- central work area,
- optional right-side inspector drawer,
- persistent model-status indicator.

The application should maximize space for the thermal schematic and time-series visualization.

### 6.2 Mobile

Mobile should use:

- compact top bar,
- bottom navigation for the most important destinations,
- full-screen content regions,
- bottom sheets for parameter editing and detailed inspectors,
- horizontally scrollable legends only when unavoidable,
- touch targets of at least 44 px,
- no hover-only information.

The mobile Simulation Lab should prioritize scenario selection, Run Simulation, and the primary coolant/engine temperature plot. Detailed engineering channels can be reached through tabs or expandable sections.

### 6.3 Persistent model-status treatment

A small model-status control should be available globally:

```text
VTMS-V1
Numerically verified
Generic parameters
Controlled validation pending
```

It may collapse to a single `Model status` badge on mobile.

Selecting it opens a concise maturity panel rather than a marketing modal.

---

## 7. Overview

### 7.1 Purpose

The Overview is both the portfolio entry point and the fastest path into the engineering system.

It should answer within a few seconds:

- What is VTMS?
- What does it calculate?
- What is the current model state?
- What can I run right now?

### 7.2 Hero composition

The hero should be dominated by an interactive thermal-system schematic rather than text.

Suggested layout:

```text
[ VTMS-V1 | model status ]              [ Run canonical scenario ]

                  THERMAL SYSTEM

 Engine Structure  ->  Coolant  ->  Thermostat  ->  Radiator
       |                |              |               |
       |                +-> Bypass ----+               v
       |                                         Ambient Air
       +-----------------> Ambient             Ram + Fan

 Current playback values appear at each component.
```

Default Overview state should load a documented canonical scenario result, preferably S-01 cold start, without pretending that the simulation is currently running.

A timeline scrubber can allow the user to move through the result.

### 7.3 Supporting content

Below the schematic:

- engine structure temperature,
- coolant temperature,
- radiator outlet temperature,
- radiator heat rejection,
- thermostat opening,
- fan command,
- pump flow,
- energy residual status.

These should be compact instrumentation tiles, not a wall of cards.

### 7.4 Calls to action

Primary:

- `Open Simulation Lab`

Secondary:

- `Run Cold Start`
- `Explore Fault Scenarios`
- `View Validation Evidence`

---

## 8. Simulation Lab

### 8.1 Purpose

Simulation Lab is the main engineering interaction surface.

The user can:

- start from a canonical scenario,
- create a custom operating condition,
- inject supported V1 faults,
- run VTMS,
- and inspect the resulting transient response.

### 8.2 Input groups

#### Operating conditions

- ambient temperature, °C
- engine speed, rpm
- effective engine load, 0 to 1 or percentage display
- vehicle speed, km/h in UI, normalized to m/s at API boundary
- simulation duration

#### Initial conditions

- initial engine structure temperature, °C
- initial coolant temperature, °C

#### Advanced engineering input

- engine heat override, W, clearly labeled advanced
- output interval if exposed at all

The heat override should not be prominent for casual users.

### 8.3 Fault controls

Supported V1 faults map directly to the existing `FaultState` contract:

- fan failure
- thermostat normal
- thermostat stuck closed
- thermostat stuck open
- thermostat health
- pump health
- radiator health
- airflow health

Health values should be presented as percentages while preserving the 0 to 1 API representation.

Fault controls must never claim to reproduce a specific production failure severity unless calibrated evidence exists.

### 8.4 Input behavior

Every control needs:

- unit label,
- allowed range,
- concise engineering description,
- reset-to-scenario value,
- validation before submission.

Invalid values should be prevented or explained before the run is sent.

### 8.5 Run behavior

Primary action:

`Run Simulation`

After submission:

1. UI enters `computing` state.
2. API returns a complete `SimulationResult`.
3. UI transitions to Results.
4. Playback starts only if the user chooses `Play` or if a brief onboarding animation is enabled.

Do not fake progressive engine calculations in the browser.

### 8.6 Presets

Canonical scenarios should be selectable from a compact preset control.

Selecting a preset populates all editable fields and visibly identifies what changed from the canonical baseline if the user edits it.

A modified canonical scenario should become:

`Custom based on S-03 Hot Ambient Idle`

It should not retain the canonical scenario identity after parameters change.

---

## 9. Results workspace

### 9.1 Purpose

Results is where VTMS becomes an engineering analysis tool.

### 9.2 Primary layout

Desktop:

```text
[ Run summary / warnings / model status ]

[ Thermal system playback ]     [ Key values at selected time ]

[ Main transient chart --------------------------------------- ]

[ Heat flow ] [ Flow/control ] [ Energy balance ] [ Metadata ]
```

Mobile:

```text
[ Run summary ]
[ Main temperature chart ]
[ Timeline playback ]
[ System schematic ]
[ Tabs: Heat | Flow | Energy | Metadata ]
```

### 9.3 Main temperature chart

Default visible series:

- engine structure temperature
- coolant temperature
- radiator outlet temperature when meaningful
- ambient temperature if available from the scenario

The selected playback time should place a synchronized cursor on every chart and update the System Explorer values.

### 9.4 Engineering signal groups

#### Temperature

- engine structure temp
- coolant temp
- radiator outlet temp

#### Heat transfer

- engine heat
- engine-to-coolant heat
- engine-to-ambient heat
- radiator heat rejection

#### Flow

- pump flow
- radiator flow
- bypass flow
- air mass flow

#### Control/component state

- thermostat fraction
- fan fraction
- radiator effectiveness
- radiator NTU

### 9.5 Energy balance

Energy balance deserves a dedicated verification panel.

Display:

- input energy
- rejected energy
- stored energy change
- residual
- normalized residual
- pass/fail against the VTMS numerical verification criterion when applicable

Use plain language:

`Numerical energy balance: PASS`

not:

`Model accuracy: PASS`

### 9.6 Warnings

Warnings from `SimulationResult.warnings` must be prominent and persistent.

A high-temperature liquid-only model warning should explain that it is a model-domain caution and not a prediction of boiling or component damage.

### 9.7 Solver diagnostics

Place solver diagnostics in an expandable engineering inspector.

Expose:

- solver success,
- solver message,
- function evaluations,
- Jacobian evaluations,
- LU decompositions.

Do not give these equal visual weight with physical results.

---

## 10. System Explorer

### 10.1 Purpose

System Explorer is the distinctive visual engineering view of VTMS.

It should let the user understand energy and fluid paths at a selected instant.

### 10.2 Core components

- engine structure
- bulk coolant control volume
- pump
- thermostat
- bypass
- radiator
- fan
- ram airflow
- ambient environment

### 10.3 Visual encoding

Use line width and motion to represent active flow, but always show numeric values and labels.

Suggested semantic colors:

- heat / engine energy: amber-orange
- coolant path: cyan-blue
- air path: neutral blue-gray
- healthy/verified status: green
- caution: amber
- fault/warning: red
- inactive path: muted gray

Color must never be the only status indicator.

### 10.4 Component inspector

Selecting a component opens an inspector explaining:

- current value,
- governing relationship at a concise level,
- source/provenance category,
- relevant parameter values,
- limitations.

Example for radiator:

```text
Radiator
Heat rejection: 24.3 kW
Effectiveness: 0.71
NTU: 1.84
Coolant flow: 0.83 kg/s
Air flow: 0.64 kg/s
Model: crossflow, both fluids unmixed
```

The inspector should link to the Model page for the full equation explanation.

---

## 11. Scenario Library

### 11.1 Purpose

Scenario Library exposes the frozen S-01 through S-09 cases as understandable engineering tests.

### 11.2 Scenario grouping

#### Baseline operation

- S-01 Cold Start / Fast Idle
- S-02 Warm Highway
- S-03 Hot Ambient Idle
- S-04 Sustained Higher Load

#### Fault and degradation

- S-05 Fan Failure
- S-06 Thermostat Stuck Closed
- S-07 Pump Degradation
- S-08 Radiator Degradation
- S-09 Airflow Degradation

### 11.3 Scenario cards

Each scenario should show:

- scenario ID and name,
- duration,
- ambient temperature,
- RPM,
- load,
- vehicle speed,
- initial temperatures,
- fault condition,
- concise engineering purpose.

Primary action:

`Run Scenario`

Secondary action:

`Open in Simulation Lab`

### 11.4 Comparison mode

Scenario comparison is desirable but can follow the first UI shell.

Target behavior:

- select baseline run,
- select comparison run,
- overlay temperature responses,
- display delta in peak temperature, warm-up timing, final temperature, and rejected energy.

This is a UI-level comparison of separate authoritative simulation results, not a new physics model.

---

## 12. Validation

### 12.1 Purpose

Validation should be one of the strongest credibility pages in the product.

It must make it easy to distinguish current evidence from future formal validation.

### 12.2 Evidence hierarchy

Display evidence levels explicitly:

```text
Level 1  Numerical verification                 COMPLETE
Level 2  External real-world plausibility       COMPLETE
Level 3  Controlled calibration                  PENDING
Level 4  Blind holdout physical validation       PENDING
Level 5  Vehicle-specific connected validation   FUTURE
```

### 12.3 KIT section

Label:

`External Plausibility Evidence`

Show:

- measured vs predicted coolant temperature,
- residual plot,
- RMSE,
- MAE,
- bias,
- max error,
- warm-up arrival timing,
- final error,
- dataset and heat-input limitations.

The page should explicitly state that no VTMS parameters were changed in response to this first comparison.

### 12.4 Argonne section

Until the dataset is obtained:

`Controlled Physical Validation: Pending Data Acquisition`

Display the preregistered process rather than an empty chart.

Once data arrives, the same page should support:

- calibration run identity,
- holdout run identity,
- frozen parameter set,
- measured vs predicted curves,
- validation metrics,
- pass/fail against project acceptance criteria,
- residual interpretation.

### 12.5 Avoid a single accuracy score

Do not collapse validation into one percentage or confidence score. Thermal-model adequacy is multidimensional and should remain visible through actual metrics.

---

## 13. Model page

### 13.1 Purpose

The Model page explains the engineering foundation without reproducing the full technical specification.

### 13.2 Content sequence

1. System boundary
2. Two-state model
3. Energy balances
4. Coolant properties
5. Engine heat generation
6. Pump model
7. Thermostat and bypass
8. Fan and airflow
9. Crossflow effectiveness-NTU radiator
10. Fault models
11. Numerical solver
12. Verification
13. Assumptions and exclusions
14. Parameter provenance
15. Links to formal documents

### 13.3 Equation presentation

Use readable equations with plain-language descriptions.

Core balance:

```text
C_e dT_e/dt = Q_engine - Q_ec - Q_ea
C_c dT_c/dt = Q_ec - Q_rad
```

Every equation section should answer:

- What does this calculate?
- Why is it in the model?
- Which UI outputs depend on it?
- What are its limitations?

### 13.4 Parameter provenance

The interface should distinguish:

- sourced,
- assumed,
- calibrated,
- derived,
- numerical.

This should be visible through text badges and not color alone.

---

## 14. Roadmap

The roadmap communicates maturity without overclaiming.

```text
VTMS-V1
Physics simulation
        ↓
Controlled validation
        ↓
VTMS-V2
Vehicle-calibrated model
        ↓
OBD-II / CAN replay
        ↓
Connected model
        ↓
State estimation
        ↓
Vehicle-specific digital twin
```

Future AI should appear above the deterministic system as interpretation, diagnostics, anomaly explanation, and optimization support. It should not be drawn as replacing the physics engine.

---

## 15. API-facing UI contract

The UI should be designed around the existing Python domain model.

### 15.1 Simulation request

Conceptual API request:

```json
{
  "scenario_id": "custom",
  "name": "Custom hot idle",
  "duration_s": 1200,
  "ambient_temp_c": 40,
  "engine_speed_rpm": 1000,
  "effective_load": 0.25,
  "vehicle_speed_m_s": 0,
  "initial_engine_temp_c": 105,
  "initial_coolant_temp_c": 92,
  "engine_heat_override_w": null,
  "faults": {
    "fan_failed": false,
    "thermostat_mode": "normal",
    "thermostat_health": 1.0,
    "pump_health": 1.0,
    "radiator_health": 1.0,
    "airflow_health": 1.0
  }
}
```

The exact Pydantic schema will be frozen when the FastAPI layer is implemented.

### 15.2 Simulation response

The API should serialize the existing `SimulationResult` contract without deleting engineering metadata required by the UI.

Required response groups:

- model metadata
- scenario metadata
- parameter snapshot
- provenance snapshot
- time series
- events
- energy balance
- warnings
- solver diagnostics

### 15.3 Client behavior

The client may:

- format units,
- filter displayed series,
- animate playback,
- compare separate runs,
- calculate purely presentational deltas between already returned values.

The client may not:

- calculate radiator heat rejection,
- calculate thermostat behavior,
- calculate engine heat,
- integrate temperatures,
- alter engineering outputs to make a result look plausible.

---

## 16. Run state model

The UI should use an explicit application state machine.

```text
idle
  -> editing
  -> ready
  -> computing
  -> complete
  -> playback

computing -> error
complete -> editing
playback -> complete
```

A completed result remains immutable. Editing inputs creates a new prospective run rather than silently mutating the completed result.

---

## 17. Visual system direction

### 17.1 Design character

Keywords:

- technical
- precise
- automotive
- instrumented
- modern
- restrained
- high information density when requested
- visually understandable at a glance

Avoid:

- generic SaaS gradient hero sections,
- excessive glassmorphism,
- decorative gauges with no engineering value,
- fake 3D engine imagery that does not map to the model,
- excessive explanatory text on every screen.

### 17.2 Initial dark theme palette

Recommended starting tokens:

```text
--bg:              #081018
--surface-1:       #0E1822
--surface-2:       #14212D
--border:          #253544
--text-primary:    #F4F7FA
--text-secondary:  #A9B7C5
--coolant:         #3CCBDB
--heat:            #FF9F43
--airflow:         #7FA8C9
--success:         #42D392
--warning:         #F7C948
--danger:          #FF6262
```

These are initial UI tokens, not engineering signal standards. Contrast must be tested before implementation is finalized.

### 17.3 Typography

Recommended:

- primary UI: Inter or compatible system sans-serif
- engineering values / code / units: a restrained monospace such as JetBrains Mono or system monospace

Do not use monospace for large blocks of body text.

### 17.4 Number formatting

Use consistent engineering formatting:

```text
96.4 °C
24.3 kW
0.83 kg/s
71 %
1.84 NTU
```

Avoid false precision. Display precision should match meaningful engineering resolution rather than raw floating-point output.

---

## 18. Charts and playback

### 18.1 Time synchronization

All charts and the System Explorer share one selected timestamp.

Moving the timeline cursor updates:

- chart crosshair,
- component values,
- flow indicators,
- thermostat position,
- fan state,
- radiator state.

### 18.2 Playback controls

Provide:

- play/pause
- timeline scrubber
- current simulation time
- playback speed: 0.5x, 1x, 2x, 5x, 10x
- jump to start/end

Playback speed changes only the visualization rate.

### 18.3 Chart defaults

Do not show every series at once.

Default Results view:

- engine structure temp
- coolant temp
- radiator outlet temp

Secondary tabs reveal heat, flow, control, and energy signals.

### 18.4 Tooltips

Tooltips should show:

- timestamp,
- value,
- unit,
- signal name.

Where relevant, indicate `simulated`, `measured`, or `derived estimate`.

---

## 19. Accessibility

Minimum requirements:

- WCAG-conscious contrast
- keyboard navigation
- visible focus states
- semantic form labels
- accessible chart summaries
- no color-only status encoding
- no hover-only engineering explanation
- reduced-motion support for animated flow and playback
- large touch targets on mobile

If reduced motion is enabled, flow animations become static directional indicators while values continue to update.

---

## 20. Error and empty states

### 20.1 API unavailable

Message:

`Simulation service unavailable. Your scenario inputs have been preserved.`

Do not invent fallback results.

### 20.2 Solver failure

Show the actual solver failure state returned by the backend and keep the scenario inputs available for inspection.

### 20.3 No validation data

Show the preregistered validation plan and evidence status rather than a blank visualization.

### 20.4 Unsupported model request

If a user tries to enter a condition outside the supported model domain, explain the supported range and why it exists.

---

## 21. V1 UI implementation scope

### Phase UI-1: shell and static engineering views

- Next.js application shell
- responsive navigation
- theme tokens
- Overview composition
- System Explorer static component structure
- Scenario Library
- Model page
- Validation page using existing committed evidence
- mock `SimulationResult` fixture derived from a real canonical result

### Phase UI-2: FastAPI integration

- scenario request DTO
- simulation endpoint
- canonical scenario endpoint
- model metadata endpoint
- typed frontend API client
- full Results workspace

### Phase UI-3: interactive simulation playback

- synchronized timeline
- system flow visualization
- signal charts
- warning states
- energy balance inspector
- provenance inspector

### Phase UI-4: comparison and polish

- baseline vs fault comparison
- shareable run configuration
- export CSV/JSON results
- documentation links
- performance and accessibility audit

### Deferred

- Argonne calibration UI
- live OBD-II/CAN
- vehicle selector implying calibrated models
- AI diagnostics
- digital-twin state display
- user accounts unless a real product need emerges

---

## 22. Definition of done for the UI foundation

UI/UX foundation is complete when:

1. primary navigation and routes are frozen,
2. each page has a defined purpose and content hierarchy,
3. scenario inputs map directly to the Python scenario contract,
4. result visualizations map directly to `SimulationResult`,
5. measured, simulated, and derived data are visually distinguished,
6. model maturity remains visible,
7. mobile layouts are defined,
8. low-fidelity wireframes exist for all primary screens,
9. accessibility requirements are documented,
10. implementation phases are sequenced without requiring changes to VTMS physics.

---

## 23. Product decision summary

The UI should not begin as a collection of analytics cards.

The central interaction is:

```text
Choose operating condition
        ↓
Run authoritative Python simulation
        ↓
Explore heat and fluid paths
        ↓
Scrub transient response through time
        ↓
Inspect engineering evidence and limitations
```

The visual signature of VTMS is the relationship between the thermal-system schematic and the synchronized transient data.

That is the foundation the first Next.js implementation should preserve.