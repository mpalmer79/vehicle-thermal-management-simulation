# VTMS-V2 Phase 2 Residual Diagnostics

## Status

**Phase 2 diagnostic framework implemented. Full Argonne time-series reconstruction remains data-gated because raw Argonne source attachments are intentionally not redistributed in the repository and were not recoverable from the current project file library.**

This document records what can be concluded from the frozen VTMS-V1 controlled-calibration and holdout result records, what additional time-series diagnostics are now implemented, and which V2 model-form decisions are supported strongly enough to retain before any V2 fitting occurs.

No VTMS-V1 parameter is changed by this work. No consumed V1 holdout is relabeled as blind V2 validation evidence.

## Evidence available for Phase 2

The following frozen V1 records are the authoritative evidence base:

- `ARGONNE_CAL_01_FORMAL_RESULT.json`
- `ARGONNE_CAL_RAD_01_FORMAL_RESULT.json`
- `ARGONNE_VAL_HOT_01_FORMAL_RESULT.json`
- `ARGONNE_VAL_SSS_01_CONFIRMATORY_RESULT.json`
- KIT external plausibility records
- frozen V1 model equations and component implementations

The repository preserves metrics, model snapshots, source fingerprints, mappings, and evidence roles. It does not preserve the raw Argonne test attachments or full Argonne residual vectors.

## Aggregate residual decomposition

For residual `r = predicted - measured`, the mean-squared error may be decomposed as:

```text
MSE = bias^2 + residual variance
```

The ratio `bias^2 / MSE` is therefore useful for determining whether a failed comparison is dominated by a systematic offset or by zero-mean transient scatter.

### CAL-01

- RMSE: 3.71596 C
- mean bias: -2.41373 C
- bias contribution to MSE: approximately 42.2%
- final error: -4.63117 C
- wall heat fraction: 0.4999228, essentially the frozen upper bound
- engine-to-coolant UA: 2198.43 W/K, essentially the frozen upper bound

Interpretation: CAL-01 can reproduce threshold timing and meet project calibration thresholds, but it does so while using two nearly boundary-saturated effective parameters. The remaining error is not purely an offset. The fit still requires a mixture of dynamic and systematic correction.

### CAL-RAD-01

- RMSE: 5.73268 C
- mean bias: -5.27227 C
- bias contribution to MSE: approximately 84.6%
- final error: -5.12369 C
- radiator UA: 400.8325 W/K, essentially the frozen lower bound

Interpretation: radiator-active operation is dominated by systematic underprediction even after radiator conductance is minimized within the preregistered V1 bounds. This strongly rejects the hypothesis that a single constant radiator UA can reconcile the V1 topology with this operating region.

### VAL-HOT-01

- RMSE: 8.58744 C
- mean bias: -8.03750 C
- bias contribution to MSE: approximately 87.6%
- final error: -8.52745 C
- 90 C arrival error: +125.6 s late

Interpretation: the primary independent holdout is overwhelmingly dominated by a persistent cold bias. The error is too systematic to describe as solver noise or localized transient mismatch. Because the error persists to the end of a 1374 s run, incorrect hot-start initialization cannot be the sole cause.

### VAL-SSS-01

- RMSE: 5.12590 C
- mean bias: -4.01470 C
- bias contribution to MSE: approximately 61.3%
- 80 C arrival error: +17.3 s
- 90 C arrival error: +23.8 s
- final error: -8.42266 C

Interpretation: the secondary holdout reaches 80 C and 90 C at approximately the correct time, then finishes more than 8 C too cold. This is the strongest aggregate evidence that the principal failure is not simply global warm-up time constant. V1 enters the regulated hot region plausibly and then establishes the wrong thermal equilibrium/control behavior.

## Cross-run structural contradiction

The staged calibration results create a physically revealing contradiction inside the V1 topology:

1. Cold-start CAL-01 drives heat addition/coupling upward:
   - wall heat fraction approximately maximum
   - engine-to-coolant UA approximately maximum
2. Radiator-active CAL-RAD-01 drives heat rejection downward:
   - radiator UA approximately minimum
3. The independent hot-region holdouts remain too cold by approximately 8 C.

A correctly structured two-state model should not require simultaneous boundary pressure in opposite energy-balance directions and still miss the regulated temperature by this magnitude.

The evidence supports model-form revision rather than wider V1 bounds.

## V2 requirements retained after Phase 2 review

### R1: Separate engine-out and radiator-return coolant states

**Status: retain, very high confidence.**

V1 uses one bulk coolant state both as the engine coolant temperature and radiator inlet temperature. This prevents representation of spatial temperature lift through the engine and temperature drop through the radiator. It also forces the measured ECT target to represent total-system bulk coolant rather than a sensor-local hot-side state.

V2 retains:

- `T_hot`: engine-out / ECT-side coolant state
- `T_cold`: radiator-return / pump-inlet coolant state

The ECT observation equation should initially compare measured ECT to `T_hot` or to a documented sensor model derived from `T_hot`.

### R2: Dynamic thermostat state with hysteresis

**Status: retain, very high confidence.**

VAL-SSS-01 strongly localizes failure to the thermostat/radiator regulation region. V1's instantaneous linear thermostat command cannot represent actuator lag, hysteresis, or temperature history.

V2 retains an explicit bounded thermostat state `x_th` governed by a first-order response law and separate opening/closing command curves.

### R3: Decouple thermostat position from radiator-flow fraction

**Status: retain, very high confidence.**

V1 assumes radiator mass-flow fraction equals thermostat opening fraction exactly. This is not a hydraulic solution. V2 must use a nonlinear branch-flow model in which radiator and bypass flows are functions of valve state and circuit resistance.

A full pressure-network model is preferred if the required coefficients can be physically constrained. A lower-order monotonic flow-split law is acceptable for the first V2 implementation if its limitations are explicit.

### R4: Cooling-pack airflow is an independent boundary condition

**Status: retain, high confidence.**

The controlled Argonne mapping currently feeds chassis-dyno speed to the V1 vehicle-speed input, and V1 converts vehicle speed directly into ram-air flow through a geometric capture coefficient. Chassis speed is not itself radiator-core face velocity.

V2 must separate:

- road vehicle speed
- chassis/dyno speed
- test-cell fan or cooling-pack airflow boundary

If core airflow is not measured, the surrogate and its uncertainty must be explicit. Radiator UA must not be allowed to silently absorb an unqualified airflow boundary.

### R5: Flow-dependent radiator conductance

**Status: retain, high confidence.**

The CAL-RAD-01 boundary result rejects a single constant effective radiator UA as an adequate description across V1 operating conditions. V2 should parameterize `UA_rad` as a bounded function of coolant and air mass flow rather than a single constant.

The first V2 formulation should remain low order, for example a reference UA with bounded coolant-side and air-side scaling exponents. Additional complexity requires independent evidence.

### R6: Two engine-structure thermal states

**Status: retain, high confidence for transient behavior.**

The KIT plausibility comparison warmed far too quickly but converged near the measured final region. CAL-01 also requires near-maximum wall heat fraction and engine-to-coolant coupling. These patterns are consistent with one effective engine thermal capacitance being forced to reproduce multiple physical time scales.

V2 retains:

- `T_head`: faster combustion-facing/head structure
- `T_block`: slower structural storage

The two states must not be interpreted as literal homogeneous Ford components unless independently identified.

### R7: Operating-dependent heat partition

**Status: retain as a governed candidate, high confidence that constant partition is restrictive; lower confidence in exact functional form.**

V1 applies one wall heat fraction to direct fuel energy across every operating point. V2 should allow heat-to-structure/coolant partition to depend on measured operating conditions through a low-order bounded function.

The functional form must be preregistered before calibration. A neural correction model is prohibited for the initial V2 physics program.

### R8: State-aware initialization

**Status: retain, high confidence for hot-start transient accuracy.**

V1 initializes unobserved engine temperature equal to measured coolant temperature unless explicitly overridden. Hot-start tests do not guarantee thermal equilibrium between coolant and all engine structures.

V2 must support cold-soak initialization, prior-cycle state carryover, and a governed state-estimation path. Initial-state fitting to a blind validation trace is prohibited.

## What Phase 2 does not yet establish

Without the full controlled residual vectors, the following questions remain unresolved:

1. Exact residual correlation with engine RPM.
2. Exact residual correlation with direct fuel-energy rate.
3. Exact residual correlation with engine load.
4. Exact residual correlation with dyno speed.
5. Whether residual changes exhibit hysteresis across thermostat opening versus closing trajectories.
6. Whether the hot-region error is load-step dependent or approximately constant under similar ECT.
7. Whether the CAL-RAD residual is primarily explained by cooling-pack airflow, thermostat/bypass hydraulics, or radiator conductance dependence.
8. Whether additional radiator thermal mass is justified.
9. Whether an explicit oil state is identifiable or necessary after the two-structure-node revision.

These questions must remain open rather than being inferred from aggregate metrics.

## Implemented diagnostic harness

`src/vtms_validation/residual_diagnostics.py` adds deterministic, no-fit diagnostics for an already-generated comparison trace.

It reports:

- mean residual
- MAE
- RMSE
- maximum absolute residual
- bias fraction of MSE
- positive/negative residual fractions
- residual metrics by measured-coolant-temperature bin
- residual metrics across the thermostat transition region
- Pearson residual correlation against available measured operating channels

Supported correlation inputs are:

- measured coolant temperature
- engine speed
- vehicle/dyno speed
- fuel-energy rate
- engine load

The diagnostic function does not optimize, refit, mutate, or authorize any parameter change.

## Required full-trace execution when Argonne source is locally available

For each consumed V1 controlled run, reconstruct the frozen comparison with its original source fingerprint, preprocessing mapping, parameter snapshot, and no-fit rules, then pass the resulting arrays to the diagnostic harness.

Minimum output set per run:

1. `residual_vs_time.csv`
2. `residual_vs_temperature.csv`
3. `residual_diagnostics.json`
4. residual-vs-fuel-energy correlation
5. residual-vs-RPM correlation
6. residual-vs-speed correlation
7. thermostat-transition summary
8. regulated-region summary for measured ECT >= 88 C

Consumed V1 holdouts may be used for V2 model-form diagnosis because their blind role has already been consumed. They may not later be relabeled as independent V2 validation evidence.

## Phase 2 decision

The currently available evidence is sufficient to retain the proposed five-state V2 topology:

```text
x = [T_head, T_block, T_hot, T_cold, x_th]
```

It is not sufficient to freeze all V2 parameter values or all constitutive-law forms.

Before V2 physical calibration begins, the project must still freeze:

- the exact two-structure-node energy equations
- hot/cold coolant control-volume equations
- thermostat dynamic/hysteresis law
- radiator/bypass hydraulic law
- airflow-boundary policy
- flow-dependent radiator-UA law
- heat-partition functional form
- initial-state policy
- V2 calibration parameter subset and physical bounds
- new V2 blind validation tests that have not been consumed by V1 model development

## Next development gate

**Gate V2-2: Equation Freeze.**

The next implementation step is to draft and review the exact VTMS-V2 governing equations and parameter table. V2 simulation code should not be written until those equations, units, sign conventions, domains, and calibration roles are frozen in a versioned engineering-model specification.
