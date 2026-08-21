# VTMS-V2 Residual Traceability Record

## Status

**Development evidence record. Not a validation result.**

This record provides a compact trace from preserved VTMS-V1 evidence to the model-form changes proposed in `VTMS_V2_MODEL_FORM_REVISION_SPEC.md`.

| Evidence | Observed V1 behavior | Inference | V2 requirement | Confidence |
|---|---|---|---|---|
| CAL-01 | `wall_heat_fraction` = 0.4999228433, nearly upper bound | one constant heat-partition term is compensating for omitted thermal structure/operating dependence | bounded operating-dependent fuel-energy heat partition | high |
| CAL-01 | `engine_coolant_ua_w_per_k` = 2198.4326 W/K, nearly upper bound | one engine structural state cannot reproduce all engine-to-coolant time scales | fast and slow engine structural states | high |
| KIT plausibility | 60 degC about 276 s early, 80 degC about 496 s early, final error only -0.79 degC | transient thermal storage is wrong even when final operating region is plausible | at least two structural thermal time scales | high |
| CAL-RAD-01 | radiator UA = 400.8325 W/K, nearly lower bound, yet final coolant still -5.12 degC | constant radiator UA plus V1 airflow/control topology over-rejects heat or misrepresents the regulated state | flow-dependent radiator conductance and explicit airflow boundary | high |
| VAL-HOT-01 | mean bias -8.04 degC and final error -8.53 degC | failure is systematic, not dominated by random transient noise | revise hot-region state/control topology | very high |
| VAL-HOT-01 | 90 degC arrival 125.6 s late | hot-start hidden state and regulation behavior are not captured | state-aware initialization plus thermostat/coolant-loop revision | high |
| VAL-SSS-01 | 80/90 degC arrival within 17.3/23.8 s, but final error -8.42 degC | warm-up timing alone is not the dominant defect; V1 settles to the wrong regulated temperature | separate hot/cold coolant states and revise thermostat/radiator flow topology | very high |
| V1 thermostat implementation | valve opening is instantaneous and linear in one bulk coolant state | actuator dynamics and local hot-side sensing are absent | dynamic hysteretic thermostat state sensing `T_hot` | high |
| V1 flow split | radiator mass-flow fraction equals thermostat opening | valve position is incorrectly treated as hydraulic flow fraction | nonlinear or pressure-loss-based radiator/bypass split | very high |
| V1 validation boundary | Argonne dyno speed becomes V1 ram-air input | roller speed is not itself cooling-pack face velocity | explicit/provenanced cooling-pack airflow boundary | high |
| V1 hot-start initialization | hidden engine state defaults to measured coolant temperature | stored metal heat is discarded at start of preconditioned/hot runs | preconditioned or governed estimated state initialization | high for early transient error |

## Interpretation limits

This table identifies the minimum model-form changes supported by current evidence. It does not prove that each proposed subsystem is uniquely responsible for a particular number of degrees of residual error.

Several effects are coupled. In particular:

- radiator UA and cooling-pack airflow are not independently identifiable from ECT alone,
- thermostat opening behavior and radiator/bypass hydraulic split are coupled,
- structural capacitances and engine-to-coolant conductances can be correlated,
- heat-partition parameters can compensate for structural storage if fitted simultaneously.

For that reason, V2 shall use staged calibration, synthetic identifiability, additional observables where available, and strong parameter governance rather than a single unrestricted optimizer.

## Highest-priority V2 changes

1. split coolant into engine-out/hot-side and radiator-return/cold-side states,
2. add a dynamic hysteretic thermostat state,
3. decouple thermostat position from radiator branch-flow fraction,
4. make cooling-pack airflow an explicit validation boundary,
5. make radiator conductance flow-dependent,
6. split engine structure into fast and slow thermal states,
7. use a bounded operating-dependent heat-partition model,
8. add governed initialization for hidden thermal states.
