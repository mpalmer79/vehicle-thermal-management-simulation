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

## Frozen calibration subset

The controlled calibration subset is:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

No other parameter may be fitted without an explicit protocol and governance change. Numerical calibration bounds are intentionally not embedded yet. They must be selected, physically justified, documented, and frozen before the first controlled Argonne fit rather than invented after observing residuals.

Synthetic demonstration bounds are test-only and must not be reused as Argonne physical calibration bounds.

## Dataset identity and immutability

Every controlled run must record:

- dataset ID
- source file name
- SHA-256 hash of the exact source file
- file size
- model ID and model version
- equation set
- parameter set
- SHA-256 hash of the exact parameter snapshot
- validation role
- evidence grade
- fitted-parameter declaration, if and only if the run is calibration
- acceptance criteria

If the source file changes by even one byte, it is a different dataset artifact for provenance purposes.

Received third-party raw validation files are kept outside version control unless redistribution terms are explicitly confirmed. The repository stores fingerprints, reviewed mappings, qualification findings, and run manifests.

## Holdout protection

A holdout manifest cannot declare calibration parameters and cannot authorize a fitting operation. This is enforced by `ValidationRunManifest.assert_parameter_fit_allowed()` rather than relying only on analyst discipline.

The controlled sequence is:

1. acquire and archive source files and source documentation
2. hash each raw artifact
3. inspect source data quality without model residuals
4. assign test IDs and roles before fitting
5. build explicit source-to-VTMS signal maps and preprocessing declarations
6. freeze physically justified calibration bounds
7. qualify the calibration run
8. fit only the preregistered subset
9. freeze the resulting parameter snapshot and hash
10. execute holdout runs without retuning
11. publish metrics, residuals, warnings, and failures

A failed holdout remains part of the engineering record. It must not be converted into a new calibration run after its results have been inspected.

## Argonne D3 mapping policy

VTMS does not guess Argonne D3 column names, units, file semantics, or cleanup rules.

Argonne supplied the requested 2012 Ford Focus material on 2026-08-17. The received comprehensive test files are tab-separated text and provide the reviewed channels needed by VTMS:

- `Time [s]`
- `EngineCoolantTemp[C]`
- `Eng_Spd[RPM]`
- `Dyno_Spd[mph]`
- `Cell_Temp[C]`
- `Eng_FuelFlow_Direct[cc/s]`

`ArgonneD3Adapter` requires a reviewed `ArgonneSignalMap`. The map explicitly names every source column and unit. The adapter now supports explicitly mapped CSV, TSV, and delimited text files because the received D3 package documents that format.

The direct fuel-flow source is volumetric. The included Argonne master summary reports a fuel density of 0.743 g/mL, so the adapter may convert `cc/s` to `kg/s` only when that density is explicitly declared in the mapping metadata. Controlled execution still requires the fuel lower heating value to be explicitly supplied to the runner.

The adapter also supports explicit source-time start/end selection and explicit exclusion intervals. It does not infer invalid ECT values and does not silently clean a trace. Every removed interval must be declared in the reviewed map and is recorded in normalized dataset metadata.

The detailed qualification record is `docs/ARGONNE_D3_DATA_QUALIFICATION.md`.

Preferred formal heat-input evidence is direct measured fuel rate or fuel-energy rate when available. MAF-derived stoichiometric heat remains secondary plausibility evidence and must not be relabeled as measured fuel. The received comprehensive MAF channel contains impossible spikes in several tests and is not used for controlled heat input.

## Measured operating data versus frozen model domain

External measurement files are evidence records and may contain measured operating values outside the frozen VTMS-V1 scenario input domain. `ValidationDataset` therefore validates measured RPM as nonnegative evidence rather than forcing the evidence into the model domain.

At comparison execution, the runner projects nonzero measured RPM into the frozen 700 to 6500 rpm `Scenario` reference domain and records the projection in `input_preprocessing_metadata`. The raw dataset values remain unchanged.

For the current controlled-validation path, engine heat comes from direct fuel evidence through `engine_heat_override_w`, not from the generic RPM/load heat estimator. The RPM projection therefore exists only to keep the measured operating profile compatible with the frozen V1 component-model boundary.

## Current Argonne role reservations

Role reservations were made from Argonne test documentation and source-signal quality before any VTMS residual was inspected.

- `CAL-01`: 71207062, UDDS #1 cold start, calibration candidate after explicit ECT quality selection.
- `VAL-HOT-01`: 71207063, UDDS #2 hot start, independent holdout candidate.
- `VAL-SSS-01`: 71207052, 55 mph warm-up, secondary independent holdout candidate reserved before fit.
- `VAL-CS-01`: no separate clean cold-start UDDS replicate identified in the received package.
- `VAL-HWY-01`: 71207065, not qualified for full-cycle ECT validation because the received ECT channel becomes unavailable early.
- `VAL-US06-01`: 71207066, not qualified for full-cycle ECT validation because the received ECT channel becomes unavailable early.
- `CHALLENGE-IDLE-CS-01`: 71207072, cold-start idle/no-fan challenge candidate with partial ECT coverage.

These reservations do not authorize calibration. Physical calibration bounds remain unresolved and must be frozen first.

## Project acceptance criteria

These thresholds are VTMS project criteria, not SAE or Argonne standards:

- RMSE <= 5 C
- MAE <= 4 C
- absolute mean bias <= 3 C
- 90th percentile absolute error <= 7 C
- 60/80/90 C arrival error <= 60 s or 10 percent of the measured arrival time, whichever is larger

Passing numerical verification remains necessary but is not equivalent to physical validation.

## Current evidence state

VTMS-V1 remains `numerical_verified_generic_uncalibrated`.

The KIT comparison remains `external_plausibility_not_formal_validation` and must not be used to tune VTMS-V1 parameters.

Argonne D3 source acquisition and fingerprinting are complete. Signal mapping and data qualification are in progress. Controlled Argonne calibration has not started, and no physical holdout result exists yet.
