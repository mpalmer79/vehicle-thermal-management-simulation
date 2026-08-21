# VTMS-V2 Full-Trace Execution Record

## Status

This record is reserved for the first reconstruction of consumed VTMS-V1 Argonne comparison traces for VTMS-V2 model-form diagnosis.

The reconstruction must preserve each V1 run's original source identity, reviewed preprocessing, frozen parameter snapshot, and no-retuning rule. Results in this record are development evidence for VTMS-V2 only. They do not restore blind status to any consumed V1 holdout.

## Required runs

- CAL-01 / source 71207062
- CAL-RAD-01 / source 71207057
- VAL-HOT-01 / source 71207063
- VAL-SSS-01 / source 71207052

## Required diagnostics

For each run, record:

- exact source SHA-256 and source size
- exact parameter snapshot SHA-256
- preprocessing/mapping identity
- row count and normalized duration
- reconstructed RMSE, MAE, bias, P90 absolute error, and final error
- agreement against the previously frozen formal result
- residual correlation with measured ECT
- residual correlation with RPM
- residual correlation with dyno/vehicle-speed input
- residual correlation with fuel-energy rate
- residual correlation with load when available
- thermostat-region residual summary
- regulated-region residual summary
- time-localized extrema and persistent-bias intervals

## Acceptance rule for reconstruction

A reconstructed trace is accepted for diagnostic use only if its aggregate metrics reproduce the frozen formal result within numerical tolerance. If they do not, diagnose the reconstruction mismatch before interpreting residual correlations.

## Governance

No V1 parameters may be modified during reconstruction. No V2 parameters may be fitted from this record until the V2 equation set and calibration protocol are separately frozen.
