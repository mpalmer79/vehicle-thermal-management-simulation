# VTMS-V2 M1 Rejection and M2 Promotion Gate

## Decision

**Gate V2-M1-R1: PASS. M1 is rejected as the continuing model form and M2 model-form planning is authorized.**

This is a model-selection decision based only on already-consumed development evidence. It is not a validation claim, does not promote any M1 parameter set, and does not open any reserved blind prediction.

## M1 model tested

M1 was the minimum structural expansion after M0 rejection:

\[
x_{M1}=[T_{engine},T_{hot},T_{cold}]
\]

with `ECT_pred = T_hot`.

M1 retained one effective engine-structure state and added explicit engine-out and radiator-return coolant control volumes. The total coolant thermal capacitance remained conserved and partitioned by one topology parameter.

The retained M0 control boundary included the static thermostat law, nonlinear radiator/bypass split, explicit external-fan airflow treatment, RPM-based pump, internal fan controller, and effectiveness-NTU radiator.

## Synthetic gate before physical development

M1 passed synthetic verification and synthetic prefit identifiability with stage restrictions.

The new hot/cold capacitance partition produced a nonzero and distinguishable ECT signature. The topology-plus-engine subset was full rank, but radiator UA and `f_open` remained nearly collinear. Therefore the project prohibited a single all-parameter physical optimizer and instead used a preregistered feasibility envelope.

## Physical-development evidence

Only previously consumed development tests were used:

- 71207062, cold-start development;
- 71207063, hot-start development.

No source reserved for a future M1/M2/M3 blind rung was opened for model prediction.

The hot-start comparison used nine preregistered hidden-state initialization combinations:

- `T_engine(0) - ECT(0)` in `{0, 10, 20} C`;
- `T_cold(0) - ECT(0)` in `{0, -5, -10} C`.

Those states were evaluated as fixed sensitivity cases and were not fitted per run.

## Stage A

Stage A evaluated 180 structural/thermal M1 configurations at the frozen central cooling-control reference.

Results:

- cold-start passes: **6 / 180**;
- hot-start passes under any hidden-state initialization: **0 / 180**;
- conditional joint survivors: **0**;
- robust joint survivors: **0**.

The frozen rule therefore opened Stage B before any M1 rejection was allowed.

## Stage B

Stage B crossed the same 180 structural cases with 243 preregistered cooling-control cases:

\[
180 \times 243 = 43{,}740
\]

The control envelope included:

- thermostat full-open temperature: 97.0, 99.5, 102.0 C;
- `eta_pack`: 0.25, 0.40, 0.80;
- radiator UA: 400, 1100, 2200 W/K;
- `f_open`: 0.85, 0.95, 1.0;
- `gamma`: 0.5, 1.0, 2.0.

The exact joint-feasibility predicate was evaluated efficiently by screening the cold trace first. This changes only execution order, not the mathematical set being tested: a joint survivor must pass both traces, so any cold failure can be discarded before hot-start evaluation without changing the joint result.

Cold-screen result:

- **2,957 / 43,740** configurations passed the cold-start acceptance criteria;
- pass fraction: **6.7604%**.

Those exact 2,957 configurations were then evaluated against all nine preregistered hot-start hidden-state initialization cases, producing 26,613 configuration-initialization evaluations.

**Hot-start result: zero passes in every one of the nine initialization cases.**

Therefore:

- conditional joint survivors: **0**;
- robust joint survivors: **0**;
- exact joint feasible set: **empty**.

## Execution corrections

Two implementation issues were detected before any Stage B conclusion was accepted.

First, an initial Stage B grid used `f_open=0.925` and accidentally omitted the Stage A reference `0.95`. The partial calculation was invalidated, the manifest was amended to restore a nested grid, and Stage B was restarted from scratch.

Second, an initial local screening helper checked the 96-100 C hot-region criterion after the minimum sample count but before enforcing the separate 30-second coverage requirement. That partial calculation was also invalidated before any conclusion. The frozen rule was restored exactly and Stage B was restarted.

No invalidated partial result contributes to the final counts above.

## Interpretation

The result does **not** prove that every conceivable three-state automotive thermal model is impossible.

It establishes something narrower and sufficient for this governed hierarchy: hot/cold coolant separation by itself cannot reconcile the consumed cold-start and hot-start evidence inside the frozen M1 structural, thermal, cooling-control, and hidden-state envelopes.

Further widening or retuning M1 after this result would violate the preregistered hierarchy and would allow the remaining effective parameters to act as compensators for missing thermal-storage structure.

Therefore no additional M1 tuning is authorized.

## M2 authorization

The next nested model may add one and only one new structural concept: a second engine solid thermal-storage state.

The planned M2 state vector is:

\[
x_{M2}=[T_{head},T_{slow},T_{hot},T_{cold}]
\]

where:

- `T_head` is the faster combustion-facing/head-dominant engine thermal state;
- `T_slow` is the slower block/structural thermal state;
- `T_hot` remains the engine-out coolant state and ECT observation;
- `T_cold` remains the radiator-return coolant state.

M2 does not yet receive a dynamic thermostat actuator state. That remains reserved for M3 and must be earned separately.

## Required M2 gates

Before any M2 physical-development comparison, the project must freeze and verify:

1. the four-state governing equations and conservation identity;
2. the split of total engine effective thermal capacitance into fast and slow storage;
3. heat partition between the two solid states;
4. conductance topology among head, slow structure, and hot coolant;
5. hidden-state initialization rules for hot starts;
6. limiting cases that collapse M2 back toward M1;
7. synthetic identifiability and parameter-stage restrictions;
8. a new consumed-development feasibility manifest;
9. preservation of the M2 blind reserve.

## Blind-evidence protection

The existing hierarchy freeze remains in force. M1 earns **no** blind execution after this failure.

Reserved evidence remains protected for the higher-order hierarchy. In particular, M2 model development must be completed and preregistered before any M2 blind prediction is generated.

## Supported claim

The supported engineering statement is:

> The governed three-state M1 family failed its preregistered joint development envelope. Explicit hot/cold coolant separation alone is insufficient, so the minimum next model-form test is a second engine thermal-storage state while retaining the M1 coolant topology.
