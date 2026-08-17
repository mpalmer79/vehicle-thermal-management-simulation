# VTMS Controlled Validation Governance

## Purpose

This document defines the controls that separate plausibility evidence, calibration data, independent holdout validation, and environmental challenge runs for VTMS. It supplements the Physical Validation Protocol and does not change VTMS-V1 physics.

## Evidence roles

Every external-data run is assigned exactly one role before formal analysis:

- `plausibility`: secondary external evidence used to exercise the pipeline or assess broad physical reasonableness. It cannot establish formal model validity.
- `calibration`: the only role that permits parameter fitting. The permitted fitted subset is preregistered.
- `holdout`: independent validation evidence. Parameter fitting is prohibited.
- `challenge`: intentionally out-of-scope or partially modeled conditions used to expose model limitations. Parameter fitting is prohibited.

The role and evidence grade are coupled in code. A manifest with a mismatched role/evidence grade is invalid.

## Governed calibration universe and frozen bounds

Only these four VTMS-V1 parameters were eligible for controlled physical calibration:

1. `wall_heat_fraction`, bound 0.20 to 0.50
2. `engine_thermal_capacitance_j_per_k`, bound 25,000 to 100,000 J/K
3. `engine_coolant_ua_w_per_k`, bound 400 to 2,200 W/K
4. `radiator_ua_nominal_w_per_k`, bound 400 to 2,200 W/K

The numerical intervals were frozen before any VTMS-vs-Argonne residual inspection. They are effective-model engineering bounds, not direct measurements of Ford component properties. Synthetic demonstration bounds remain test-only and are not physical justification.

The complete four-parameter bound set is an audit record for the governed calibration universe. It does **not** authorize all four parameters to move in the same optimizer stage.

## Pre-fit identifiability and staged calibration

Two synthetic diagnostics were completed before physical fitting:

1. a broad rich-excitation preflight to detect gross local collinearity or numerical degeneracy,
2. a warm-up-stage diagnostic asking whether the cold-start CAL-01 experiment materially excites all four parameters.

The warm-up-stage diagnostic is internally generated and cannot accept Argonne data. Its combined synthetic warm-up profiles are full rank, but radiator-UA RMS coolant sensitivity is about 0.94 percent of the strongest parameter sensitivity. The strongest combined sensitivity-shape relationship is wall heat fraction versus effective engine capacitance, cosine about -0.88.

The 2 percent weak-relative-sensitivity threshold is a VTMS engineering heuristic, not a formal statistical criterion. It exists to prevent a weakly informed parameter from moving merely because an optimizer can move it.

As a result, a four-parameter simultaneous CAL-01 fit was prohibited.

## Completed calibration stages

### CAL-01: cold-start warm-up

Source test: `71207062`, UDDS #1 cold start.

Authorized fitted parameters:

- `wall_heat_fraction`
- `engine_thermal_capacitance_j_per_k`
- `engine_coolant_ua_w_per_k`

`radiator_ua_nominal_w_per_k` remained fixed during this stage.

CAL-01 met the project calibration-stage numerical thresholds:

- RMSE 3.716 C
- MAE 3.285 C
- mean bias -2.414 C
- P90 absolute error 5.907 C

Its frozen parameter snapshot is `8cef9aa350922a589b9794679c479db643a300842ee0c9c8aebcb517cd145ad2`.

Two fitted effective parameters landed within 1 percent of their frozen upper bounds:

- `wall_heat_fraction` = 0.4999228433
- `engine_coolant_ua_w_per_k` = 2198.4326 W/K

`engine_thermal_capacitance_j_per_k` fitted to 52393.9078 J/K. These are effective VTMS-V1 lumped parameters and are not uniquely identified physical Ford component properties.

### CAL-RAD-01: radiator-active highway

Source test: `71207057`, 1.2 highway x2.

Authorized fitted parameter:

- `radiator_ua_nominal_w_per_k`

All CAL-01 parameters remained frozen. The radiator-stage source was selected from measured operating conditions before its VTMS residual was inspected.

CAL-RAD-01 failed the core project calibration criteria:

- RMSE 5.733 C
- MAE 5.344 C
- mean bias -5.272 C
- P90 absolute error 8.124 C

Radiator UA fitted to 400.8325 W/K, within 1 percent of the frozen 400 W/K lower bound. The bound was not widened and CAL-01 parameters were not reopened.

The final staged parameter snapshot is `ae983fdbc636cc4d7e597bc22108e47a5833960761d16bb6e38e30bc5784c287`.

## Dataset identity and immutability

Every controlled run records:

- dataset ID
- source file name and SHA-256
- file size
- model ID/version and equation set
- parameter-set identifier and exact parameter-snapshot SHA-256
- validation role and evidence grade
- fitted-parameter declaration for calibration runs only
- frozen bound set applicable to that stage
- preprocessing/mapping provenance
- acceptance criteria

If a source file changes by one byte, it is a different provenance artifact.

Received third-party raw validation files remain outside version control unless redistribution terms are explicitly confirmed. The repository stores fingerprints, reviewed mappings, qualification findings, manifests, and derived result records.

## Holdout protection and completed primary holdout

The holdout roles were reserved before physical fitting:

- `VAL-HOT-01`: test 71207063, UDDS #2 hot start
- `VAL-SSS-01`: test 71207052, 55 mph warm-up

A holdout manifest cannot declare calibration parameters and cannot authorize fitting. Neither holdout may be repurposed for fitting after its model residual is observed.

### VAL-HOT-01 formal result

The primary hot-start holdout was opened only after the final staged parameter snapshot, source fingerprint, preprocessing map, and holdout manifest were frozen. It was evaluated once with no parameter fitting.

Formal result:

- RMSE 8.587 C, limit 5 C: FAIL
- MAE 8.069 C, limit 4 C: FAIL
- absolute mean bias 8.037 C, limit 3 C: FAIL
- P90 absolute error 10.051 C, limit 7 C: FAIL
- 60 C arrival timing: NOT_EVALUABLE because the measured trace begins above 60 C
- 80 C arrival timing: NOT_EVALUABLE because the measured trace begins above 80 C
- 90 C arrival error 125.6 s, limit 60 s: FAIL

The final measured coolant temperature is 99.0 C and the frozen model predicts 90.47 C, an error of -8.53 C.

Formal decision: `formal_holdout_acceptance_fail`.

**VTMS-V1 did not pass the preregistered controlled physical validation criteria.** The failed holdout remains part of the engineering record. It does not authorize post-hoc retuning, bound expansion, role reassignment, or reuse of the holdout as calibration data.

## Threshold-arrival observation-window rule

Before VAL-HOT-01 was opened, the acceptance evaluator was clarified so an arrival-time criterion is `NOT_EVALUABLE` when the measured trace begins at or above that threshold. In that situation, the physical crossing occurred before the observation window and a zero-second timing error would be artificial.

This clarification was made after CAL-RAD-01 exposed the issue on its already-hot calibration trace but before the primary holdout source was opened. It did not change the CAL-RAD-01 outcome because that stage already failed all four core temperature criteria.

## Controlled sequence and completion state

The governed sequence was:

1. acquire and archive source files and documentation
2. hash each raw artifact
3. inspect measurement quality without model residuals
4. assign source roles before fitting
5. build explicit source-to-VTMS mappings
6. freeze physical bounds
7. run synthetic pre-fit identifiability diagnostics
8. freeze staged calibration roles
9. freeze CAL-01 mapping, preprocessing, baseline parameter snapshot, bounds subset, and immutable manifest
10. execute CAL-01 on only its three declared parameters
11. freeze the CAL-01 output snapshot
12. freeze CAL-RAD-01 mapping and immutable radiator-only manifest
13. execute CAL-RAD-01 without reopening CAL-01 parameters
14. freeze the final staged parameter snapshot
15. freeze the primary holdout source, preprocessing, and parameter locks
16. execute the untouched primary holdout without retuning
17. publish metrics, residuals, warnings, acceptance decisions, and failures

Steps 1 through 16 are complete for the primary validation path. Reporting is active. The secondary preregistered holdout remains available for confirmatory evidence, but it cannot change the failed primary formal decision and cannot be used for fitting.

## Argonne D3 mapping policy

VTMS does not guess Argonne D3 column names, units, file semantics, or cleanup rules. The received comprehensive files are tab-separated text and provide explicit channels including time, ECT, RPM, dyno speed, cell temperature, and direct bench fuel flow.

`ArgonneD3Adapter` requires a reviewed `ArgonneSignalMap`. Direct volumetric fuel flow is converted to mass flow only with the documented 0.743 g/mL fuel density, and controlled execution still requires an explicitly supplied lower heating value. MAF is not formal controlled heat-input evidence.

Source-time selection and ECT exclusions are explicit reviewed mapping decisions. The adapter does not automatically infer or repair bad ECT samples.

## Measured operating data versus frozen model domain

External measurement files are evidence records. Measured RPM is preserved as nonnegative source evidence even when it lies below the frozen scenario-domain floor. The comparison runner projects nonzero RPM into the frozen 700 to 6500 rpm model domain only at execution and records that projection as preprocessing provenance.

Controlled engine heat comes from direct fuel evidence rather than the generic RPM/load heat estimator.

## Project acceptance criteria

These thresholds are VTMS project criteria, not SAE or Argonne standards:

- RMSE <= 5 C
- MAE <= 4 C
- absolute mean bias <= 3 C
- 90th percentile absolute error <= 7 C
- 60/80/90 C arrival error <= 60 s or 10 percent of measured arrival time, whichever is larger, when the measured crossing occurs inside the observation window

Passing numerical verification remains necessary but is not equivalent to physical validation.

## Current evidence state

The production/default VTMS-V1 parameter set remains the generic V1 set and has not been silently replaced by the Argonne-calibrated validation artifact.

The KIT comparison remains `external_plausibility_not_formal_validation` and is not calibration evidence.

The controlled Argonne staged calibration has been completed and frozen. The primary independent physical holdout has been executed with no fitting and failed the formal acceptance criteria. VTMS-V1 therefore has **not passed controlled physical validation**.

The correct next engineering response is model-form investigation under a new governed revision, not holdout-driven retuning of VTMS-V1.
