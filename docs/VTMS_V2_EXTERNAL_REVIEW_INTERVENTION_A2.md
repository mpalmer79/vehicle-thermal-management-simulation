# VTMS-V2 External Review Intervention A2

## Status

**Frozen before radiator root-cause diagnosis.**

This amendment pauses further VTMS-V2-M2 Stage B execution without rejecting M2, promoting M3, changing any frozen acceptance threshold, or opening any reserved blind evidence.

## Why this amendment exists

An independent staff-level engineering review performed on 2026-08-22 identified the constant-radiator-UA formulation as a specific lower-order model-form hypothesis that should be tested before the project spends additional computation on higher-order thermal-state topology.

The active M2 thermal model still delegates radiator heat exchange to the VTMS-V1 `RadiatorModel`, where effective UA is constant with air and coolant mass flow except for the multiplicative health factor. M0, M1, and M2 therefore share this radiator limitation even though M0 corrected the Argonne airflow-boundary treatment and radiator/bypass flow split.

The review hypothesis is **not accepted as fact** by this amendment. In particular, the earlier V1 interpretation that low vehicle/dyno speed implied low radiator-core airflow is not transferable to the documented Argonne constant-speed external-fan cases. The V2 airflow boundary explicitly prohibits dyno speed from silently becoming core airflow for those runs.

The proper next question is therefore narrower:

> Does a physically bounded, flow-dependent radiator-UA formulation explain residual structure on already-consumed development evidence after the corrected V2 airflow boundary is retained?

## M2 disposition at the intervention point

M2 remains an active, unrejected model-form family.

The last repository-committed authoritative independent Stage B checkpoint is:

- `validation_outputs/VTMS_V2_M2_STAGE_B_INDEPENDENT_RESTART_CHECKPOINT_2K.json`
- contiguous global Stage B prefix: 0 through 1,999
- independent four-state SciPy RK45 integration per configuration
- cold-start passes: 0 / 2,000
- hot-start evaluations required in that prefix: 0
- M2 rejection: not authorized
- M3 promotion: not authorized

Additional local Stage B work beyond that checkpoint is not promoted into the scientific record by this amendment because the exact local scalar enumeration harness and checkpoint state were not preserved as a fully reproducible committed execution artifact. Near the discontinuous 90 C arrival-time criterion, small numerical/execution differences can alter classifications. The project therefore falls back to the last durable committed independent checkpoint rather than reconstructing or inferring missing results after the fact.

No result from the superseded vectorized 116k checkpoint is restored to gate evidence.

## Frozen intervention rules

1. **M2 Stage B is paused, not failed.**
2. **M3 is not authorized.** Dynamic thermostat lag or hysteresis cannot be added under this amendment.
3. **No reserved blind prediction may be generated or inspected.**
4. **No M2 parameter range or acceptance threshold may be changed.**
5. **No consumed residual may be used to widen a radiator hypothesis range after results are inspected.**
6. **VTMS-V1 production physics and its published validation record remain unchanged.**
7. **The radiator investigation must start with residual localization and provenance/bounds freeze before a new radiator law is executed on physical development traces.**
8. **The lowest-order governed topology must be tested first.** A more complex thermal-state model may not receive preferential treatment simply because it already exists.
9. **If the flow-dependent-UA hypothesis is falsified or materially non-explanatory, M2 Stage B resumes from the durable independent checkpoint under its existing numerical execution amendment and frozen grid.**
10. **If the hypothesis earns promotion, the V2 hierarchy must be explicitly rebased in a new frozen model-form record. Earlier M0/M1/M2 results remain historically valid for the constant-UA family and are not rewritten.**

## Radiator root-cause gate sequence

### Gate RAD-D0: diagnostic provenance freeze

Before any new model-form execution, freeze:

- consumed run identities and source hashes
- retained row-selection rules
- corrected airflow-boundary class for each run
- residual sign convention
- independent variables to be inspected
- temperature/control regime bins
- any derived radiator quantities permitted in diagnostics
- publication/data-rights classification for any derived trace artifact

### Gate RAD-D1: residual localization

On already-consumed evidence only, produce aggregate diagnostics for at least:

- residual vs time
- residual vs measured ECT
- residual vs modeled radiator air mass flow
- residual vs radiator coolant mass flow
- residual vs radiator heat rejection
- residual vs thermostat position
- residual by 80/88/92/96/100 C temperature regions
- residual vs engine speed and direct fuel-energy input
- residual vs measured oil temperature where available

Vehicle/dyno speed may be plotted as an operating variable but must not be relabeled as radiator-core airflow in constant-fan tests.

Outcome classes:

- `RADIATOR_HYPOTHESIS_SUPPORTED_FOR_MODEL_FORM_TEST`
- `RADIATOR_HYPOTHESIS_INCONCLUSIVE`
- `RADIATOR_HYPOTHESIS_NOT_SUPPORTED`

RAD-D1 does not fit parameters and cannot validate a new radiator model.

### Gate RAD-P0: physical-law and bounds freeze

Only if RAD-D1 supports or leaves the hypothesis materially plausible, perform a source/provenance review and freeze a candidate relation such as:

`UA = UA_ref * (m_air / m_air_ref)^n_air * (m_cool / m_cool_ref)^n_cool`

The exact law, zero-flow treatment, reference flows, exponent bounds, and provenance must be frozen before physical residual fitting. The external review's approximate air-side exponent near 0.65 is a hypothesis-generating prior, not a Ford-specific measured property and not a frozen project value.

### Gate RAD-S0: synthetic verification and identifiability

Before physical development execution, require:

- zero heat transfer at zero air or coolant flow
- effectiveness in [0, 1]
- finite behavior near zero flow
- positive effective UA in its valid domain
- nominal reduction at reference flow
- monotonic heat-rejection behavior over the frozen physical operating domain
- energy conservation
- synthetic sensitivity/identifiability analysis of `UA_ref`, flow exponents, `eta_pack`, and retained hydraulic parameters

Joint fitting of confounded parameters is prohibited unless synthetic identifiability supports it.

### Gate RAD-F0: lowest-order physical feasibility

Use already-consumed physical development evidence only. Start from the smallest corrected V2 topology that can represent the candidate radiator law. Do not start with M2 merely because M2 has already been implemented.

Possible outcomes:

- **Simple corrected topology becomes jointly feasible:** rebase the V2 hierarchy around the earned radiator correction; do not resume the old M2 sweep as the primary path.
- **Radiator correction improves but does not resolve the contradiction:** carry the earned correction into the next-lowest required topology under a separately frozen gate.
- **Radiator correction is non-explanatory:** record falsification and resume the existing M2 Stage B protocol without changing its grid or thresholds.

## Blind evidence remains protected

This intervention does not open, inspect predictions for, or reassign the reserved blind ladder. Source-only qualification remains distinct from prediction inspection.

No blind test becomes development evidence merely because the model hierarchy is being reconsidered.

## Scientific interpretation

The purpose of this amendment is not to follow an external reviewer's preferred model. It is to respond to a specific, physically interpretable criticism with a lower-complexity falsification test before adding further states.

A simpler model with a better heat-exchanger law is preferred over a higher-state model if both explain the consumed evidence. Conversely, if the proposed radiator mechanism does not survive governed testing under the corrected Argonne airflow boundary, the project will preserve that negative result and resume the previously frozen M2 path.
