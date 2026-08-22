# VTMS-V2 Radiator Root-Cause Diagnostic Protocol

## Gate

`VTMS-V2-RAD-D0`

This protocol is frozen before executing the new radiator-focused residual analysis introduced by External Review Intervention A2.

## Question

The diagnostic question is intentionally narrower than "what model fits best?"

> After retaining the corrected V2 airflow boundary, is the temperature residual structure materially associated with the modeled radiator heat-rejection regime in a consistent way across already-consumed Argonne development traces?

The analysis cannot identify a new radiator law, estimate a Ford-specific heat-exchanger property, reopen validation, or authorize a blind prediction.

## Why this gate is necessary

VTMS-V1 uses an effectiveness-NTU radiator with an effective UA that does not vary with air or coolant mass flow except through the radiator-health multiplier. M0 corrected major control-boundary issues, but M0, M1, and M2 still inherit that underlying radiator law.

An external staff engineering review identified this constant-UA formulation as a plausible structural contributor to the observed cold bias. That criticism is physically interpretable but not yet proven for the corrected V2 boundary. The Argonne 71207062 and 71207063 tests are documented constant-speed external-fan cases, so low dyno speed is not evidence of low radiator-core airflow by itself.

The project therefore tests residual localization before changing the radiator model.

## Evidence

Only already-consumed runs are permitted:

| Run | Test | Role in this diagnostic | Airflow interpretation |
|---|---|---|---|
| CAL-01 | 71207062 | consumed cold-start development | constant-speed external fan, hood up |
| CAL-RAD-01 | 71207057 | consumed radiator development | unresolved unless separately documented |
| VAL-HOT-01 | 71207063 | consumed former primary holdout | constant-speed external fan, hood up |
| VAL-SSS-01 | 71207052 | consumed former confirmatory holdout | unresolved unless separately documented |

The frozen SHA-256 fingerprints are stored in `validation_configs/vtms_v2_rad_d0_diagnostic_manifest.json`.

No reserved V2 blind run is permitted.

## Residual convention

`residual = predicted ECT - measured ECT`

Negative values mean VTMS predicts coolant colder than measured.

## Required diagnostic views

### Whole-trace summaries

For every run, retain:

- bias
- MAE
- RMSE
- P90 absolute error
- bias fraction of MSE

### Temperature regime

Compute residual summaries in the frozen measured-ECT regions:

- below 80 C
- 80 to 88 C
- 88 to 92 C
- 92 to 96 C
- 96 to 100 C
- 100 to 130 C

The 88 to 92 C region is retained because prior development evidence showed both holdouts were comparatively accurate there, while the 96 to 100 C region became strongly cold-biased.

### Correlation variables

Compute descriptive correlation with:

- time
- measured ECT
- engine speed
- dyno speed, labelled only as an operating variable
- direct fuel-energy rate
- engine load
- measured oil temperature where available
- modeled thermostat fraction
- modeled radiator coolant flow
- modeled radiator air mass flow
- modeled radiator heat rejection
- modeled radiator effectiveness
- modeled radiator NTU

Pearson correlation is descriptive only. It is not a causal score.

### Frozen binned summaries

Use the bins recorded in the machine manifest for:

- time
- modeled radiator air mass flow
- modeled radiator coolant flow
- modeled radiator heat rejection
- modeled thermostat fraction

Bins may be empty. Empty bins must remain reported rather than silently merged after inspection.

## Required cross-run interpretation

A radiator model-form test is supported only if the complete diagnostic picture is consistent with a heat-rejection mechanism across more than one consumed run.

Examples of supporting structure include, but are not limited to:

- residual magnitude changing systematically with modeled heat-rejection regime
- the strongest cold bias occurring where the constant-UA formulation implies disproportionate rejection
- temperature-region behavior and heat-rejection-region behavior pointing in the same direction
- a radiator-specific relation remaining visible after inspecting engine/load/heat-input variables

The following do **not** by themselves support the hypothesis:

- correlation with dyno speed in a constant-fan test
- a single high Pearson coefficient
- one run improving under a post-hoc radiator parameter change
- a result that depends on relabeling external-fan capacity as measured core flow

## Airflow language rules

For 71207062 and 71207063:

- the boundary class is `CONSTANT_SPEED_EXTERNAL_FAN`
- the known protocol fan capacity is not measured radiator-core flow
- V2's effective core-airflow transfer remains an engineering boundary assumption
- dyno speed must not be substituted for that boundary

For 71207052 and 71207057, unresolved cooling setup must remain explicit unless stronger evidence is independently added.

## Data-rights rule

Raw Argonne rows and row-level reconstructed traces are not committed.

The diagnostic may generate detailed plots locally for engineering inspection, but public measured-trace plots remain blocked until a separate data-rights review determines what derived visualization can be redistributed.

Commit-safe outputs are limited to source hashes, aggregate statistics, frozen bin summaries, and other derived quantities that do not reproduce the raw dataset row by row.

## Outcome classes

### `RADIATOR_HYPOTHESIS_SUPPORTED_FOR_MODEL_FORM_TEST`

The residual structure is sufficiently consistent with heat-rejection regime to justify freezing a physically sourced variable-UA candidate and bounds in RAD-P0.

This does not mean variable UA is proven correct.

### `RADIATOR_HYPOTHESIS_INCONCLUSIVE`

The radiator mechanism remains materially plausible but is confounded by unresolved boundary/control variables. RAD-P0 may proceed, but its uncertainty treatment must explicitly carry those confounders.

### `RADIATOR_HYPOTHESIS_NOT_SUPPORTED`

The preregistered residual diagnostics do not show a consistent radiator-specific signature. The variable-UA intervention stops, the negative finding is preserved, and the previously frozen M2 Stage B path resumes unchanged.

## Prohibited actions during RAD-D0/D1

- parameter fitting
- optimizer execution
- parameter ranking
- widening any physical range from residual inspection
- opening blind evidence
- adding thermostat dynamics
- changing M2 acceptance criteria
- declaring a radiator cause from one diagnostic

## Next gate

If supported or inconclusive, proceed to `VTMS-V2-RAD-P0`, where literature/provenance, candidate equation, reference flows, zero-flow treatment, and all parameter bounds are frozen before any new physical-model execution.
