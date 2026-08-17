# VTMS Controlled Validation Governance

## Purpose

This document defines the controls that separate plausibility evidence, calibration data, independent holdout validation, and environmental challenge runs for VTMS. It supplements the Physical Validation Protocol and does not change VTMS-V1 physics.

## Evidence roles

Every external-data run must be assigned exactly one role before formal analysis:

- `plausibility`: secondary external evidence used to exercise the pipeline or assess broad physical reasonableness. It cannot establish formal model validity.
- `calibration`: the only role that permits parameter fitting. The permitted fitted subset is preregistered.
- `holdout`: independent validation evidence. Parameter fitting is prohibited.
- `challenge`: intentionally out-of-scope or partially modeled conditions used to expose model limitations. Parameter fitting is prohibited.

The role and evidence grade are coupled in code. A manifest with a mismatched role/evidence grade is invalid.

## Governed calibration universe and frozen bounds

Only these four VTMS-V1 parameters may be adjusted by controlled physical calibration:

1. `wall_heat_fraction`, bound 0.20 to 0.50
2. `engine_thermal_capacitance_j_per_k`, bound 25,000 to 100,000 J/K
3. `engine_coolant_ua_w_per_k`, bound 400 to 2,200 W/K
4. `radiator_ua_nominal_w_per_k`, bound 400 to 2,200 W/K

The numerical intervals were frozen before any VTMS-vs-Argonne residual inspection. They are effective-model engineering bounds, not direct measurements of Ford component properties. Synthetic demonstration bounds remain test-only and are not physical justification.

The complete four-parameter bound set is an audit record for the governed calibration universe. It does **not** authorize all four parameters to move in the same optimizer stage.

## Pre-fit identifiability and staged calibration

Two synthetic diagnostics are used before physical fitting:

1. a broad rich-excitation preflight to detect gross local collinearity or numerical degeneracy,
2. a warm-up-stage diagnostic that asks whether the cold-start CAL-01 experiment materially excites all four parameters.

The warm-up-stage diagnostic is internally generated and cannot accept Argonne data. Its combined synthetic warm-up profiles are full rank, but radiator-UA RMS coolant sensitivity is about 0.94 percent of the strongest parameter sensitivity. The strongest combined sensitivity-shape relationship is wall heat fraction versus effective engine capacitance, cosine about -0.88.

The 2 percent weak-relative-sensitivity threshold is a VTMS engineering heuristic, not a formal statistical criterion. It exists to prevent a weakly informed parameter from moving merely because an optimizer can move it.

As a result, a four-parameter simultaneous CAL-01 fit is prohibited.

### CAL-01

Source test: `71207062`, UDDS #1 cold start.

Authorized parameters:

- `wall_heat_fraction`
- `engine_thermal_capacitance_j_per_k`
- `engine_coolant_ua_w_per_k`

`radiator_ua_nominal_w_per_k` is fixed during this stage.

### CAL-RAD-01

Source test: `71207057`, 1.2 highway x2.

Authorized parameter:

- `radiator_ua_nominal_w_per_k`

The run was selected from source measurements before any VTMS prediction or residual inspection. Its post-zero source record has complete ECT from 91 to 99 C, average dyno speed about 57.31 mph, and about 92.65 percent of samples at or above 40 mph while ECT is at or above 88 C.

CAL-RAD-01 must use the frozen CAL-01 output snapshot for every non-radiator parameter. It may not reopen the CAL-01 parameters.

## Dataset identity and immutability

Every controlled run must record:

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

Received third-party raw validation files remain outside version control unless redistribution terms are explicitly confirmed. The repository stores fingerprints, reviewed mappings, qualification findings, and run manifests.

## Holdout protection

A holdout manifest cannot declare calibration parameters and cannot authorize fitting. Existing holdout reservations remain protected after the staged-calibration decision:

- `VAL-HOT-01`: test 71207063, UDDS #2 hot start
- `VAL-SSS-01`: test 71207052, 55 mph warm-up

Neither may be repurposed for fitting after its model residual is observed.

The controlled sequence is now:

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
15. execute untouched holdouts without retuning
16. publish metrics, residuals, warnings, acceptance decisions, and failures

A failed physical comparison remains part of the engineering record. Bounds or roles may not be widened or rearranged merely to improve an already-observed residual.

## Argonne D3 mapping policy

VTMS does not guess Argonne D3 column names, units, file semantics, or cleanup rules. The received comprehensive files are tab-separated text and provide explicit channels including time, ECT, RPM, dyno speed, cell temperature, and direct bench fuel flow.

`ArgonneD3Adapter` requires a reviewed `ArgonneSignalMap`. Direct volumetric fuel flow is converted to mass flow only with the documented 0.743 g/mL fuel density, and controlled execution still requires an explicitly supplied lower heating value. MAF is not formal controlled heat-input evidence.

Source-time selection and ECT exclusions are explicit reviewed mapping decisions. The adapter does not automatically infer or repair bad ECT samples.

## Measured operating data versus frozen model domain

External measurement files are evidence records. Measured RPM is preserved as nonnegative source evidence even when it lies below the frozen scenario-domain floor. The comparison runner projects nonzero RPM into the frozen 700 to 6500 rpm model domain only at execution and records that projection as preprocessing provenance.

Controlled engine heat comes from direct fuel evidence rather than the generic RPM/load heat estimator.

## Current Argonne role reservations

- `CAL-01`: 71207062, three-parameter cold-start warm-up calibration stage
- `CAL-RAD-01`: 71207057, radiator-UA-only highway calibration stage
- `VAL-HOT-01`: 71207063, independent hot-start holdout
- `VAL-SSS-01`: 71207052, secondary independent holdout
- `VAL-CS-01`: no separate clean cold-start UDDS replicate identified
- `VAL-HWY-01`: 71207065, not qualified for full-cycle ECT validation
- `VAL-US06-01`: 71207066, not qualified for full-cycle ECT validation
- `CHALLENGE-IDLE-CS-01`: 71207072, challenge only

These roles and bounds still do not authorize physical calibration until exact preprocessing and immutable manifests are frozen.

## Project acceptance criteria

These thresholds are VTMS project criteria, not SAE or Argonne standards:

- RMSE <= 5 C
- MAE <= 4 C
- absolute mean bias <= 3 C
- 90th percentile absolute error <= 7 C
- 60/80/90 C arrival error <= 60 s or 10 percent of measured arrival time, whichever is larger

Passing numerical verification remains necessary but is not equivalent to physical validation.

## Current evidence state

VTMS-V1 remains `numerical_verified_generic_uncalibrated`.

The KIT comparison remains `external_plausibility_not_formal_validation` and must not be used to tune VTMS-V1 parameters.

Argonne source acquisition, fingerprinting, physical-bound freeze, synthetic preflight, and staged role allocation are complete. Signal/mapping qualification is being finalized. No Argonne physical calibration or holdout validation result exists yet.
