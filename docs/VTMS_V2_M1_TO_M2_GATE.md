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

## Synthetic gate before physical development

M1 passed synthetic verification and synthetic prefit identifiability with stage restrictions. The hot/cold capacitance partition produced a distinguishable ECT signature, while radiator UA and `f_open` remained nearly collinear. The project therefore prohibited a single all-parameter optimizer and used a preregistered feasibility envelope.

## Physical-development evidence

Only previously consumed tests were used:

- 71207062, cold-start development;
- 71207063, hot-start development.

No reserved M1/M2/M3 blind source was opened for model prediction.

Hot-start hidden-state cases were frozen as:

- `T_engine(0) - ECT(0)` in `{0, 10, 20} C`;
- `T_cold(0) - ECT(0)` in `{0, -5, -10} C`.

These were fixed sensitivity cases, not per-run fitted states.

## Stage A

Stage A evaluated 180 structural/thermal configurations at the frozen central control boundary:

- cold-start passes: **6 / 180**;
- hot-start passes under any initialization: **0 / 180**;
- conditional joint survivors: **0**;
- robust joint survivors: **0**.

The frozen rule therefore opened Stage B.

## Stage B

Stage B crossed the same 180 structural cases with 243 preregistered control cases:

\[
180\times243=43{,}740
\]

The control envelope included:

- thermostat full-open temperature: 97.0, 99.5, 102.0 C;
- `eta_pack`: 0.25, 0.40, 0.80;
- radiator UA: 400, 1100, 2200 W/K;
- `f_open`: 0.85, 0.95, 1.0;
- `gamma`: 0.5, 1.0, 2.0.

The exact joint-feasibility predicate was evaluated cold-first. This changes computation order only. Any joint survivor must satisfy both traces, so a cold failure can be discarded before hot evaluation without changing the joint set.

### Corrected cold-screen result

A post-execution acceptance audit compared the local batch helper with the repository's formal arrival-time semantics. The repository correctly requires a **FAIL** when the measured trace reaches an evaluable temperature threshold but the prediction never reaches it.

Re-evaluating the 2,957 originally retained cold candidates with that strict rule produced:

- **2,753 / 43,740** strict cold-start passes;
- pass fraction: **6.2940%**.

The corrected segment counts are 366, 543, 586, 253, 513, and 492 for the six 7,290-configuration segments.

The original hot screen had already evaluated the full 2,957-configuration superset under all nine hidden-state initializations and found **zero hot-start passes in every initialization case**. Because the corrected 2,753 configurations are a subset of that already-tested superset, the strict hot survivor count is necessarily also zero. A hot rerun cannot create a survivor and is not required for the decision.

Therefore:

- conditional joint survivors: **0**;
- robust joint survivors: **0**;
- strict joint feasible set: **empty**.

## Execution corrections

Three audit corrections are preserved in the development record.

1. An initial Stage B grid used `f_open=0.925` and omitted the Stage A reference `0.95`. That partial calculation was invalidated, the nested grid was restored, and Stage B was restarted.
2. An initial helper applied the 96-100 C criterion before enforcing its separate 30-second coverage requirement. That partial calculation was invalidated, the frozen coverage rule was restored, and Stage B was restarted.
3. The final batch helper did not explicitly fail an evaluable arrival threshold when the prediction never crossed it. Rechecking the previously retained cold candidates reduced the cold pass count from 2,957 to 2,753. The M1 rejection is invariant because the larger 2,957-case hot-screen superset already had zero passes under every initialization.

The authoritative detailed record is `validation_outputs/VTMS_V2_M1_DEV_01_RESULT.json`.

## Interpretation

The result does **not** prove every conceivable three-state automotive thermal model impossible. It establishes the narrower model-selection conclusion required by this hierarchy: hot/cold coolant separation alone cannot reconcile the consumed cold-start and hot-start evidence inside the frozen M1 structural, thermal, control, and hidden-state envelopes.

Further M1 tuning is therefore prohibited.

## M2 authorization

The next nested model adds one and only one new structural concept: a second engine solid thermal-storage state.

\[
x_{M2}=[T_{head},T_{slow},T_{hot},T_{cold}]
\]

M2 retains the M1 coolant topology and static thermostat. A dynamic thermostat state remains reserved for M3 and must be earned separately.

## Blind-evidence protection

M1 earns no blind execution after this failure. Reserved evidence remains protected for the higher-order hierarchy, and M2 development must be completed and preregistered before any M2 blind prediction is generated.

## Supported claim

> The governed three-state M1 family failed its preregistered joint development envelope under strict repository acceptance semantics. Explicit hot/cold coolant separation alone is insufficient, so the minimum next model-form test is a second engine thermal-storage state while retaining the M1 coolant topology.
