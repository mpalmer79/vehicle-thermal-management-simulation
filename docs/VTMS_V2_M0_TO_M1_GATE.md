# VTMS-V2 M0 Rejection and M1 Promotion Gate

## Decision

**Gate V2-M0-R1: PASS. M0 is rejected as the continuing model form and M1 promotion is authorized.**

This is a model-selection decision based only on already-consumed development evidence. It is not a validation claim and it does not open any reserved blind prediction.

## Evidence chain

VTMS-V2-M0 was intentionally constructed as the strongest defensible two-state corrected-control baseline before adding thermal states. It retained the state vector:

\[
x_{M0}=[T_{engine},T_{coolant}]
\]

while correcting the major V1 control-boundary assumptions: thermostat anchoring, nonlinear radiator/bypass flow split, explicit airflow boundary classes, and bounded external-fan transfer uncertainty.

Synthetic identifiability prohibited a simultaneous five-parameter heat-rejection/control fit. FEAS-01 then tested the frozen corrected-control envelope on consumed cold-start and hot-start development evidence. Although 272 of 810 configurations could satisfy the cold-start run, zero of 810 satisfied the hot-start run.

TFEAS-01 subsequently reopened the full preregistered major two-state thermal envelope rather than preserving the CAL-01 effective thermal snapshot. It crossed 36 thermal configurations with all 810 corrected-control configurations, producing 29,160 M0 configurations.

**TFEAS-01 result: zero of 29,160 configurations satisfied the consumed hot-start acceptance criteria.** The preregistered rule therefore prevented the cold joint-check stage from opening.

## Interpretation

This result does not prove that every conceivable two-state thermal model is impossible. It shows that the governed M0 model family, including the complete frozen thermal and control uncertainty envelope considered physically admissible for this revision, cannot reproduce the consumed hot-start evidence.

Further widening or retuning would violate the preregistered model-selection process and would turn M0 parameters into compensators for missing structure.

Therefore no additional M0 fitting is authorized.

## M1 authorization

The first structural revision is limited to coolant topology:

\[
x_{M1}=[T_{engine},T_{hot},T_{cold}]
\]

where:

- `T_engine` is the effective engine-structure state retained from M0;
- `T_hot` is the engine-out / hot-side coolant control volume and the predicted ECT observation;
- `T_cold` is the radiator-return / cold-side coolant control volume.

M1 does **not** yet add a second engine solid state or a thermostat actuator state. M2 and M3 remain conditional future promotions.

## Blind-evidence protection

The hierarchy freeze remains in force. No reserved blind prediction is authorized by this gate. In particular, source-only blind records remain uninspected for model prediction.

M1 must first pass:

1. equation and parameter freeze;
2. synthetic conservation and limiting-case verification;
3. numerical convergence and deterministic-repeatability checks;
4. synthetic identifiability review;
5. a separately frozen physical-development protocol using only evidence already consumed for development.

Only after those gates may the project decide whether an independent M1 blind rung can be opened.

## Prohibited interpretations

This gate must not be described as:

- physical validation of M1;
- proof that three states are sufficient;
- proof that five states are unnecessary;
- vehicle-specific parameter identification;
- evidence that a specific thermostat, radiator, or airflow parameter is correct.

The supported claim is narrower: **the governed two-state M0 family failed its preregistered development falsification envelope, so the minimum next model-form test is hot/cold coolant separation.**
