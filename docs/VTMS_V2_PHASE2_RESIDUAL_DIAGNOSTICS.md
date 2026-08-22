# VTMS-V2 Phase 2 Residual Diagnostics

## Status

**Full consumed-run residual reconstruction complete for CAL-01, CAL-RAD-01, VAL-HOT-01, and VAL-SSS-01.**

The original Argonne archives were recovered from the project file library and their source files reproduce the SHA-256 fingerprints frozen in the VTMS-V1 validation records. The four V1 comparisons were reconstructed with the frozen V1 equations, signal mappings, parameter snapshots, direct fuel evidence, and no-retuning rules.

This work is model-development evidence for VTMS-V2. It does not restore blind status to any consumed V1 holdout and does not authorize V1 retuning.

## Reconstruction integrity

The recovered source files match the frozen V1 identities:

| Run | Source test | Frozen source SHA-256 status |
|---|---:|---|
| CAL-01 | 71207062 | exact match |
| CAL-RAD-01 | 71207057 | exact match |
| VAL-HOT-01 | 71207063 | exact match |
| VAL-SSS-01 | 71207052 | exact match |

The reconstructed aggregate metrics agree with the preserved formal records within small numerical reconstruction differences. Those differences are immaterial to the residual-shape conclusions and must not be interpreted as a replacement formal result.

| Run | Reconstructed RMSE C | Frozen RMSE C | Delta C |
|---|---:|---:|---:|
| CAL-01 | 3.71784 | 3.71596 | +0.00188 |
| CAL-RAD-01 | 5.73802 | 5.73268 | +0.00534 |
| VAL-HOT-01 | 8.58427 | 8.58744 | -0.00317 |
| VAL-SSS-01 | 5.12995 | 5.12590 | +0.00406 |

Raw Argonne rows and reconstructed time-series traces are not committed. Only derived diagnostics may be retained in the repository.

## Aggregate bias decomposition

For residual `r = predicted - measured`:

```text
MSE = bias^2 + residual variance
```

The reconstructed bias contribution to MSE is:

| Run | Bias C | Bias fraction of MSE |
|---|---:|---:|
| CAL-01 | -2.4168 | 42.3% |
| CAL-RAD-01 | -5.2813 | 84.7% |
| VAL-HOT-01 | -8.0345 | 87.6% |
| VAL-SSS-01 | -4.0201 | 61.4% |

The hot-operation failures are therefore dominated by systematic cold bias rather than zero-mean scatter.

## The dominant residual structure is temperature-region dependent

The full traces provide a substantially stronger diagnosis than the aggregate metrics alone.

### CAL-01 residual by measured ECT

| Measured ECT region | Mean residual C | RMSE C |
|---|---:|---:|
| below 80 C | -2.54 | 3.88 |
| 80 to 88 C | +3.02 | 3.14 |
| 88 to 92 C | -0.20 | 1.45 |
| 92 to 96 C | -3.93 | 4.15 |
| 96 to 100 C | -5.52 | 5.56 |

### CAL-RAD-01 residual by measured ECT

| Measured ECT region | Mean residual C | RMSE C |
|---|---:|---:|
| 88 to 92 C | +4.08 | 4.10 |
| 92 to 96 C | +0.66 | 1.86 |
| 96 to 100 C | -5.44 | 5.80 |

### VAL-HOT-01 residual by measured ECT

| Measured ECT region | Mean residual C | RMSE C |
|---|---:|---:|
| 88 to 92 C | -0.51 | 1.20 |
| 92 to 96 C | -2.42 | 2.58 |
| 96 to 100 C | **-9.32** | **9.36** |

More granular VAL-HOT behavior:

| Measured ECT region | Mean residual C |
|---|---:|
| 88 to 90 C | +0.57 |
| 90 to 92 C | -1.34 |
| 92 to 94 C | -2.33 |
| 94 to 96 C | -3.77 |
| 96 to 98 C | -5.32 |
| 98 to 100 C | **-9.38** |

### VAL-SSS-01 residual by measured ECT

| Measured ECT region | Mean residual C | RMSE C |
|---|---:|---:|
| below 80 C | -3.70 | 3.81 |
| 80 to 88 C | -1.94 | 2.39 |
| 88 to 92 C | **-0.13** | **0.64** |
| 92 to 96 C | -2.33 | 2.49 |
| 96 to 100 C | **-7.98** | **8.05** |

More granular VAL-SSS behavior:

| Measured ECT region | Mean residual C |
|---|---:|
| 88 to 90 C | +0.50 |
| 90 to 92 C | -0.61 |
| 92 to 94 C | -2.02 |
| 94 to 96 C | -4.32 |
| 96 to 98 C | -5.92 |
| 98 to 100 C | **-8.40** |

## Primary Phase 2 finding

Both independent holdouts are comparatively accurate around **88 to 92 C**, then develop a rapidly increasing cold bias as the measured vehicle enters the approximately **96 to 100 C regulated region**.

This rejects a simple explanation based only on a global warm-up time constant.

The principal V1 generalization failure is concentrated in the hot coolant-control / heat-rejection regime.

## Operating-channel correlations

Pearson correlations are diagnostic, not causal. Several operating channels co-vary with time, temperature, and one another.

### VAL-HOT-01

| Variable | Residual correlation |
|---|---:|
| measured ECT | **-0.963** |
| RPM | -0.034 |
| dyno speed | +0.009 |
| fuel energy rate | +0.147 |
| load | +0.169 |
| oil temperature | -0.918 |

The very weak RPM and speed correlations in VAL-HOT materially weaken the hypothesis that its approximately 8 to 10 C hot-region error is primarily a vehicle-speed/ram-air problem.

### VAL-SSS-01

| Variable | Residual correlation |
|---|---:|
| measured ECT | -0.500 |
| RPM | +0.397 |
| dyno speed | +0.378 |
| fuel energy rate | +0.430 |
| load | +0.467 |
| oil temperature | -0.679 |

These correlations are more mixed and remain confounded by the steady-speed warm-up structure.

### CAL-RAD-01

| Variable | Residual correlation |
|---|---:|
| measured ECT | -0.472 |
| RPM | +0.323 |
| dyno speed | +0.217 |
| fuel energy rate | +0.107 |
| load | +0.102 |
| V1 thermostat fraction | +0.902 |
| V1 radiator-flow fraction | +0.806 |

The strong correlation with V1's own thermostat/radiator-flow states is evidence that the residual is closely coupled to the control topology, but it does not prove that thermostat dynamics alone are the missing physics.

## Cross-condition evidence against airflow as the sole root cause

Late in VAL-HOT, the average modeled condition is low-speed and modest-load while the model remains approximately 9 C too cold.

Late in VAL-SSS, the vehicle is at substantially higher speed/load while the model is also approximately 8 to 9 C too cold.

A similar endpoint error appearing under materially different speed and airflow conditions is inconsistent with cooling-pack airflow being the sole root cause.

Airflow governance remains required for controlled dynamometer science because dyno speed is not radiator-core air velocity, but it is now classified as a secondary uncertainty rather than the primary explanation for both holdout failures.

## Thermostat/control counterfactual

Because the V1 thermostat thresholds were engineering assumptions rather than vehicle-specific measurements, Phase 2 tested a deliberately post-hoc counterfactual on the already-consumed development evidence.

The V1 static thermostat curve is:

```text
opening begins: 88 C
fully open:     98 C
```

Shifting both thresholds upward while holding the rest of the final staged V1 model fixed produces large numerical changes.

### Holdout counterfactual

| Shift | Opening/full C | VAL-HOT RMSE C | VAL-SSS RMSE C |
|---:|---|---:|---:|
| +4 C | 92 / 102 | 5.081 | 3.365 |
| +5 C | 93 / 103 | 4.279 | 3.232 |
| +6 C | 94 / 104 | 3.579 | 3.266 |
| +7 C | 95 / 105 | 2.997 | 3.476 |
| +8 C | 96 / 106 | 2.503 | 3.809 |
| +9 C | 97 / 107 | 2.224 | 4.247 |
| +10 C | 98 / 108 | 2.309 | 4.757 |

This is an important falsification result.

It shows that a simple static control-curve change can numerically remove much of the independent hot-region error without adding thermal states.

It therefore **invalidates the earlier claim that the five-state topology has already been proven necessary by the V1 residuals**.

However, the counterfactual is not an acceptable calibration result. It is post-hoc, uses consumed evidence, and has no current physical basis establishing a 95 to 108 C opening/full-open thermostat curve for the test vehicle.

It also degrades other aspects of the evidence. For example, a +7 C shift gives CAL-01 RMSE about 4.03 C but moves its 90 C arrival approximately 92 s early, outside the project's 60 s timing criterion.

The correct conclusion is not to retune the thermostat. The correct conclusion is that **vehicle-specific thermostat/control identification must precede topology expansion**.

## Counterfactuals that do not explain the failure alone

### Radiator UA alone

Allowing radiator UA below the original preregistered V1 lower bound does not produce one value that reconciles both independent holdouts.

Examples:

- around 100 W/K, VAL-HOT improves but VAL-SSS becomes grossly hot
- around 200 W/K, VAL-SSS improves substantially while VAL-HOT remains materially cold
- around the frozen 400 W/K boundary, both retain their original failure pattern

Constant radiator UA is therefore rejected as the sole missing degree of freedom.

### Radiator-flow fraction alone

Scaling V1 radiator flow below the identity `radiator_flow_fraction = thermostat_fraction` improves both traces, particularly VAL-SSS, but does not fully resolve VAL-HOT.

This supports hydraulic flow-split revision as a contributor, not a complete explanation.

### Wall heat fraction alone

Increasing wall heat fraction substantially above its original frozen 0.50 maximum improves the error only moderately. Even values around 0.70 do not resolve VAL-HOT.

Constant heat partition is therefore not the primary isolated failure mechanism.

## V1 single-coolant-state limitation remains strongly supported

V1 uses one coolant state as both the engine-side coolant temperature and the temperature from which radiator heat is removed.

The reconstructed V1 model simultaneously produces very large algebraic radiator outlet drops under some hot-region conditions while keeping only one integrated bulk coolant state. Those model-internal outlet values are not physical measurements and must not be presented as such. They demonstrate that V1 itself predicts large spatial branch temperature differences that its state vector cannot preserve dynamically.

This supports separating engine-out/hot coolant from radiator-return/mixed coolant in the next minimal topology experiment.

## Oil temperature as an independent observable

The comprehensive Argonne data include measured engine-oil temperature.

Observed oil behavior differs materially among the consumed tests and provides an additional thermal observable not used in the V1 fitting target. It is valuable for distinguishing fast and slow thermal storage.

Phase 2 does **not** yet justify adding oil as a mandatory sixth or separate state. The preferred use is:

1. use measured oil temperature as auxiliary evidence for slow thermal-state identifiability;
2. test whether a generic slow structural state can explain it sufficiently;
3. add an explicit oil state only if the lower-order model fails under preregistered criteria.

## Revised V2 model hierarchy

Phase 2 supersedes the earlier decision to jump directly to a frozen five-state implementation.

V2 should now be developed through nested falsification models.

### V2-M0: corrected-control two-state baseline

Retain the V1 two-state thermal topology temporarily, but replace unsupported generic control assumptions with physically sourced/frozen vehicle-specific inputs where available:

- vehicle-specific thermostat opening behavior
- explicit control/sensor temperature definition
- improved static radiator/bypass flow-split law
- explicit dynamometer airflow-boundary provenance

Purpose: determine how much of the V1 failure is caused by boundary/control assumptions before adding states.

V2-M0 is a falsification baseline, not the expected final production model.

### V2-M1: minimum hot/cold coolant topology

If M0 cannot generalize with physically credible parameters, introduce the minimum structural revision:

```text
x = [T_engine, T_hot, T_cold]
```

where:

- `T_engine` retains one effective engine-structure state
- `T_hot` is the engine-out / ECT-side coolant state
- `T_cold` is radiator-return / pump-inlet coolant state

ECT initially observes `T_hot`.

Thermostat behavior remains a static physically sourced control law unless data demonstrate that a dynamic state is required.

This is now the preferred first executable V2 model-form experiment.

### V2-M2: split engine thermal storage

Only if M1 cannot reproduce consumed development evidence without unphysical parameters or systematic transient residuals, add a second structural state:

```text
x = [T_head, T_slow, T_hot, T_cold]
```

Measured oil temperature should be used as auxiliary evidence for the `T_slow` hypothesis.

### V2-M3: dynamic thermostat state

Add:

```text
x_th
```

only if static vehicle-specific thermostat/control behavior leaves reproducible lag/hysteresis residuals or independent thermostat-position/control evidence supports it.

The originally proposed five-state model:

```text
[T_head, T_block, T_hot, T_cold, x_th]
```

therefore remains a valid **candidate V2-M3 architecture**, but it is no longer classified as the minimum architecture already proven by V1 residuals.

## Revised requirement confidence

| Proposed capability | Phase 2 disposition |
|---|---|
| vehicle-specific thermostat/control identification | **required before model expansion** |
| separate hot-side ECT and radiator-return coolant representation | **high-confidence structural candidate, first state expansion** |
| nonlinear radiator/bypass hydraulic split | **high-confidence contributor** |
| explicit dyno/cooling-pack airflow provenance | **required governance, secondary error mechanism** |
| flow-dependent radiator UA | **secondary candidate, not proven primary** |
| second engine thermal-storage state | **conditional M2 addition** |
| dynamic thermostat/hysteresis state | **conditional M3 addition, not yet proven** |
| operating-dependent heat partition | **secondary candidate** |
| state-aware initialization | **required protocol improvement, not root cause** |
| explicit oil state | **not yet justified** |

## Implemented diagnostic harness

`src/vtms_validation/residual_diagnostics.py` provides deterministic, no-fit diagnostics for reconstructed comparison traces. It reports:

- mean residual
- MAE
- RMSE
- maximum absolute residual
- bias fraction of MSE
- positive/negative residual fractions
- residual metrics by measured-coolant-temperature bin
- residual metrics across the thermostat transition region
- residual correlations against available operating channels

`scripts/run_v1_residual_diagnostics.py` provides an offline entry point for already-reconstructed comparison CSVs.

Neither tool fits or changes model parameters.

## Governance decision

The consumed V1 runs may now be used as **V2 development/falsification evidence only**.

They must never be relabeled as blind V2 validation evidence.

No counterfactual in this document is a calibration result. Its purpose is to determine which hypotheses survive before V2 equations and calibration freedoms are frozen.

## Revised next gate

**Gate V2-2 is changed from immediate five-state Equation Freeze to Model Hierarchy Freeze.**

Before writing the V2 engine, freeze:

1. the M0, M1, M2, and optional M3 hypothesis hierarchy;
2. the physical source for the 2012 Focus thermostat/control law;
3. the M0 radiator/bypass static flow law;
4. the cooling-pack airflow evidence policy;
5. quantitative promotion criteria from M0 to M1, M1 to M2, and M2 to M3;
6. the V2 development dataset roles;
7. untouched evidence reserved for eventual V2 validation.

Only after that hierarchy is frozen should executable V2 physics development begin.
