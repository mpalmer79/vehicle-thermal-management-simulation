# VTMS-V2 Argonne Cooling-Air Boundary Audit

## Status

**Development evidence and input-boundary correction. Not a V2 validation result.**

This audit records a mismatch between the frozen VTMS-V1 airflow boundary and the documented Argonne test-cell setup for key consumed runs.

## V1 airflow boundary

VTMS-V1 currently maps:

```text
Dyno_Spd[mph] -> vehicle_speed_m_s
```

and then computes ram airflow from vehicle speed:

```text
V_dot_ram = ram_capture_coefficient * radiator_face_area * vehicle_speed
```

Fan airflow is added through the V1 internal fan controller.

This construction implicitly treats dyno roller speed as a proxy for road-relative radiator airflow.

## Argonne public master-summary evidence

The public 2012 Ford Focus Argonne package includes a master-summary table recording test-cell and vehicle setup.

For the following V1 controlled runs, the table records:

| V1 role | Test ID | Cycle | Cooling-fan setup | Hood |
|---|---:|---|---|---|
| CAL-01 | 71207062 | UDDS cold start | constant speed | up |
| VAL-HOT-01 | 71207063 | UDDS hot start | constant speed | up |

The same public summary table also identifies constant-speed cooling and hood-up setup for other standard tests in that sequence.

The table does not provide a row for every consumed V1 test, so this record does not infer the setup for CAL-RAD-01 71207057 or VAL-SSS-01 71207052 without separate evidence.

## Argonne methodology context

Argonne methodology distinguishes two cooling setups:

1. speed-matched fan with hood closed, intended to approximate road conditions;
2. certification-style constant-speed fan with hood open for comparison/certification testing.

Therefore `Dyno_Spd` is not a universal cooling-air boundary even within Argonne testing.

## Consequence for V1 interpretation

For CAL-01 and VAL-HOT, the V1 airflow boundary is not a faithful representation of the documented test-cell cooling setup.

The V1 model changes calculated ram airflow continuously with dyno speed while the test record says the external vehicle cooling fan was operated at constant speed.

This means radiator UA and other V1 parameters were calibrated/evaluated while carrying an unmodeled airflow-boundary discrepancy.

The preserved V1 formal outcomes remain valid as statements about the frozen V1 implementation. This audit changes the interpretation of why the model failed, not the historical result.

## Important directionality caution

The boundary mismatch does not automatically explain the cold bias.

A constant external fan can provide more or less effective radiator-core airflow than the V1 speed surrogate depending on fan setting, grille restriction, shutter position, hood position, recirculation, and cooling-pack pressure loss.

Do not infer a corrected radiator heat-rejection rate until the actual fan boundary is quantified.

## Active grille shutter interaction

The 2012 Focus platform includes an active grille shutter system when equipped. Ford workshop documentation states that the PCM commands the shutters using inputs including coolant temperature, vehicle speed, fan state, and engine oil temperature.

If the Argonne test vehicle had active grille shutters, then effective radiator-core airflow during a constant-speed external-fan test could still vary dynamically because the vehicle itself modulates the upstream restriction.

VTMS-V1 contains no grille-shutter model.

This creates a potentially important control path:

```text
ECT / oil / speed / other PCM inputs
            -> grille shutter command
            -> cooling-pack airflow restriction
            -> radiator heat rejection
            -> ECT
```

A post-hoc thermostat-threshold shift can numerically mimic reduced radiator heat rejection, so omitted grille-airflow control is a credible alternative explanation for some of the thermostat-counterfactual leverage.

## Airflow attenuation falsification

A consumed-data diagnostic scaled both V1 ram and fan airflow capacity together while leaving the rest of the final staged model fixed.

| Airflow scale | VAL-HOT RMSE C | VAL-SSS RMSE C |
|---:|---:|---:|
| 1.0 | 8.584 | 5.130 |
| 0.5 | 8.475 | 5.000 |
| 0.2 | 7.995 | 4.334 |
| 0.1 | 5.914 | 2.888 |

Even extreme attenuation does not fully resolve VAL-HOT under the existing V1 topology. Therefore a simple constant airflow multiplier is not the sole missing mechanism.

The test does show that cooling-air control has meaningful leverage and should not be hidden inside radiator UA.

## M0 requirement

Before executing the V2-M0 falsification baseline, each development run must receive an explicit airflow-boundary classification:

```text
SPEED_MATCHED_EXTERNAL_FAN
CONSTANT_SPEED_EXTERNAL_FAN
MEASURED_CORE_AIRFLOW
OTHER_DOCUMENTED_BOUNDARY
UNKNOWN
```

Required metadata include, where available:

- hood position;
- external fan mode;
- external fan setting or air-speed/flow value;
- active grille shutter equipment status;
- active grille shutter command/position if measured;
- vehicle internal cooling-fan command/state;
- A/C operating state;
- ambient cell temperature.

`Dyno_Spd` may still be retained as a vehicle operating signal, but it must not automatically define radiator airflow for constant-fan tests.

## M0 modeling policy

### Constant-speed external fan

Use an explicit constant test-cell cooling-air boundary or a documented fan-to-core transfer surrogate. Do not derive it from dyno speed.

### Speed-matched external fan

Use the documented fan command/air-speed relation if available. Dyno speed may be an input to that boundary only because the test equipment was commanded to match it.

### Active grille shutters

If confirmed on the Argonne vehicle, model shutter effect as a separate upstream airflow-control factor or commanded restriction. Do not bury it inside radiator UA.

### Unknown airflow magnitude

Treat airflow as an uncertainty/bounded nuisance input. Do not calibrate radiator UA freely against the same trace and then interpret the result as a physical radiator constant.

## Revised diagnosis

This audit strengthens the decision to run V2-M0 before adding thermal states.

M0 must correct three coupled control/boundary assumptions first:

1. vehicle-specific thermostat behavior;
2. radiator/bypass hydraulic flow split;
3. documented test-cell/vehicle cooling-air control, including active grille shutters if equipped.

Only after these boundaries are frozen can failure of the two-state thermal topology be cleanly attributed to missing thermal states.

## Data gap

The exact constant-fan magnitude for 71207062 and 71207063 is not frozen in the current VTMS mapping record.

Argonne's general methodology describes certification-style constant-fan procedures, but the exact test-specific value must be confirmed from the source test documentation before M0 physical execution.

The cooling setup for 71207057 and 71207052 also requires separate confirmation.
