# VTMS-V2 Model-Form Revision Specification Amendment 1

## Status

**This amendment supersedes the original specification wherever that document describes the five-state architecture as the minimum or already-proven VTMS-V2 topology.**

The original specification remains useful as the detailed definition of the higher-order five-state candidate. Full consumed-run residual reconstruction completed afterward provided new evidence that requires a more conservative model-selection process.

## Reason for amendment

Full reconstruction of CAL-01, CAL-RAD-01, VAL-HOT-01, and VAL-SSS-01 established that the largest independent holdout errors develop primarily as measured coolant temperature enters the 96 to 100 C regulated region.

Both holdouts are comparatively accurate around 88 to 92 C and then become strongly cold-biased near 99 C.

A post-hoc static thermostat-threshold counterfactual can remove much of this hot-region error numerically without adding states. That counterfactual is not a valid calibration and is not accepted as a physical thermostat model. Its significance is epistemic: it proves that the residuals do not uniquely require all five originally proposed states.

## Superseded design statement

The following statement is no longer valid as a frozen implementation decision:

```text
VTMS-V2 minimum state vector = [T_head, T_block, T_hot, T_cold, x_th]
```

Replace it with:

```text
VTMS-V2 uses a nested model hierarchy.
State additions require preregistered failure of the lower-order model.
```

## Revised hierarchy

### V2-M0

```text
[T_engine, T_coolant]
```

Correct vehicle-specific thermostat/control assumptions, hydraulic flow-split behavior, and airflow provenance while retaining two thermal states as a falsification baseline.

### V2-M1

```text
[T_engine, T_hot, T_cold]
```

First structural expansion. Add separate engine-out/ECT-side and radiator-return coolant states if M0 cannot generalize with physically credible parameters.

### V2-M2

```text
[T_head, T_slow, T_hot, T_cold]
```

Add a second engine thermal-storage state only if M1 retains transient/storage residuals or forces effective engine parameters outside defensible ranges. Use measured oil temperature as auxiliary evidence.

### V2-M3

```text
[T_head, T_slow, T_hot, T_cold, x_th]
```

The original five-state design becomes M3. Add the dynamic thermostat state only if sourced static control behavior leaves reproducible lag/hysteresis error or independent actuator evidence supports it.

## Requirements retained from the original specification

The following governance principles remain in force:

- VTMS-V1 remains unchanged and its failed holdouts remain preserved.
- Consumed V1 evidence may support V2 development but can never become blind V2 validation evidence.
- Browser code must not become the governing physics implementation.
- Direct fuel evidence remains preferred for controlled thermal input.
- Numerical verification remains distinct from physical validation.
- Parameter bounds and model promotion rules must be frozen before the evidence they govern is evaluated.
- State complexity must not be added merely to improve curve fit.
- No machine-learned residual correction is authorized for the initial V2 physics hierarchy.

## Requirements changed by this amendment

### Dynamic thermostat

Changed from required to conditional M3 capability.

### Two engine structural states

Changed from immediate V2 requirement to conditional M2 capability.

### Flow-dependent radiator UA

Changed from immediate requirement to secondary constitutive-law candidate after M0/M1 control and topology tests.

### Operating-dependent heat partition

Changed from immediate requirement to secondary candidate after dominant control/topology hypotheses are tested.

### Hot/cold coolant separation

Retained as the highest-priority structural state expansion, but only after M0 tests whether corrected physical control/boundary assumptions can explain the evidence without added states.

## New first-order requirement

The project must identify and freeze a physically defensible vehicle-specific thermostat/control boundary before selecting V2 state complexity.

A post-hoc thermostat threshold that minimizes consumed residuals is not an acceptable source.

## Gate change

The next gate is **Model Hierarchy Freeze**, not immediate five-state Equation Freeze.

See:

- `VTMS_V2_PHASE2_RESIDUAL_DIAGNOSTICS.md`
- `VTMS_V2_RESIDUAL_TRACEABILITY.md`
- `VTMS_V2_FULL_TRACE_EXECUTION_RECORD.md`
- `VTMS_V2_EQUATION_FREEZE_PLAN.md`

for the revised evidence and promotion rules.
