# VTMS Information Architecture

## Purpose

This document freezes the first web-application information architecture for VTMS-V1.

The goal is to keep the application understandable to a portfolio visitor while preserving a clear path to detailed engineering analysis.

The architecture is deliberately smaller than a typical analytics product. VTMS should not bury the engineering model under dozens of dashboard routes.

---

## 1. Primary navigation

```text
Overview
Simulation Lab
System Explorer
Scenarios
Validation
Model
```

Secondary destinations:

```text
Results/[runId]
Roadmap
Engineering documents
Repository
```

Recommended routes:

```text
/                     Overview
/simulate             Simulation Lab
/system               System Explorer
/scenarios            Scenario Library
/results/[runId]      Simulation Results
/validation           Validation Evidence
/model                Engineering Model
/roadmap              Project Maturity Roadmap
```

---

## 2. Navigation hierarchy

```text
VTMS
│
├── Overview
│   ├── Thermal system hero
│   ├── Model status
│   ├── Canonical quick run
│   └── Key engineering outputs
│
├── Simulation Lab
│   ├── Scenario preset
│   ├── Operating conditions
│   ├── Initial conditions
│   ├── Fault injection
│   ├── Advanced heat override
│   └── Run Simulation
│
├── System Explorer
│   ├── Engine structure
│   ├── Coolant volume
│   ├── Pump
│   ├── Thermostat
│   ├── Bypass
│   ├── Radiator
│   ├── Fan
│   ├── Ram airflow
│   └── Component inspector
│
├── Scenarios
│   ├── Baseline operation
│   │   ├── S-01 Cold Start / Fast Idle
│   │   ├── S-02 Warm Highway
│   │   ├── S-03 Hot Ambient Idle
│   │   └── S-04 Sustained Higher Load
│   └── Fault and degradation
│       ├── S-05 Fan Failure
│       ├── S-06 Thermostat Stuck Closed
│       ├── S-07 Pump Degradation
│       ├── S-08 Radiator Degradation
│       └── S-09 Airflow Degradation
│
├── Validation
│   ├── Evidence hierarchy
│   ├── Numerical verification
│   ├── KIT external plausibility evidence
│   ├── Controlled validation status
│   ├── Physical validation protocol
│   └── Limitations
│
├── Model
│   ├── System boundary
│   ├── State variables
│   ├── Governing balances
│   ├── Components
│   ├── Solver
│   ├── Parameter provenance
│   ├── Assumptions and exclusions
│   └── Formal documentation
│
├── Results/[runId]
│   ├── Run summary
│   ├── Temperature response
│   ├── System playback
│   ├── Heat flows
│   ├── Fluid and air flows
│   ├── Component controls
│   ├── Energy balance
│   ├── Warnings
│   ├── Solver diagnostics
│   └── Metadata / provenance
│
└── Roadmap
    ├── VTMS-V1
    ├── Controlled validation
    ├── VTMS-V2
    ├── OBD-II/CAN replay
    ├── Connected model
    └── Digital twin maturity
```

---

## 3. Page responsibility rules

### Overview

**Question answered:** What is VTMS and what is the thermal system doing?

Must not become a full Results page.

The Overview should surface the system schematic, model status, a small number of primary values, and obvious routes into simulation or validation.

### Simulation Lab

**Question answered:** What conditions should VTMS simulate?

This page owns editable scenario inputs. Other pages may deep-link to it with preloaded values but should not duplicate the complete scenario editor.

### System Explorer

**Question answered:** Where is heat or fluid moving at this selected moment?

This page owns component-centric inspection. It should not become a second Model documentation page.

### Scenarios

**Question answered:** Which frozen engineering test should I run?

This page owns canonical scenario discovery and scenario purpose.

### Results

**Question answered:** What happened during this simulation run?

This page owns the complete transient result and detailed engineering inspection.

### Validation

**Question answered:** What evidence exists that the model behaves like a physical vehicle?

This page owns measured-vs-predicted comparisons, evidence status, calibration/holdout distinctions, and limitations.

### Model

**Question answered:** How does VTMS calculate the result?

This page owns concise engineering explanations and links to the formal specification.

### Roadmap

**Question answered:** What is VTMS today and what must happen before it becomes a digital twin?

This page prevents future capabilities from being confused with current capabilities.

---

## 4. Global context objects

The UI has four important context objects.

### 4.1 Model context

```text
model version
model status
parameter set
validation state
```

This context is global and read-only in VTMS-V1.

### 4.2 Scenario context

```text
scenario identity
operating conditions
initial conditions
fault state
```

Editable in Simulation Lab.

### 4.3 Run context

```text
run identifier
scenario snapshot
SimulationResult
selected playback time
warnings
```

A run is immutable once computed.

### 4.4 Evidence context

```text
dataset identity
measurement type
prediction source
validation classification
metrics
limitations
```

Used only by Validation views.

---

## 5. Core user flows

### Flow A: Portfolio visitor quick experience

```text
Overview
  ↓
Run S-01 Cold Start
  ↓
Results
  ↓
Scrub thermal playback
  ↓
Validation
  ↓
Model
```

Target: a visitor should understand the project without configuring parameters manually.

### Flow B: Custom engineering simulation

```text
Simulation Lab
  ↓
Choose preset or Custom
  ↓
Edit operating conditions
  ↓
Set supported fault state
  ↓
Run Simulation
  ↓
Results
  ↓
Inspect charts / energy / provenance
```

### Flow C: Fault exploration

```text
Scenarios
  ↓
S-03 Hot Ambient Idle
  ↓
Run baseline
  ↓
S-05 Fan Failure
  ↓
Run fault
  ↓
Compare responses
```

Comparison is a later UI capability, but the architecture must leave room for it.

### Flow D: Engineering credibility review

```text
Overview model-status badge
  ↓
Validation
  ↓
KIT evidence
  ↓
Controlled validation plan
  ↓
Model
  ↓
Formal specification
```

---

## 6. Desktop navigation behavior

Recommended shell:

```text
┌────────────┬──────────────────────────────────────────┐
│ VTMS       │ Top context bar                          │
│            ├──────────────────────────────────────────┤
│ Overview   │                                          │
│ Simulate   │                                          │
│ System     │              PAGE CONTENT                │
│ Scenarios  │                                          │
│ Validation │                                          │
│ Model      │                                          │
│            │                                          │
│ Status     │                                          │
└────────────┴──────────────────────────────────────────┘
```

The navigation rail should remain compact. Long explanatory descriptions do not belong inside navigation.

---

## 7. Mobile navigation behavior

Recommended bottom navigation:

```text
Overview | Simulate | System | Scenarios | More
```

`More` contains:

```text
Validation
Model
Roadmap
Engineering docs
GitHub
```

When viewing Results, the bottom navigation may remain available but the first visual priority is the result itself.

---

## 8. Result information hierarchy

Results should be revealed in this order:

1. Run identity and warnings
2. Primary temperature response
3. Selected-time system state
4. Heat flows
5. Coolant and air flows
6. Thermostat / fan / radiator state
7. Energy balance
8. Parameter provenance
9. Solver diagnostics

This sequence matches user significance rather than raw data structure.

---

## 9. Engineering evidence hierarchy

Evidence classification must remain visible throughout the product.

```text
NUMERICAL VERIFICATION
Does code solve the equations?

EXTERNAL PLAUSIBILITY
Does the generic model show physically recognizable behavior against independent road telemetry?

CONTROLLED CALIBRATION
Which uncertain parameters are fitted using one qualified experiment?

BLIND HOLDOUT VALIDATION
How does the frozen calibrated model perform on untouched experiments?

CONNECTED VEHICLE VALIDATION
How does a vehicle-specific synchronized model behave in operation?
```

The UI must not let a user mistake one evidence level for another.

---

## 10. URL and shareability behavior

A canonical scenario should have a stable URL:

```text
/scenarios/S-01
```

A completed run may eventually support a shareable run configuration, but V1 should avoid persisting simulation results in a database until there is a real need.

An initial implementation can keep run state client-side and use generated local run IDs.

If persisted runs are added later, they must capture the complete scenario snapshot and model metadata so results remain reproducible.

---

## 11. Search and filtering

Global search is unnecessary for the first version.

Useful local filters:

- Scenario Library: baseline / fault / degradation
- Results signals: temperature / heat / flow / controls
- Model parameters: sourced / assumed / calibrated / derived / numerical

Do not add generic enterprise filtering patterns that do not solve a real VTMS task.

---

## 12. Empty and future states

### Controlled validation pending

Validation should show:

- current stage,
- data acquisition status,
- preregistered methodology,
- expected metrics,
- link to protocol.

### No completed run

System Explorer may display a canonical example with an explicit label:

`Example playback: S-01`

or direct the user to run a scenario.

It must not display unlabeled invented values.

---

## 13. Information architecture acceptance criteria

The information architecture is acceptable when:

- no engineering concept has multiple competing home pages,
- canonical scenarios can be reached in two taps/clicks,
- custom simulation can be started in one primary destination,
- every completed run has one authoritative Results workspace,
- validation is structurally separated from simulation,
- model documentation is structurally separated from validation evidence,
- current and future digital-twin capability cannot be confused,
- mobile navigation preserves all essential tasks.