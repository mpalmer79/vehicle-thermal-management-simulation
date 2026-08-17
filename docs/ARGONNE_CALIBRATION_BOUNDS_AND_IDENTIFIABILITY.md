# Argonne Calibration Bounds and Identifiability Preregistration

## Status

**Frozen before inspection of VTMS-vs-Argonne residuals. Physical calibration has not started.**

This document records the controlled physical-calibration bounds for VTMS-V1 and the pre-Argonne identifiability decisions that determine how those bounds may be used. The purpose is to prevent residual-driven boundary selection, prevent weakly informed parameters from drifting inside a large optimizer, and make later calibration decisions auditable.

The Argonne source data have been received and qualified. No VTMS prediction residual against CAL-01, CAL-RAD-01, or the reserved holdouts was used to select the bounds or the staged calibration roles in this document.

## Governed calibration universe

The validation protocol permits only four adjustable parameters:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

No other VTMS-V1 parameter may move without a new protocol and governance version. These four parameters form the governed calibration universe. They are not required to move in the same optimizer stage.

## Frozen physical calibration bounds

| Parameter | Lower | Upper | Current generic value |
|---|---:|---:|---:|
| `wall_heat_fraction` | 0.20 | 0.50 | 0.28 |
| `engine_thermal_capacitance_j_per_k` | 25,000 J/K | 100,000 J/K | 50,000 J/K |
| `engine_coolant_ua_w_per_k` | 400 W/K | 2,200 W/K | 1,000 W/K |
| `radiator_ua_nominal_w_per_k` | 400 W/K | 2,200 W/K | 1,100 W/K |

These are engineering bounds for the frozen VTMS-V1 topology, not direct measurements of Ford components. A fitted effective parameter must not be relabeled as a physical mass, local heat-transfer coefficient, or bench-rated radiator constant. The synthetic calibration-harness ranges remain software-test fixtures and are not physical justification.

## Parameter rationale

### Wall heat fraction

Transient gasoline-engine start-up work reports combustion-wall heat transfer as a large term in the start-up energy balance. Those measurements are not identical to the VTMS parameter because V1 collapses multiple engine solids into one state and does not explicitly represent oil, exhaust, or spatial wall temperatures. The frozen 0.20 to 0.50 range therefore brackets the literature scale without equating the effective V1 term to a local wall measurement.

Primary source basis: SAE 2009-01-0613 and SAE 2010-01-1270.

### Effective engine thermal capacitance

Engine warm-up literature uses lumped thermal capacitances or lumped masses. VTMS-V1 is lower order than those models, so its engine capacitance is an effective participating capacitance rather than the heat capacity of the complete engine assembly. The frozen 25 to 100 kJ/K interval spans a factor of four around the generic 50 kJ/K value.

Primary source basis: SAE 910302, SAE 931153, SAE 971852, and SAE 2016-01-0197.

### Engine-to-coolant UA

Detailed engine thermal models resolve coolant-side convection, conduction through engine solids, spatial wall temperatures, and multiple coolant paths. VTMS-V1 compresses that network into one `UA_ec`, so there is no single transferable literature coefficient. The frozen 400 to 2,200 W/K interval permits a large coupling-time-scale correction while remaining finite and positive.

Primary source basis: SAE 931157, SAE 971852, and SAE 2011-01-0647.

### Radiator nominal UA

The V1 radiator is an effectiveness-NTU heat exchanger. Automotive radiator experiments and models show performance depends on core geometry, flow rates, and inlet-air distribution, so a universal passenger-car radiator UA cannot be imported without the exact test hardware. The frozen 400 to 2,200 W/K range is an effective-system interval around the generic 1,100 W/K value.

Primary source basis: SAE 940771 and SAE 2011-01-0647.

## Two complementary synthetic identifiability questions

VTMS runs two different synthetic diagnostics before physical calibration. They answer different questions.

### Broad excitation preflight

`evaluate_synthetic_identifiability()` uses a deliberately rich synthetic profile containing warm-up, thermostat/radiator, vehicle-speed, and fuel-rate changes. It estimates `dT_c/d(log theta)`, normalizes the sensitivity columns, and computes correlation, singular values, and a normalized-Jacobian condition number.

This asks whether the frozen model can create locally distinct coolant-temperature parameter signatures under sufficiently rich excitation. It can detect gross numerical degeneracy, but it does not prove that one physical experiment excites every parameter strongly enough to estimate it.

### Warm-up-stage preflight

`evaluate_warmup_stage_identifiability()` reuses the existing deterministic synthetic calibration and holdout warm-up profiles and applies a 1 percent central fractional perturbation around the generic VTMS-V1 point.

This asks the narrower experimental-design question: **should all four parameters be placed in the same cold-start CAL-01 optimizer stage?**

The combined warm-up profiles are numerically full-rank, with a normalized-matrix condition number of approximately **8.12**. Sensitivity magnitude is the important result:

| Parameter | Combined RMS coolant sensitivity per unit fractional change | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | about 8.39 °C | 100% |
| `engine_thermal_capacitance_j_per_k` | about 2.43 °C | 29% |
| `engine_coolant_ua_w_per_k` | about 4.19 °C | 50% |
| `radiator_ua_nominal_w_per_k` | about 0.079 °C | **0.94%** |

The strongest combined sensitivity-shape relationship is the inverse wall-fraction versus engine-capacitance pair, with cosine approximately **-0.88**.

The 2 percent relative-RMS weak-excitation threshold is a VTMS engineering heuristic, not a statistical confidence criterion or validation limit. Its purpose is to prevent a parameter with negligible leverage from drifting merely because the optimizer can move it.

## Staged calibration decision

The four physical bounds remain frozen and valid for the governed calibration universe, but a four-parameter simultaneous CAL-01 fit is not authorized.

### CAL-01: cold-start warm-up stage

Argonne test `71207062`, UDDS #1 cold start.

Allowed fitted parameters:

- `wall_heat_fraction`: 0.20 to 0.50
- `engine_thermal_capacitance_j_per_k`: 25,000 to 100,000 J/K
- `engine_coolant_ua_w_per_k`: 400 to 2,200 W/K

`radiator_ua_nominal_w_per_k` is fixed during CAL-01.

### CAL-RAD-01: radiator-active stage

Argonne test `71207057`, 1.2 highway x2.

Allowed fitted parameter:

- `radiator_ua_nominal_w_per_k`: 400 to 2,200 W/K

The run was selected from source measurements before any VTMS prediction or residual was inspected. From source time zero through 1287.5 s, ECT is complete at 91 to 99 °C, average dyno speed is approximately 57.31 mph, and approximately 92.65 percent of samples are at or above 40 mph while ECT is at or above 88 °C.

CAL-RAD-01 must use the frozen CAL-01 output snapshot for the three non-radiator parameters and may not reopen them.

## Holdout protection

The staged decision does not consume previously reserved holdouts:

- `VAL-HOT-01`, test 71207063, remains the primary clean independent holdout.
- `VAL-SSS-01`, test 71207052, remains a secondary independent holdout.

Neither run was repurposed after seeing a model residual. No model residual has been inspected for either holdout.

## Interpretation rule

If a calibration returns parameters near bounds, strong covariance, or materially different parameter combinations with similar coolant residuals, VTMS will treat the individual fitted parameters as non-unique effective values. The project will not claim that coolant temperature alone uniquely identifies physical engine mass, wall heat transfer, engine-to-coolant conductance, or radiator conductance.

The correct response to poor identifiability is to add independent observables or stronger physically sourced constraints, not to keep widening bounds until a trace looks good.

## Change-control rule

The four numerical bounds and the two-stage parameter allocation are preregistered before physical residual inspection. Any later change requires a new documented protocol/bounds version, a reason independent of improving an already-observed residual, disclosure that the original preregistration was superseded, and a new immutable calibration manifest before rerunning the affected fit.

The first physical residual from each stage must therefore be preserved even if it is poor.
