# VTMS-V2 Model Hierarchy and Equation Freeze Plan

## Purpose

This document defines the revised **Gate V2-2** after full VTMS-V1 residual reconstruction.

The earlier plan treated a five-state topology as the frozen design target. Full-trace diagnostics and counterfactual falsification show that conclusion was premature. A static thermostat/control-curve change alone has enough leverage to remove much of the hot-region residual numerically, even though such a post-hoc change is not an acceptable physical calibration.

VTMS-V2 will therefore use a nested model hierarchy. Additional states are promoted only when a lower-order model fails with physically credible, preregistered parameters.

## Gate V2-2: Model Hierarchy Freeze

Before any V2 physics engine is implemented, freeze:

1. model hierarchy M0 through M3;
2. vehicle-specific thermostat/control evidence policy;
3. radiator/bypass flow law used by M0;
4. cooling-pack airflow boundary policy;
5. quantitative promotion criteria between model levels;
6. development/calibration evidence roles;
7. untouched V2 validation evidence.

Only after this gate passes does each model level receive its own equation freeze.

## V2-M0: corrected-control two-state falsification baseline

State vector:

```text
x = [T_engine, T_coolant]
```

M0 retains the V1 thermal-state count intentionally. It is not presumed to be the final V2 architecture.

M0 changes only assumptions that are not defensible as vehicle-specific physics:

- source and freeze the thermostat/control law for the 2012 Focus or document uncertainty explicitly;
- separate thermostat valve command from radiator-flow fraction through a bounded monotonic hydraulic law;
- make dynamometer cooling-pack airflow provenance explicit;
- preserve direct fuel-energy evidence;
- preserve deterministic numerical integration and energy accounting.

### M0 purpose

Test whether V1 failed principally because its assumed control/boundary functions were wrong rather than because two thermal states are mathematically incapable of explaining the evidence.

### M0 prohibition

Do not use consumed V1 traces to freely fit a thermostat temperature until residuals look good. The Phase 2 thermostat shifts are diagnostic counterfactuals only.

## V2-M1: minimum hot/cold coolant topology

Promote to M1 if M0 cannot satisfy preregistered development criteria with physically credible parameters.

State vector:

```text
x = [T_engine, T_hot, T_cold]
```

where:

- `T_engine` is one effective engine-structure state;
- `T_hot` is engine-out / ECT-side coolant;
- `T_cold` is radiator-return / pump-inlet coolant.

Initial observation equation:

```text
ECT_pred = T_hot
```

### M1 rationale

Full-trace V1 diagnostics show near-zero residual around 88 to 92 C in both holdouts followed by large negative residual as measured ECT approaches 99 C. V1 also calculates large algebraic radiator outlet temperature drops but cannot retain that spatial separation because it integrates only one coolant state.

M1 directly tests whether preserving hot-side and cold-side coolant states resolves the regulated-region failure without adding unnecessary engine or thermostat states.

## Candidate M1 energy architecture

The exact equations are not frozen yet, but the equation review must conserve coolant enthalpy through engine heating, radiator cooling, bypass flow, and branch mixing.

A preferred conceptual form is:

```text
engine structure -> hot coolant
hot coolant -> thermostat-controlled split
split -> radiator branch + bypass branch
radiator branch -> cold coolant
bypass branch + radiator return -> pump/engine inlet
```

The final equations must avoid double-counting coolant transport and must pass closed-system conservation tests.

## V2-M2: split engine thermal storage

Promote to M2 only if M1 retains systematic transient residuals or requires unphysical effective engine parameters.

State vector:

```text
x = [T_head, T_slow, T_hot, T_cold]
```

where:

- `T_head` represents faster combustion-facing/head thermal storage;
- `T_slow` represents slower engine/oil/block-associated storage;
- `T_hot` and `T_cold` retain the M1 coolant topology.

### Oil as auxiliary evidence

Argonne provides measured engine-oil temperature. M2 should use oil temperature as an independent observable for the slow-state hypothesis before introducing a dedicated oil state.

A separate oil state is not authorized merely because oil is physically real.

## V2-M3: dynamic thermostat state

Promote to M3 only if a physically sourced static thermostat/control law leaves repeatable lag or hysteresis residuals, or independent evidence supports dynamic thermostat behavior.

Candidate state vector:

```text
x = [T_head, T_slow, T_hot, T_cold, x_th]
```

Candidate thermostat equation:

```text
tau_th dx_th/dt = x_cmd(T_hot, thermal_direction) - x_th
```

with:

```text
0 <= x_th <= 1
```

Separate opening and closing command laws may be used if hysteresis evidence exists.

The five-state architecture remains a valid candidate, but it is **not frozen as the minimum required V2 model**.

## Thermostat/control evidence requirement

The Phase 2 counterfactual shows thermostat assumptions have unusually high leverage on the hot-region residual. Therefore thermostat/control behavior must be constrained independently before topology selection.

Required evidence hierarchy:

1. OEM engineering/service specification for the exact vehicle/engine, if available;
2. component-level manufacturer specification for the exact thermostat assembly;
3. controlled bench characterization;
4. documented equivalent component specification with uncertainty;
5. engineering assumption only if no stronger source exists, explicitly labeled and subjected to sensitivity analysis.

A post-hoc threshold that improves consumed residuals is not physical evidence.

## Coolant hydraulic network

All V2 model levels must discontinue the V1 identity:

```text
radiator_flow_fraction = thermostat_opening_fraction
```

Permitted low-order approaches are:

### Option A: branch-resistance solution

```text
DeltaP_rad(m_dot_rad, valve_state) = DeltaP_bypass(m_dot_bypass, valve_state)
m_dot_pump = m_dot_rad + m_dot_bypass
```

Preferred when resistance data can be constrained.

### Option B: bounded monotonic flow-split law

```text
f_rad = g(valve_state, m_dot_pump)
m_dot_rad = f_rad m_dot_pump
m_dot_bypass = (1 - f_rad) m_dot_pump
```

Acceptable for M0/M1 if `g` is monotonic, bounded, auditable, and preregistered.

## Pump model

The V1 RPM-based pump-flow model may be retained initially as a fixed candidate boundary, but pump flow, thermostat flow split, and radiator conductance must not become simultaneous unconstrained compensators.

Classify pump parameters before any fit as:

- sourced/fixed;
- engineering-assumed/fixed;
- or calibratable under a specific stage.

## Radiator model

The V1 effectiveness-NTU framework remains acceptable as a baseline heat-exchanger structure.

### M0/M1 baseline

Begin with the frozen effective-UA formulation unless independent evidence supports a different law. This isolates the impact of control and coolant-state topology.

### Conditional flow-dependent UA

Promote to a flow-dependent law only if the lower-order radiator formulation leaves systematic residuals across independently varying coolant/airflow conditions:

```text
UA_rad = UA_ref
         (m_dot_air / m_dot_air_ref)^a_air
         (m_dot_cool / m_dot_cool_ref)^a_cool
```

Constant radiator UA alone has already been falsified as the sole solution to the V1 failures, but this does not prove that flow-dependent UA must be introduced before the control/topology hypotheses are tested.

## Airflow boundary model

V2 must separate:

```text
road vehicle speed
chassis/dyno speed
radiator-core air mass flow
```

### Road simulation

A vehicle-speed-to-core-flow surrogate is acceptable if explicitly identified as a vehicle-level approximation with provenance and uncertainty.

### Chassis-dyno development and validation

Dyno speed must not silently become radiator face velocity.

Preferred evidence:

- measured cooling-pack airflow;
- documented test-cell fan command with frozen transfer law;
- preregistered surrogate with uncertainty bounds.

Full-trace VAL-HOT residuals show almost no raw correlation with dyno speed, so airflow is not currently ranked as the primary cause of both holdout failures. Governance remains necessary regardless.

## Heat-input partition

Direct fuel evidence remains the preferred thermal input basis:

```text
Q_fuel = m_dot_fuel LHV
```

### M0/M1

Retain a fixed effective heat fraction initially to avoid adding correlated degrees of freedom while testing the dominant control/topology hypothesis.

### Conditional operating-dependent partition

Introduce:

```text
eta_heat = f(rpm, load, thermal_state)
```

only if lower-order models retain load-correlated residuals after the coolant/control structure is corrected.

The Phase 2 wall-heat counterfactual showed that increasing one constant heat fraction cannot explain VAL-HOT alone, so heat partition is not the first V2 degree of freedom.

No machine-learned residual correction is permitted in the initial V2 physics hierarchy.

## Initial-state policy

All model levels must improve V1 initialization governance.

Supported modes:

### Cold soak

All unobserved thermal states begin within a preregistered tolerance of measured ambient/coolant soak conditions.

### State carryover

States are propagated from a preceding simulated test segment or soak.

### Governed state estimation

Unobserved initial states may be estimated from pre-observation history under a frozen estimator.

A blind validation trace may not fit its own initial state.

The persistent late VAL-HOT error proves initialization is not the sole V1 failure mechanism.

## Model promotion criteria

Promotion criteria must be frozen before the lower-order model is executed against the designated V2 development set.

### M0 -> M1

Promote if M0 requires any of the following:

- thermostat/control parameters outside independently defensible ranges;
- branch-flow behavior outside physical bounds;
- persistent regulated-region bias above the development threshold;
- incompatible parameter values across cold-start, hot-start, and highway conditions.

### M1 -> M2

Promote if M1 shows:

- persistent warm-up shape error after hot/cold coolant topology correction;
- effective engine capacity/coupling parameters repeatedly pressing bounds;
- residual patterns that correlate with independent oil-temperature dynamics;
- incompatible transient parameters across cold and hot conditions.

### M2 -> M3

Promote if M2 with a sourced static thermostat law shows:

- reproducible opening/closing path dependence;
- time lag around control transitions not explainable by coolant transport;
- or independent evidence of thermostat actuator dynamics.

Do not promote models solely because a higher-order version can fit consumed data better.

## Identifiability constraints

Every model level must pass synthetic identifiability review before physical fitting.

Required work:

1. local sensitivity matrix under multiple excitation profiles;
2. singular-value / condition-number review;
3. pairwise sensitivity-shape correlation;
4. weak-excitation exclusion thresholds;
5. stage-specific parameter allocation;
6. parameter-count limit per fit stage;
7. independent observables used wherever possible.

No model level may fit all available parameters simultaneously to ECT alone.

## Observation priorities

1. engine-out ECT
2. measured oil temperature as an independent slow-thermal observable
3. radiator inlet temperature
4. radiator outlet temperature
5. coolant flow
6. thermostat valve position or command
7. cooling-pack airflow / cell-fan evidence
8. direct metal/head temperatures if available

A new state requires residual evidence, independent observability, or strong sourced constraints.

## Verification requirements

Each executable model level must pass deterministic checks appropriate to its topology:

- energy conservation
- zero-input equilibrium
- state invariants
- radiator effectiveness bounds
- mass-flow continuity
- physically bounded flow split
- zero-flow radiator behavior
- zero-airflow radiator behavior
- pump-off behavior
- solver convergence
- cold-start regression
- hot-start regression
- highway regression
- idle regression
- thermostat-transition regression
- no browser-side governing physics

Dynamic-thermostat hysteresis tests apply only to M3.

## Evidence governance

Consumed V1 evidence may be used for:

- residual diagnosis;
- V2 model-form falsification;
- development parameter studies if explicitly assigned that role.

Consumed V1 evidence may not be used for:

- blind V2 validation;
- post-hoc acceptance-limit selection;
- hidden bound expansion;
- claims that a counterfactual parameter is physically identified.

## Gate V2-2 exit criteria

Model Hierarchy Freeze passes only when:

- [ ] M0, M1, M2, and optional M3 roles are approved
- [ ] vehicle-specific thermostat/control evidence is documented
- [ ] M0/M1 hydraulic flow-split law is frozen
- [ ] airflow evidence policy is frozen
- [ ] promotion thresholds are frozen
- [ ] development/calibration evidence roles are assigned
- [ ] independent V2 validation evidence is reserved
- [ ] M0 parameter table and provenance are frozen
- [ ] M0 synthetic identifiability review is complete

After Gate V2-2, implement and test M0 first. M1 equations are frozen only if M0 is formally promoted. M2 and M3 remain dormant until their promotion criteria are met.
