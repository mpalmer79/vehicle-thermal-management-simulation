# VTMS-V2 Full-Trace Execution Record

## Status

**Complete for the four consumed controlled VTMS-V1 Argonne runs.**

The original Argonne archives were recovered from the project file library. Target source files matched the SHA-256 identities frozen before their original V1 executions. The V1 comparisons were reconstructed under the same model equations, reviewed mappings, direct-fuel-energy treatment, parameter snapshots, and no-retuning semantics.

This record is VTMS-V2 development evidence only. It does not modify the preserved VTMS-V1 formal results and does not restore blind status to any consumed holdout.

Raw Argonne files and reconstructed row-level traces are not committed.

## Source identity

| Run | Source test | Source SHA-256 |
|---|---:|---|
| CAL-01 | 71207062 | `4065b06eedefa5728ac6b8cb7c268f5f354021cf8bd98bf204dbdfcd74985e09` |
| CAL-RAD-01 | 71207057 | `57034f3e01e45bae7271cc4f96d3b7eb88055e17bb1bf3522e28c6734b631e3d` |
| VAL-HOT-01 | 71207063 | `8a1953112752e35ade720ab9a64201b05b37c70d172839234f12504e68f2aa8d` |
| VAL-SSS-01 | 71207052 | `b5a837449f824ad76b00a6ab7da7ae92486b4feec0b4e3a81eb126bac14b0f02` |

Each recovered hash matched its previously frozen expected value.

## Reconstruction environment

The local reconstruction environment matched the versions recorded in the formal controlled results:

- Python 3.13.5
- NumPy 2.3.5
- SciPy 1.17.0

The relevant local VTMS-V1 physics modules were checked against the repository implementation. The governing behavior matched the frozen V1 model used by the controlled program.

## Metric reproduction

| Run | Rows | Duration s | Reconstructed RMSE C | Frozen RMSE C | RMSE delta C |
|---|---:|---:|---:|---:|---:|
| CAL-01 | 13,638 | 1365.3 | 3.71784 | 3.71596 | +0.00188 |
| CAL-RAD-01 | 12,876 | 1287.5 | 5.73802 | 5.73268 | +0.00534 |
| VAL-HOT-01 | 13,741 | 1374.0 | 8.58427 | 8.58744 | -0.00317 |
| VAL-SSS-01 | 4,462 | 446.1 | 5.12995 | 5.12590 | +0.00406 |

Additional reconstructed metrics:

| Run | MAE C | Bias C | P90 abs C | Final error C | Bias fraction of MSE |
|---|---:|---:|---:|---:|---:|
| CAL-01 | 3.28596 | -2.41678 | 5.91005 | -4.62701 | 42.3% |
| CAL-RAD-01 | 5.35303 | -5.28135 | 8.11106 | -5.17345 | 84.7% |
| VAL-HOT-01 | 8.06584 | -8.03452 | 10.04584 | -8.53320 | 87.6% |
| VAL-SSS-01 | 4.11334 | -4.02012 | 8.39967 | -8.42181 | 61.4% |

The small metric deltas relative to the preserved formal records are accepted for diagnostic reconstruction only. The original formal JSON records remain authoritative for validation claims.

## Temperature-region residual findings

### VAL-HOT-01

| Measured ECT | Mean residual C | RMSE C |
|---|---:|---:|
| 88 to 92 C | -0.510 | 1.197 |
| 92 to 96 C | -2.418 | 2.582 |
| 96 to 100 C | **-9.317** | **9.364** |

### VAL-SSS-01

| Measured ECT | Mean residual C | RMSE C |
|---|---:|---:|
| below 80 C | -3.699 | 3.806 |
| 80 to 88 C | -1.935 | 2.390 |
| 88 to 92 C | **-0.130** | **0.645** |
| 92 to 96 C | -2.333 | 2.486 |
| 96 to 100 C | **-7.982** | **8.054** |

Both independent holdouts are relatively accurate near 88 to 92 C and diverge strongly as measured ECT approaches the 99 C regulated region.

## Correlation summary

### VAL-HOT-01

| Channel | Pearson r with residual |
|---|---:|
| measured ECT | **-0.963** |
| RPM | -0.034 |
| dyno speed | +0.009 |
| fuel-energy rate | +0.147 |
| load | +0.169 |
| oil temperature | -0.918 |

### VAL-SSS-01

| Channel | Pearson r with residual |
|---|---:|
| measured ECT | -0.500 |
| RPM | +0.397 |
| dyno speed | +0.378 |
| fuel-energy rate | +0.430 |
| load | +0.467 |
| oil temperature | -0.679 |

### CAL-RAD-01

| Channel | Pearson r with residual |
|---|---:|
| measured ECT | -0.472 |
| RPM | +0.323 |
| dyno speed | +0.217 |
| fuel-energy rate | +0.107 |
| load | +0.102 |
| V1 thermostat fraction | +0.902 |
| V1 radiator-flow fraction | +0.806 |

Correlations are not treated as causal identification because the channels co-vary with time and thermal state.

## Thermostat/control counterfactual record

The consumed development traces were used to falsify the claim that a five-state model is already proven necessary.

Holding the final V1 model fixed and shifting the static thermostat opening/full-open thresholds upward produced:

| Threshold shift | Opening/full C | VAL-HOT RMSE C | VAL-SSS RMSE C |
|---:|---|---:|---:|
| +4 C | 92 / 102 | 5.081 | 3.365 |
| +5 C | 93 / 103 | 4.279 | 3.232 |
| +6 C | 94 / 104 | 3.579 | 3.266 |
| +7 C | 95 / 105 | 2.997 | 3.476 |
| +8 C | 96 / 106 | 2.503 | 3.809 |
| +9 C | 97 / 107 | 2.224 | 4.247 |
| +10 C | 98 / 108 | 2.309 | 4.757 |

These are deliberately post-hoc development counterfactuals. They are not calibrated vehicle parameters.

A +7 C shift also changes CAL-01 90 C arrival timing by approximately -92 s, which would fail the original 60 s project timing criterion despite improving the hot holdouts.

Interpretation: thermostat/control assumptions have enough leverage that vehicle-specific control evidence must be established before additional thermal states are declared necessary.

## Other falsification results

### Radiator UA

No single constant radiator UA below the original V1 bound reconciles both independent holdouts. Reducing UA can improve one condition while materially degrading another.

### Radiator-flow fraction

Reducing the fraction of pump flow routed through the radiator improves both holdouts, especially VAL-SSS, but does not fully resolve VAL-HOT. The V1 identity between thermostat opening and radiator-flow fraction is therefore a plausible contributor but not an isolated solution.

### Wall heat fraction

Increasing the constant heat fraction substantially above the V1 frozen maximum improves the traces only partially. Constant heat input scaling does not explain the hot-region failure alone.

## Additional observable discovered

The comprehensive Argonne files contain measured engine-oil temperature. Oil was not used as the V1 fitting target and can therefore serve as an auxiliary slow-thermal observable during V2 model-form development.

This does not yet justify an explicit oil state.

## Engineering decision

The full-trace evidence changes the V2 development strategy.

The five-state proposal:

```text
[T_head, T_slow, T_hot, T_cold, x_th]
```

remains a valid higher-order candidate, but it is no longer treated as the minimum architecture proven by V1 residuals.

VTMS-V2 will proceed through a nested hierarchy:

- **M0:** corrected-control two-state falsification baseline
- **M1:** three-state engine + hot coolant + cold coolant model
- **M2:** four-state split engine-storage + hot/cold coolant model
- **M3:** optional fifth dynamic thermostat state if separately justified

This hierarchy minimizes parameter growth and forces each added state to earn its place through a preregistered failure of the lower-order model.

## Governance

No V1 parameters were changed in the preserved project history.

No raw Argonne data are redistributed by this record.

No V2 calibration is authorized by these diagnostics.

Consumed V1 evidence is permanently classified as development/falsification evidence for V2 and cannot become blind V2 validation evidence.
