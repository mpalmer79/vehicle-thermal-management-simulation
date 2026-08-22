# VTMS-V2 M0 Synthetic Identifiability Freeze

## Status

**Gate V2-M0-I1: Synthetic pre-fit identifiability. PASS with stage restrictions.**

This record freezes the interpretation of the VTMS-V2-M0 synthetic sensitivity analysis before any M0 physical parameter fitting occurs.

No Argonne residuals were used by the M0 identifiability calculation. No reserved blind V2 prediction was generated. Passing this gate does not authorize physical calibration by itself.

## Executable M0 baseline

The branch now contains an executable `vtms_v2.m0` package with:

- a dedicated M0 parameter object and model metadata;
- sourced static thermostat opening onset and bounded full-open uncertainty;
- nonlinear radiator/bypass branch-flow splitting;
- explicit cooling-air boundary classes;
- an M0 thermal assembly that retains the two-state V1 energy topology while replacing the corrected control/boundary laws;
- an RK45 M0 simulation runner;
- deterministic synthetic identifiability diagnostics;
- M0 verification tests.

VTMS-V1 is not modified by these classes.

## Synthetic excitation set

The identifiability preflight uses three deterministic scenarios only:

```text
SYN-M0-WARMUP
SYN-M0-CONSTANT-FAN
SYN-M0-SPEED-MATCHED
```

Together they create thermostat-transition, hot-regulation, constant-external-fan, and speed-dependent cooling excitation without reading Argonne measurements.

## Candidate heat-rejection/control parameters

The tested five-parameter universe is:

```text
radiator_ua_nominal_w_per_k
eta_pack
f_closed
f_open
gamma
```

The five-parameter set has numerical rank 5 but is **not authorized for simultaneous fitting**.

Key diagnostics:

| Diagnostic | Result |
|---|---:|
| normalized Jacobian condition number | 15.7838 |
| strongest absolute pairwise cosine | 0.983359 |
| weakest global parameter | `f_closed` |
| `f_closed` relative RMS sensitivity | 0.00663 |
| simultaneous five-parameter fit | prohibited |

The dominant confounding pair is:

```text
radiator_ua_nominal_w_per_k <-> f_open
absolute pairwise cosine = 0.983359
```

Therefore radiator UA and fully-open radiator branch fraction may not be optimized in the same physical M0 calibration stage.

## Cooling-pack transfer and radiator UA

The synthetic `radiator_ua_nominal_w_per_k + eta_pack` pair is mathematically full-rank:

```text
condition number = 3.63195
absolute pairwise cosine = 0.859066
```

This does **not** authorize simultaneous physical fitting of those two terms.

`eta_pack` represents an unresolved external-fan-to-effective-core-airflow boundary. It is an input-boundary uncertainty, not a radiator property. Allowing ECT to identify both `eta_pack` and radiator UA would risk assigning test-cell airflow error to the heat exchanger.

For the first M0 physical program:

- `eta_pack` is uncertainty-only and is not an optimizer variable;
- radiator UA may not be interpreted as a bench radiator constant;
- any later joint identification requires independent cooling-pack airflow evidence.

## Hydraulic parameter decision

The three-parameter hydraulic shape set is mathematically distinguishable, but `f_closed` is weak when assessed against the complete heat-rejection parameter universe.

The narrower pair:

```text
f_open
gamma
```

is strongly distinguishable under the synthetic excitation:

| Diagnostic | Result |
|---|---:|
| normalized Jacobian condition number | 1.24448 |
| absolute pairwise cosine | 0.215298 |
| numerical rank | 2 |
| weak parameters | none |
| mathematical subset authorization | pass |

Therefore the first M0 iteration freezes:

```text
f_closed = 0.02
```

as a fixed engineering assumption.

The only hydraulic parameters eligible for a future preregistered physical hydraulic stage are:

```text
f_open in [0.85, 1.00]
gamma  in [0.50, 2.00]
```

This mathematical eligibility does not yet authorize a physical fit. The physical stage must additionally hold the cooling-air boundary and radiator-UA treatment fixed or explicitly bounded under a frozen uncertainty design.

## Thermostat full-open uncertainty

The exact Motorcraft RT-1219 full-open temperature remains unverified.

The existing 97 to 102 C engineering envelope is now frozen as a **discrete non-optimized sensitivity design** for initial M0 work:

```text
97.0 C
99.5 C
102.0 C
```

No continuous optimizer may select thermostat full-open temperature from consumed residuals.

The sourced opening onset remains fixed at approximately 87.8 C.

## External-fan-to-core airflow uncertainty

Until direct cooling-pack airflow or a validated fan-to-core transfer relation is obtained, `eta_pack` is treated as a non-identified nuisance boundary rather than a physical calibration parameter.

Initial uncertainty design points are:

```text
eta_pack = 0.10, 0.25, 0.40, 0.60, 0.80, 1.00
```

These values span the allowed dimensionless transfer domain for stress testing. They are not claimed as probability bounds or measured Ford/Argonne transfer efficiencies.

A physical M0 conclusion that changes solely because one post-hoc `eta_pack` value is selected is not robust enough to justify validation or model promotion.

## Hot-region metric evaluability

The 96 to 100 C hot-region mean residual criterion is evaluable only when the selected comparison contains both:

```text
at least 30 distinct comparison samples
and
at least 30 seconds of total time coverage within measured ECT 96..100 C
```

The metric limit remains:

```text
absolute mean residual <= 3.0 C
```

If the coverage rule is not met, the hot-region metric is reported as non-evaluable rather than passed.

Source-only qualification of reserved test 71207054 establishes that it has abundant 96 to 100 C coverage. This statement uses measured source data only and does not inspect an M0 prediction.

## First-stage prohibitions

The following combinations are explicitly prohibited for the initial M0 physical program:

```text
radiator UA + f_open in one optimizer stage
radiator UA + eta_pack in one ECT-only optimizer stage
eta_pack fitted directly from ECT
f_closed fitted in the first physical iteration
thermostat full-open temperature continuously optimized from residuals
all five heat-rejection/control parameters fitted together
per-run hydraulic parameters
per-run radiator UA
```

## Blind holdout protection

`71207054` remains the M0 primary blind holdout.

Its exact source mapping and source-only QC are frozen separately in:

```text
validation_configs/argonne_2012_focus_71207054_m0_blind.json
```

The mapping explicitly records `prediction_inspected = false` and `prediction_generation_authorized = false`.

The current airflow boundary for that test is still classified `UNKNOWN`. The blind prediction remains blocked until the test's airflow treatment is frozen or the approved uncertainty policy is incorporated into the blind decision protocol before prediction.

## Gate decision

**V2-M0-I1 passes.**

This means:

- executable M0 infrastructure is accepted for further pre-fit development;
- the complete five-parameter control fit is rejected;
- `f_open + gamma` is the only hydraulics pair currently eligible for a later staged physical fit;
- `f_closed` is fixed at 0.02 for the first M0 iteration;
- `eta_pack` is uncertainty-only, not physically identified;
- thermostat full-open uncertainty is discrete, not fitted;
- the blind holdout remains protected.

Physical M0 calibration remains **not authorized** until a complete physical-stage manifest freezes which consumed development runs are used, their airflow treatments, fixed nuisance cases, objective functions, and parameter subset.
