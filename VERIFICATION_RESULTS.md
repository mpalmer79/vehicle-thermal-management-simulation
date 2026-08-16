# VTMS-V1 Verification Results

**Run date:** August 15, 2026

**Core automated Python tests:** 17 passed

**Combined engine + validation tests:** 22 passed

**Specification verification checks:** 21 passed

**Solver convergence:** maximum one-second state difference = 0.000428107 °C

## Canonical scenario results

| ID | Scenario | End engine °C | End coolant °C | Energy residual | Warning |
|---|---|---:|---:|---:|---|
| S-01 | Cold start / fast idle | 102.68 | 96.47 | 6.772e-06 | No |
| S-02 | Warm highway cruise | 122.42 | 90.86 | 1.520e-05 | No |
| S-03 | Hot ambient idle | 101.06 | 96.50 | 2.478e-05 | No |
| S-04 | Sustained higher load | 139.76 | 96.34 | 4.737e-06 | No |
| S-05 | Fan failure at hot idle | 167.96 | 166.73 | 3.464e-08 | Yes |
| S-06 | Thermostat stuck closed | 167.96 | 166.73 | 3.464e-08 | Yes |
| S-07 | 50% pump degradation | 146.06 | 102.72 | 2.894e-06 | No |
| S-08 | 40% radiator UA loss | 163.07 | 119.94 | 1.462e-06 | No |
| S-09 | 50% airflow restriction | 145.25 | 101.89 | 2.728e-06 | No |

## Interpretation

The suite verifies implementation consistency with Engineering Model Specification 1.0.0. It does not constitute production-vehicle physical validation. S-05 and S-06 exceed the implementation liquid-only caution boundary, so those high-temperature results are intentionally labeled qualitative because pressure and phase-change physics are outside V1.

## Status

**PASS: VTMS-V1 standalone Python engine is ready for independent physical validation.**
