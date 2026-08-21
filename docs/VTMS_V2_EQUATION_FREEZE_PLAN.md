# VTMS-V2 Equation Freeze Plan

## Purpose

This document defines the work required to pass **Gate V2-2: Equation Freeze** before any VTMS-V2 simulation engine is implemented.

The gate exists to prevent residual-driven coding. VTMS-V2 must have a frozen state vector, governing equations, constitutive laws, units, domains, initialization rules, and calibration roles before physical implementation or fitting begins.

## Frozen candidate state vector

The Phase 1 and Phase 2 evidence supports the following five-state candidate architecture:

```text
x = [T_head, T_block, T_hot, T_cold, x_th]
```

where:

- `T_head` is a fast effective engine-structure temperature
- `T_block` is a slower effective engine-structure temperature
- `T_hot` is engine-out / ECT-side coolant temperature
- `T_cold` is radiator-return / pump-inlet coolant temperature
- `x_th` is normalized thermostat actuator state in `[0, 1]`

The five-state choice is frozen as the design target for equation review, but no V2 parameter values are frozen by this document.

## Proposed energy equations for review

### Fast engine structure

```text
C_head dT_head/dt = Q_head
                       - UA_head_hot (T_head - T_hot)
                       - UA_head_block (T_head - T_block)
                       - Q_head_ambient
```

### Slow engine structure

```text
C_block dT_block/dt = Q_block
                        + UA_head_block (T_head - T_block)
                        - UA_block_hot (T_block - T_hot)
                        - Q_block_ambient
```

### Engine-out / hot coolant control volume

```text
C_hot dT_hot/dt = Q_head_hot
                    + Q_block_hot
                    + m_dot_bypass cp (T_cold - T_hot)
                    + m_dot_rad cp (T_cold - T_hot)
                    + Q_hot_aux
```

The final sign convention and mass-flow transport formulation must be reviewed carefully. The equation above is a control-volume design placeholder, not yet an implementation authorization.

### Radiator-return / cold coolant control volume

```text
C_cold dT_cold/dt = m_dot_rad cp (T_rad_out - T_cold)
                      + m_dot_bypass cp (T_hot - T_cold)
                      + Q_cold_aux
```

A cleaner transport formulation may instead model the radiator branch and bypass branch as inlet enthalpy terms with explicit outlet mixing. The final form must conserve energy numerically and avoid double-counting coolant transport.

### Thermostat state

```text
tau_th dx_th/dt = x_cmd(T_hot, direction) - x_th
```

with:

```text
0 <= x_th <= 1
```

and separate opening/closing command laws to represent hysteresis.

## Heat input partition

Fuel energy remains grounded in direct fuel evidence when available:

```text
Q_fuel = m_dot_fuel LHV
```

The constant V1 wall-heat fraction is replaced by a bounded low-order partition:

```text
eta_head = f_head(rpm, load, thermal_state)
eta_block = f_block(rpm, load, thermal_state)

Q_head = eta_head Q_fuel
Q_block = eta_block Q_fuel
```

The first V2 equation freeze must choose one explicit functional form. Candidate forms should be compared on identifiability and physical interpretability before selection.

No machine-learned residual correction is permitted in the first V2 physics implementation.

## Coolant hydraulic network

V2 must not reuse the V1 identity:

```text
radiator_flow_fraction = thermostat_opening_fraction
```

The equation freeze must select one of two permitted low-order approaches.

### Option A: branch-resistance solution

```text
DeltaP_rad(m_dot_rad, x_th) = DeltaP_bypass(m_dot_bypass, x_th)
m_dot_pump = m_dot_rad + m_dot_bypass
```

This is preferred if physically defensible resistance coefficients can be constrained.

### Option B: bounded monotonic flow-split law

```text
f_rad = g(x_th, m_dot_pump)
m_dot_rad = f_rad m_dot_pump
m_dot_bypass = (1 - f_rad) m_dot_pump
```

This is acceptable for the first V2 implementation only if `g` is monotonic, bounded, auditable, and not fitted freely to consumed holdout traces.

## Pump model

The V1 RPM-based pump-flow law may be retained temporarily as a candidate upstream boundary if it passes V2 sensitivity review.

Before equation freeze, classify pump parameters as one of:

- sourced/fixed
- engineering-assumed/fixed
- calibratable under a new V2 protocol

Do not allow pump flow, thermostat flow split, and radiator conductance to become simultaneous unconstrained compensators.

## Radiator model

The effectiveness-NTU framework may be retained, but nominal UA becomes flow dependent.

Candidate low-order law:

```text
UA_rad = UA_ref
         (m_dot_air / m_dot_air_ref)^a_air
         (m_dot_cool / m_dot_cool_ref)^a_cool
```

Required constraints:

- `UA_ref > 0`
- bounded nonnegative exponents unless physical evidence justifies otherwise
- defined behavior at near-zero flow
- no discontinuity at fan/ram transitions
- preserve thermodynamic effectiveness bounds

The radiator metal thermal mass remains excluded from the initial V2 state vector unless residual reconstruction or independent measurements establish a need for it.

## Airflow boundary model

V2 must separate three concepts:

```text
road vehicle speed
chassis/dyno speed
radiator-core air mass flow
```

The equation freeze must define how each evidence class supplies air flow.

### Road simulation

A vehicle-speed-to-core-flow surrogate may be used if it is explicitly identified as a vehicle-level approximation.

### Chassis-dyno validation

Dyno speed must not silently become radiator face velocity. Acceptable inputs are:

- measured cooling-pack airflow
- documented cell-fan command mapped through a frozen transfer law
- a preregistered surrogate with uncertainty bounds

If only dyno speed is available, the airflow assumption must be treated as a model/input uncertainty source rather than hidden inside radiator UA.

## ECT observation equation

The initial V2 observation model should be:

```text
ECT_pred = T_hot
```

A sensor lag or sensor-location correction may be added only if supported by source documentation or independent measurement evidence.

The observation equation must remain separate from the governing coolant physics.

## Initial-state policy

V2 must support three governed initialization modes.

### Cold soak

```text
T_head ~= T_block ~= T_hot ~= T_cold ~= ambient
```

with documented tolerances.

### State carryover

All five states are carried from a preceding simulated segment or soak.

### State estimation

Unobserved thermal states may be estimated from pre-observation history under a frozen estimator. Blind holdout residuals may not be used to fit their own initial conditions.

## Candidate parameter classes

### Thermal capacities

- `C_head`
- `C_block`
- `C_hot`
- `C_cold`

### Structure-to-structure / structure-to-coolant conductances

- `UA_head_hot`
- `UA_head_block`
- `UA_block_hot`
- engine-to-ambient terms if retained

### Thermostat dynamics

- opening threshold/shape parameters
- closing threshold/shape parameters
- `tau_th`

### Hydraulic parameters

- pump-flow coefficients
- radiator-branch resistance coefficients or flow-split coefficients
- bypass-branch resistance coefficients or flow-split coefficients

### Radiator parameters

- `UA_ref`
- `a_air`
- `a_cool`
- reference air and coolant flows

### Heat-partition parameters

- coefficients for `eta_head`
- coefficients for `eta_block`

The equation freeze must classify each candidate as fixed, sourced, assumed, derived, or calibratable.

## Identifiability constraints

The initial V2 calibration program must not fit every parameter simultaneously to ECT.

Required pre-fit work:

1. structural identifiability review of the frozen equations
2. synthetic sensitivity matrix across candidate experiments
3. parameter-correlation analysis
4. stage-specific excitation review
5. explicit weak-sensitivity exclusion rules
6. parameter-count limit per calibration stage

Where possible, physical/source constraints should replace optimization freedom.

## Observation priorities

Additional observables should be ranked as follows:

1. engine-out ECT
2. radiator inlet temperature
3. radiator outlet temperature
4. coolant flow rate
5. thermostat position or command
6. cooling-pack airflow or cell-fan evidence
7. oil temperature if an oil state is reconsidered
8. metal/head temperature if available

A new state should not be added solely because it is physically plausible. It should have residual evidence, independent observability, or a strong sourced constraint.

## Verification requirements before physical calibration

The V2 engine must pass at least the following deterministic verification classes:

- energy conservation for closed/no-loss configurations
- zero-input equilibrium
- state invariants and bounded thermostat state
- radiator effectiveness bounds
- mass-flow continuity at bypass/radiator mixing
- monotonic thermostat command behavior
- thermostat hysteresis direction tests
- zero-flow radiator behavior
- zero-airflow radiator behavior
- pump-off behavior
- solver convergence under step refinement
- regression scenarios for cold start, hot start, highway, idle, fan-on, and thermostat transitions
- no hidden browser-side governing physics

## Calibration governance

Consumed V1 evidence may be used for:

- model-form design
- sensitivity development
- preliminary V2 calibration if explicitly reclassified as development evidence

Consumed V1 evidence may not be used for:

- a new claim of blind V2 validation
- threshold selection after seeing V2 residuals
- hidden parameter-bound widening

A new V2 validation plan must reserve independent tests before V2 physical fitting begins.

## Gate V2-2 exit criteria

Equation Freeze passes only when all of the following are complete:

- [ ] exact five-state ODE system approved
- [ ] coolant transport/mixing equations energy-balanced
- [ ] thermostat hysteresis law frozen
- [ ] branch-flow law frozen
- [ ] radiator-UA flow law frozen
- [ ] airflow evidence policy frozen
- [ ] heat-partition law frozen
- [ ] ECT observation equation frozen
- [ ] initialization modes frozen
- [ ] complete parameter table with units and domains
- [ ] parameter provenance classifications assigned
- [ ] preliminary calibration roles assigned
- [ ] synthetic identifiability plan approved
- [ ] independent V2 validation evidence reserved

Until this checklist passes, VTMS-V2 remains a governed model-design program rather than an executable validated model.
