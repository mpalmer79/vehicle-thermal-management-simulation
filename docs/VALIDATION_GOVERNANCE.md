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

No other parameter may be fitted without an explicit protocol and governance change. Numerical calibration bounds are intentionally not embedded yet. They must be selected and documented before the first controlled Argonne fit rather than invented after observing residuals.

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

## Holdout protection

A holdout manifest cannot declare calibration parameters and cannot authorize a fitting operation. This is enforced by `ValidationRunManifest.assert_parameter_fit_allowed()` rather than relying only on analyst discipline.

The intended controlled sequence is:

1. acquire and archive source files and signal dictionary
2. hash each raw file
3. assign test IDs and roles before fitting
4. build explicit source-to-VTMS signal maps
5. qualify the calibration run
6. fit only the preregistered subset
7. freeze the resulting parameter snapshot and hash
8. execute holdout runs without retuning
9. publish metrics, residuals, warnings, and failures

A failed holdout remains part of the engineering record. It must not be converted into a new calibration run after its results have been inspected.

## Argonne D3 mapping policy

VTMS does not guess Argonne D3 column names, units, file semantics, or optional channels.

`ArgonneD3Adapter` requires a reviewed `ArgonneSignalMap`. The map explicitly names each source column and its source unit. The current adapter supports explicitly mapped CSV only. If the received D3 package uses another format, a dedicated parser must be added after that format is documented.

The template at `validation_configs/argonne_d3_mapping.template.json` is intentionally unresolved and cannot pass adapter validation until every placeholder has been replaced from the received signal dictionary.

Preferred formal heat-input evidence is direct measured fuel rate or fuel-energy rate when available. MAF-derived stoichiometric heat remains secondary plausibility evidence and must not be relabeled as measured fuel.

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

Controlled Argonne calibration and blind holdout validation remain pending receipt and qualification of the requested D3 files and signal dictionary.
