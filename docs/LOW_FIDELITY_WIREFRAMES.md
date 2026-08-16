# VTMS Low-Fidelity Wireframes

## Purpose

These wireframes define content hierarchy and interaction structure before visual design or frontend implementation begins.

They are intentionally low fidelity. Spacing, typography, final colors, icons, and component styling remain implementation decisions within the constraints of the UI/UX Product Specification.

---

## 1. Overview, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ VTMS-V1                              Model status: Generic / Verified       │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ Vehicle Thermal Management Simulation Platform              │
│ Overview     │ Understand heat generation, coolant transport, and          │
│ Simulate     │ radiator heat rejection through transient simulation.       │
│ System       │                                             [Open Sim Lab]  │
│ Scenarios    │                                                              │
│ Validation   │  ┌───────────────────────────────────────────────────────┐   │
│ Model        │  │                THERMAL SYSTEM PLAYBACK                │   │
│              │  │                                                       │   │
│              │  │ Engine ──heat──> Coolant ──> Thermostat ──> Radiator│   │
│              │  │   │               │             │              │      │   │
│              │  │   └─ambient       └─> Bypass ───┘              │      │   │
│              │  │                                      Ram + Fan │      │   │
│              │  │                                               ↓       │   │
│              │  │                                             Ambient    │   │
│              │  │                                                       │   │
│              │  │ t = 480 s       ◀──────●──────────────▶   [Play]    │   │
│              │  └───────────────────────────────────────────────────────┘   │
│              │                                                              │
│              │ Engine Temp     Coolant Temp     Q radiator      Pump Flow  │
│              │   108.2 °C        94.7 °C         21.8 kW        0.84 kg/s │
│              │                                                              │
│              │ [Run Cold Start] [Explore Faults] [Validation Evidence]      │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

### Overview behavior

- Default example is clearly labeled as a canonical simulation playback.
- Timeline updates all displayed system values.
- `Open Sim Lab` is the main CTA.
- Model status is always visible but not visually dominant.

---

## 2. Overview, mobile

```text
┌──────────────────────────────┐
│ VTMS-V1        [Model status]│
├──────────────────────────────┤
│ Thermal Management           │
│ Simulation Platform          │
│                              │
│ [ Open Simulation Lab ]      │
│                              │
│ ┌──────────────────────────┐ │
│ │ ENGINE                   │ │
│ │ 108.2 °C                 │ │
│ │    ↓ heat                │ │
│ │ COOLANT                  │ │
│ │ 94.7 °C                  │ │
│ │    ↓                     │ │
│ │ THERMOSTAT 67%           │ │
│ │   ↘ bypass               │ │
│ │ RADIATOR                 │ │
│ │ 21.8 kW rejected         │ │
│ │    ↑ ram + fan air       │ │
│ └──────────────────────────┘ │
│                              │
│ t 480 s   ─────●────  [▶]   │
│                              │
│ Coolant        Pump          │
│ 94.7 °C        0.84 kg/s     │
│                              │
├──────────────────────────────┤
│ Home  Simulate  System  More │
└──────────────────────────────┘
```

---

## 3. Simulation Lab, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ VTMS-V1                                      Simulation Lab                 │
├──────────────┬───────────────────────────────┬──────────────────────────────┤
│ Overview     │ SCENARIO INPUTS               │ PREVIEW / ENGINEERING CONTEXT│
│ Simulate ●   │                               │                              │
│ System       │ Preset                        │ S-03 Hot Ambient Idle        │
│ Scenarios    │ [ S-03 Hot Ambient Idle  v ]  │                              │
│ Validation   │                               │ Engine: 105 °C initial       │
│ Model        │ Operating conditions          │ Coolant: 92 °C initial       │
│              │ Ambient      [ 40 ] °C        │ Ambient: 40 °C               │
│              │ RPM          [1000] rpm       │                              │
│              │ Load         [ 25 ] %         │ Fault state                  │
│              │ Speed        [  0 ] km/h      │ None                         │
│              │ Duration     [1200] s         │                              │
│              │                               │ Model                         │
│              │ Initial conditions            │ VTMS-V1 / EM-V1              │
│              │ Engine temp  [105] °C         │ Generic parameters           │
│              │ Coolant temp [ 92] °C         │                              │
│              │                               │                              │
│              │ Faults                        │                              │
│              │ Fan failure      [ off ]      │                              │
│              │ Thermostat       [normal v]   │                              │
│              │ Pump health      [100%]       │                              │
│              │ Radiator health  [100%]       │                              │
│              │ Airflow health   [100%]       │                              │
│              │                               │                              │
│              │ [Advanced ▸]                  │                              │
│              │                               │                              │
│              │       [ Run Simulation ]      │                              │
└──────────────┴───────────────────────────────┴──────────────────────────────┘
```

### Editing behavior

- Changing a canonical preset marks it `Custom based on S-03`.
- Units remain attached to controls.
- Range errors appear beside the control before submission.
- Advanced heat override remains collapsed by default.

---

## 4. Simulation Lab, mobile

```text
┌──────────────────────────────┐
│ Simulation Lab               │
├──────────────────────────────┤
│ Preset                       │
│ [S-03 Hot Ambient Idle   v]  │
│                              │
│ Operating conditions         │
│ Ambient       [ 40 ] °C      │
│ Engine speed  [1000] rpm     │
│ Load          [ 25 ] %       │
│ Speed         [  0 ] km/h    │
│ Duration      [1200] s       │
│                              │
│ Initial conditions           │
│ Engine        [105] °C       │
│ Coolant       [ 92] °C       │
│                              │
│ Faults                   [>] │
│ Advanced                 [>] │
│                              │
│ [      Run Simulation      ] │
├──────────────────────────────┤
│ Home  Simulate  System  More │
└──────────────────────────────┘
```

Faults open as a bottom sheet rather than forcing a long primary form.

---

## 5. Results workspace, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ S-03 Hot Ambient Idle     COMPLETE    Generic parameters    [Edit & rerun] │
│ Warning: none                                                               │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ TEMPERATURE RESPONSE                                         │
│              │ ┌──────────────────────────────────────────────────────────┐ │
│              │ │  °C                                                      │ │
│              │ │ 140 ─ Engine                                             │ │
│              │ │ 120 ───────╮                                             │ │
│              │ │ 100 Coolant └──────────────────                          │ │
│              │ │  80                                                      │ │
│              │ │     0        300       600       900       1200 s       │ │
│              │ └──────────────────────────────────────────────────────────┘ │
│              │ t = 660 s        ◀────────●────────────▶        [▶ 2x]     │
│              │                                                              │
│              │ ┌──────────────────────────────┐ ┌────────────────────────┐ │
│              │ │ SYSTEM AT 660 s              │ │ SELECTED VALUES        │ │
│              │ │ Engine 121.3 °C              │ │ Q engine     28.1 kW  │ │
│              │ │    ↓ 24.9 kW                 │ │ Q radiator   21.2 kW  │ │
│              │ │ Coolant 96.1 °C              │ │ Pump flow   0.22 kg/s │ │
│              │ │    ↓ Thermostat 81%          │ │ Air flow    1.01 kg/s │ │
│              │ │ Radiator → Ambient           │ │ Fan         52%       │ │
│              │ └──────────────────────────────┘ └────────────────────────┘ │
│              │                                                              │
│              │ [Heat] [Flow] [Controls] [Energy] [Metadata]                │
│              │                                                              │
│              │ Energy balance: PASS   normalized residual 0.00008%          │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

### Results behavior

- Chart cursor, playback time, system schematic, and selected values are synchronized.
- Warnings stay above results until dismissed visually, but remain accessible.
- `Edit & rerun` copies the scenario into Simulation Lab and creates a new run on submission.
- Completed result data is immutable.

---

## 6. Results workspace, mobile

```text
┌──────────────────────────────┐
│ S-03 Hot Ambient Idle        │
│ COMPLETE                     │
│ Generic parameters           │
├──────────────────────────────┤
│ Temperature response         │
│ ┌──────────────────────────┐ │
│ │          chart           │ │
│ │ Engine / Coolant / Rad   │ │
│ └──────────────────────────┘ │
│                              │
│ t 660 s   ─────●────  [▶2x] │
│                              │
│ System at selected time      │
│ Engine      121.3 °C         │
│ Coolant      96.1 °C         │
│ Thermostat    81 %           │
│ Q radiator   21.2 kW         │
│                              │
│ [System Explorer]            │
│                              │
│ Heat | Flow | Energy | More  │
│                              │
│ Energy balance: PASS         │
├──────────────────────────────┤
│ Home  Simulate  System  More │
└──────────────────────────────┘
```

---

## 7. System Explorer, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ System Explorer                  Run: S-03             t = 660 s            │
├──────────────┬──────────────────────────────────────┬───────────────────────┤
│              │                                      │ COMPONENT INSPECTOR   │
│              │       ENGINE STRUCTURE               │                       │
│              │          121.3 °C                    │ Radiator              │
│              │             │ 24.9 kW                │                       │
│              │             ▼                        │ Heat rejection        │
│              │         COOLANT                      │ 21.2 kW               │
│              │          96.1 °C                     │                       │
│              │             │                        │ Effectiveness         │
│              │        ┌────┴─────┐                  │ 0.69                  │
│              │        ▼          ▼                  │                       │
│              │  THERMOSTAT     BYPASS               │ NTU                   │
│              │     81%           19%                │ 1.77                  │
│              │        │          │                  │                       │
│              │        └────┬─────┘                  │ Coolant flow          │
│              │             ▼                        │ 0.18 kg/s             │
│              │         RADIATOR  ◀── AIR            │                       │
│              │          21.2 kW   Ram + Fan         │ [Open Model Details]  │
│              │                                      │                       │
│              │ ◀────── timeline scrubber ─────────▶ │                       │
└──────────────┴──────────────────────────────────────┴───────────────────────┘
```

Selecting any component changes the inspector.

---

## 8. Scenario Library, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario Library                                 [Baseline] [Faults] [All]  │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ BASELINE OPERATION                                           │
│              │                                                              │
│              │ ┌──────────────────┐ ┌──────────────────┐                   │
│              │ │ S-01             │ │ S-02             │                   │
│              │ │ Cold Start       │ │ Warm Highway     │                   │
│              │ │ 20 °C ambient    │ │ 25 °C ambient    │                   │
│              │ │ 1200 rpm         │ │ 2500 rpm         │                   │
│              │ │ Purpose: warm-up │ │ Purpose: ram air │                   │
│              │ │ [Run] [Edit]     │ │ [Run] [Edit]     │                   │
│              │ └──────────────────┘ └──────────────────┘                   │
│              │                                                              │
│              │ FAULT / DEGRADATION                                          │
│              │                                                              │
│              │ ┌──────────────────┐ ┌──────────────────┐                   │
│              │ │ S-05             │ │ S-06             │                   │
│              │ │ Fan Failure      │ │ Thermostat Closed│                   │
│              │ │ Based on S-03    │ │ Based on S-03    │                   │
│              │ │ [Run] [Edit]     │ │ [Run] [Edit]     │                   │
│              │ └──────────────────┘ └──────────────────┘                   │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 9. Validation, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Validation Evidence                                                        │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ EVIDENCE MATURITY                                            │
│              │ [✓ Numerical verification]                                   │
│              │ [✓ External plausibility]                                    │
│              │ [○ Controlled calibration]                                   │
│              │ [○ Blind holdout validation]                                 │
│              │                                                              │
│              │ KIT EXTERNAL PLAUSIBILITY                                    │
│              │                                                              │
│              │ ┌──────────────────────────┐ ┌─────────────────────────────┐ │
│              │ │ measured vs predicted    │ │ RMSE        21.40 °C       │ │
│              │ │       chart              │ │ MAE         16.50 °C       │ │
│              │ │                          │ │ Bias        +16.13 °C       │ │
│              │ └──────────────────────────┘ │ Final error -0.79 °C        │ │
│              │                              └─────────────────────────────┘ │
│              │ ┌──────────────────────────┐                                 │
│              │ │ residual chart           │ No parameters were tuned       │
│              │ └──────────────────────────┘ in response to this comparison. │
│              │                                                              │
│              │ CONTROLLED VALIDATION                                        │
│              │ Pending Argonne D3 data acquisition                          │
│              │ [View Physical Validation Protocol]                          │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 10. Model, desktop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Engineering Model                                      VTMS-V1 / EM-V1     │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │ SYSTEM BOUNDARY                                              │
│              │ [compact diagram]                                            │
│              │                                                              │
│              │ TWO-STATE MODEL                                              │
│              │ Te = effective engine structure temperature                  │
│              │ Tc = bulk engine-side coolant temperature                    │
│              │                                                              │
│              │ Ce dTe/dt = Qengine - Qec - Qea                              │
│              │ Cc dTc/dt = Qec - Qrad                                       │
│              │                                                              │
│              │ [Engine Heat] [Pump] [Thermostat] [Radiator] [Airflow]      │
│              │                                                              │
│              │ Parameter provenance                                         │
│              │ Sourced | Assumed | Calibrated | Derived | Numerical        │
│              │                                                              │
│              │ [Engineering Specification] [Architecture]                   │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 11. Model-status drawer

```text
┌────────────────────────────────────┐
│ VTMS-V1 Model Status               │
│                                    │
│ Classification                     │
│ Physics-based lumped transient     │
│ thermal simulation                 │
│                                    │
│ Verification                       │
│ ✓ Numerical verification complete  │
│                                    │
│ Calibration                        │
│ Generic reference parameters       │
│                                    │
│ Physical validation                │
│ Controlled validation pending      │
│                                    │
│ Digital twin                       │
│ Not a digital twin in V1           │
│                                    │
│ [View Model] [View Validation]     │
└────────────────────────────────────┘
```

---

## 12. Interaction notes for implementation

### Timeline synchronization

A single selected playback timestamp is shared by:

- temperature chart,
- heat chart,
- flow chart,
- System Explorer,
- instrumentation values.

### Chart density

Never load all result channels into one chart by default.

### Panels

Desktop inspectors should use side drawers or adjacent panes. Mobile inspectors should use bottom sheets or full-screen panels.

### State clarity

Every screen displaying simulation data must be able to answer:

```text
Which model version?
Which scenario/run?
Which selected simulation time?
Is this simulated, measured, or derived?
Are there warnings?
```

### Motion

Animated flow is optional enhancement. Direction arrows and numeric values carry the meaning even when motion is disabled.

---

## 13. First implementation target

The first coded UI should prove only this workflow:

```text
Overview
  ↓
Select S-01
  ↓
Simulation Lab with frozen preset inputs
  ↓
Run through API or canonical fixture
  ↓
Results temperature chart
  ↓
Scrub timeline
  ↓
System Explorer values update
```

If that flow is strong, the rest of the application can grow around it without redesigning the core interaction model.