# VTMS-V2 Residual Traceability Record

## Status

**Development/falsification evidence. Not a validation result.**

This record traces preserved VTMS-V1 evidence and reconstructed consumed-run residuals to the revised VTMS-V2 model hierarchy.

The initial five-state proposal remains a candidate higher-order architecture. Full-trace Phase 2 analysis showed that the evidence does not yet prove every proposed state is necessary.

## Full-trace evidence to V2 requirements

| Evidence | Observed V1 behavior | Supported inference | V2 disposition | Confidence |
|---|---|---|---|---|
| VAL-HOT full trace | residual is about -0.5 C at measured 88-92 C but -9.3 C at 96-100 C | failure is concentrated in hot regulation, not a uniform warm-up time-scale error | correct thermostat/control boundary first; then test hot/cold coolant topology | very high |
| VAL-SSS full trace | residual is about -0.13 C at 88-92 C but -8.0 C at 96-100 C | independent condition reproduces the same temperature-region failure | same hot-region hypothesis survives independent-condition comparison | very high |
| VAL-HOT correlations | residual vs measured ECT r=-0.963; vs speed r=+0.009; vs RPM r=-0.034 | temperature/control state dominates the raw residual structure; speed is not the primary isolated driver | airflow remains governed but secondary to control/topology diagnosis | high |
| CAL-RAD-01 | radiator UA fitted to 400.83 W/K, near lower bound, yet remains cold | one constant UA cannot reconcile radiator-active evidence under V1 control/topology | constant UA alone rejected as solution | very high |
| thermostat counterfactual | upward static threshold shifts dramatically reduce both holdout RMSEs | assumed thermostat/control law has enough leverage that topology cannot be chosen before vehicle-specific control is constrained | vehicle-specific thermostat/control identification required before state expansion | very high |
| thermostat counterfactual across CAL-01 | hot-holdout improvement can damage cold-start timing | no single post-hoc thermostat shift should be treated as a physical calibration | use counterfactual only for falsification; freeze physical control evidence independently | very high |
| V1 flow split | radiator-flow fraction equals thermostat opening fraction | valve position and hydraulic branch flow are conflated | replace with bounded nonlinear or pressure-loss-based split | very high |
| flow-split counterfactual | reduced radiator fraction improves both holdouts but does not fully solve VAL-HOT | hydraulic split is a contributor but not isolated root cause | include improved static hydraulics in M0/M1 | high |
| V1 single coolant state | one integrated coolant temperature supplies engine coolant, thermostat sensing, and radiator inlet state | V1 cannot preserve engine-out vs radiator-return thermal separation | M1 adds `T_hot` and `T_cold` if M0 fails | high |
| V1 internal radiator outlet | V1 predicts large algebraic radiator outlet drops under conditions where only one coolant state is integrated | the existing model itself implies branch temperature separation that its state vector discards | supports M1 hot/cold state experiment | high |
| CAL-01 | wall heat fraction and engine-to-coolant UA press upper bounds | V1 warm-up fit uses effective parameters as compensators | test M1 first; add second engine storage state only if boundary pressure persists | high |
| KIT plausibility | warm-up far too early but final temperature nearly correct | transient storage remains a credible secondary model-form issue | M2 split engine storage if M1 retains transient failure | high |
| wall-heat counterfactual | even large increases do not resolve VAL-HOT | constant heat scaling is not the primary isolated hot-region error | operating-dependent heat partition remains secondary candidate | high |
| hot-start initialization | hidden engine state defaults to measured coolant | early hot-start thermal memory is not represented | improve initialization governance at every V2 level | high for early transient, low as explanation for late bias |
| Argonne oil temperature | independent measured oil trace is available and differs by test | provides slow-thermal observable not used as V1 target | use oil to test M2 slow-state hypothesis before adding explicit oil state | high |
| Argonne dyno boundary | dyno speed feeds V1 ram-air surrogate | chassis speed is not radiator-core air velocity | explicit airflow provenance required in M0+ | high governance confidence |

## Revised model hierarchy

### M0: corrected-control two-state baseline

```text
[T_engine, T_coolant]
```

Purpose:

- source/freeze vehicle-specific thermostat/control behavior;
- replace thermostat-opening equals radiator-flow-fraction identity;
- make cooling-pack airflow provenance explicit;
- determine whether control/boundary assumptions alone explain the failure with physically credible parameters.

### M1: minimum hot/cold coolant model

```text
[T_engine, T_hot, T_cold]
```

Promote only if M0 fails under preregistered criteria.

This is the first structural state expansion because the strongest residual evidence is localized to the regulated coolant region.

### M2: split engine thermal storage

```text
[T_head, T_slow, T_hot, T_cold]
```

Promote only if M1 retains transient/storage error or requires unphysical effective engine parameters.

Use measured oil temperature as auxiliary evidence for `T_slow`.

### M3: optional dynamic thermostat

```text
[T_head, T_slow, T_hot, T_cold, x_th]
```

Promote only if a sourced static thermostat/control law leaves reproducible lag/hysteresis evidence or independent actuator evidence justifies the state.

## What is no longer claimed

The project no longer claims that current V1 residuals uniquely prove:

- a dynamic thermostat state is mandatory;
- two engine structural states must be implemented before testing hot/cold coolant separation;
- flow-dependent radiator UA must be introduced immediately;
- operating-dependent heat partition is a first-order requirement;
- the five-state model is the minimum sufficient V2 topology.

Those remain testable hypotheses within the hierarchy.

## What is strongly established

The V1 evidence does establish that:

1. V1 fails formal physical validation under its frozen topology and parameters.
2. The independent holdout failures share a large high-temperature cold bias.
3. A constant radiator-UA adjustment alone does not reconcile the evidence.
4. A constant heat-input scaling alone does not reconcile the evidence.
5. The assumed thermostat/control boundary has enough leverage that it must be physically constrained before topology selection.
6. V1's identity between valve opening and radiator-flow fraction is too restrictive for a governed V2 model.
7. Additional state complexity must be earned through failure of a lower-order model, not added all at once.

## Identifiability rule

Each hierarchy level must pass synthetic sensitivity and parameter-correlation review before physical fitting.

Do not fit all available parameters to ECT simultaneously. Prefer independent source constraints and auxiliary observables, including oil temperature, over added optimizer freedom.
