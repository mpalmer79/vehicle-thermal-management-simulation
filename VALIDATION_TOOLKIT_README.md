# VTMS Validation Toolkit V1

## Purpose

This package adds dataset ingestion, comparison metrics, and evidence labeling around the frozen VTMS-V1 simulation engine. It does not modify the governing thermal equations or recalibrate the V1 parameter set.

## Evidence hierarchy

1. **Argonne D3 controlled dynamometer data:** primary planned calibration and blind validation.
2. **KIT Automotive OBD-II Dataset:** secondary external plausibility evidence and validation-pipeline test.
3. **Synthetic VTMS canonical scenarios:** numerical verification and regression only.

Verification, plausibility, calibration, and validation are intentionally kept separate.

## Validation package

`src/vtms_validation/`

- `dataset.py` defines the dataset-independent `ValidationDataset` contract.
- `adapters/kit.py` ingests a full KIT OBD CSV and synchronizes asynchronous PIDs through forward fill after first observation.
- `adapters/normalized.py` loads documented reduced comparison samples.
- `adapters/argonne.py` freezes the required D3 adapter contract but deliberately refuses to guess channel names or units before Argonne supplies the signal dictionary.
- `heat_input.py` contains the explicitly secondary MAF-based heat-input estimator.
- `metrics.py` computes RMSE, MAE, bias, max absolute error, P90 error, final error, and 60/80/90 °C arrival-time error.
- `runner.py` runs a KIT plausibility comparison without mutating VTMS parameters.

## Test status

The combined original VTMS and validation-toolkit suite contains 22 passing tests.

The validation-specific tests verify MAF heat-proxy arithmetic and provenance labeling, metric sign and threshold-crossing behavior, asynchronous KIT PID forward fill and unit conversion, frozen VTMS parameters during KIT comparison, and the Argonne adapter's refusal to invent a schema.

## Current external plausibility result

The first untouched KIT comparison shows that the generic VTMS-V1 warm-up is far too fast for the sampled real-world Seat Leon run. This finding is intentionally preserved and no V1 parameter was changed.

## Argonne handoff

When Argonne D3 data arrive:

1. archive the raw files without modification,
2. record file hashes and D3 test IDs,
3. map official channels and units in `ArgonneD3Adapter`,
4. designate CAL-01 and holdout test IDs according to the preregistered protocol,
5. calibrate only the allowed parameters on CAL-01,
6. freeze the fitted set,
7. run blind holdouts once,
8. publish validation metrics and residual plots regardless of pass/fail.
