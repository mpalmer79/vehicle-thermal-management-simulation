# VTMS-V2 Vehicle-Specific Thermal Control Evidence

## Status

**Pre-M0 evidence record. No V2 calibration authorized.**

This document records vehicle-specific thermal-control evidence for the 2012 Ford Focus platform used by the Argonne D3 controlled program. Its purpose is to replace generic control assumptions with sourced boundaries before VTMS-V2 adds thermal states.

## Argonne vehicle identity already frozen by VTMS

The repository inventory identifies the controlled vehicle as:

```text
2012 Ford Focus
2.0 L Ti-VCT GDI inline-four
6-speed automatic
2WD
```

This evidence record does not infer trim or optional equipment that is not established by the Argonne inventory.

## Thermostat assembly identity

Ford parts references identify thermostat assembly:

```text
Ford:      CP9Z-8592-G
Motorcraft: RT-1219
```

for the 2012 Focus 2.0 L DI Ti-VCT application.

A Motorcraft RT-1219 retail specification identifies the part as a **190 F thermostat**, corresponding to approximately **87.8 C** nominal rating.

### M0 implication

The V1 assumed thermostat opening onset of 88 C is close to the independently listed nominal component rating and should not be discarded merely because a higher post-hoc threshold improves consumed residuals.

The Phase 2 counterfactual values around 95 to 98 C opening therefore must be treated as compensating numerical parameters, not identified physical thermostat settings.

### What remains unresolved

A nominal thermostat rating does not define the complete valve-area curve.

Before M0 equation freeze, the project still needs a defensible source or bounded assumption for:

- start-of-opening tolerance;
- full-open temperature;
- opening-area versus temperature relationship;
- closing behavior and hysteresis, if material;
- thermostat-local sensing temperature relative to the measured ECT location.

Do not silently convert the 190 F rating into an arbitrary full-open temperature.

## Active grille shutter system

Ford 2012 Focus workshop documentation describes an active grille shutter system when equipped.

The system is not a passive aerodynamic detail. It is a thermal-control actuator positioned ahead of the radiator.

Documented behavior includes:

- commanded positioning by the PCM;
- approximately 90 degrees of total shutter movement;
- 16 discrete positions from closed to open;
- calibration movement at engine start;
- use for coolant-temperature control and faster warm-up in addition to aerodynamic drag reduction.

Documented PCM inputs/related signals include:

- engine coolant temperature;
- intake air temperature;
- A/C pressure;
- accelerator pedal position;
- vehicle speed through the ABS network;
- engine cooling fan;
- engine oil temperature.

This is directly relevant to VTMS because V1 contains no grille-shutter state or command. Its airflow model converts vehicle/dyno speed and fan command directly into radiator air mass flow.

## Equipment-status gate

The workshop manual qualifies the active grille shutter system as **when equipped**.

The current Argonne inventory establishes engine, transmission, and drivetrain but does not establish the exact trim/equipment code required to prove that the tested vehicle had active grille shutters.

Therefore M0 must not assume either condition.

Before physical M0 execution, classify the Argonne vehicle as one of:

```text
AGS_PRESENT_CONFIRMED
AGS_ABSENT_CONFIRMED
AGS_STATUS_UNRESOLVED
```

Acceptable evidence includes:

- Argonne vehicle configuration record;
- VIN/build-sheet or option-code evidence;
- test documentation explicitly naming active grille shutters;
- physical inspection record from the original test program if available.

## Airflow counterfactual

Phase 2 performed a diagnostic total-airflow attenuation sweep on the consumed holdouts by scaling both V1 ram and fan airflow capacity while leaving the rest of the final staged V1 model unchanged.

This is not an active-grille-shutter calibration. It asks only whether lower cooling-pack airflow has enough leverage to explain the failure by itself.

Selected result:

| Total V1 airflow scale | VAL-HOT RMSE C | VAL-SSS RMSE C |
|---:|---:|---:|
| 1.0 | 8.584 | 5.130 |
| 0.5 | 8.475 | 5.000 |
| 0.2 | 7.995 | 4.334 |
| 0.1 | 5.914 | 2.888 |

Interpretation:

- large airflow attenuation materially improves the secondary steady-speed holdout;
- even an extreme 90% attenuation does not bring VAL-HOT inside the original 5 C RMSE criterion;
- cooling-pack airflow control is therefore a plausible contributor but not a sufficient isolated explanation for both holdout failures.

A real active grille shutter is state- and condition-dependent, so this constant-scale test cannot identify its physical command law.

## Revised M0 thermal-control boundary

M0 should begin with the following evidence hierarchy.

### Thermostat

- nominal opening rating: approximately 88 C, sourced from the exact Ford/Motorcraft application;
- complete opening/full-open curve: unresolved until stronger evidence is obtained;
- post-hoc consumed-residual optimum: prohibited as physical input.

### Radiator/bypass flow split

- V1 identity `radiator_flow_fraction = thermostat_fraction`: rejected as an unsupported hydraulic assumption;
- M0 replacement: bounded monotonic static flow-split law or branch-resistance model with independently constrained coefficients.

### Active grille shutters

- implementation required only if equipment presence is confirmed;
- if present, the shutter becomes an explicit cooling-air boundary/control model rather than being hidden in radiator UA;
- if status remains unresolved, airflow uncertainty must be propagated and no vehicle-specific radiator parameter may absorb it silently.

### Test-cell airflow

- dyno speed is not radiator-core air velocity;
- cell-fan/core-airflow evidence remains a separate boundary requirement even if AGS status is known.

## Model hierarchy consequence

The discovery of a vehicle-level active airflow-control system strengthens the decision to test **M0 before adding states**.

A two-state M0 with corrected control boundaries can falsify whether omitted thermostat/hydraulic/airflow controls account for most of the V1 hot-region error.

If physically sourced M0 control behavior still cannot generalize across cold start, hot start, and steady-speed operation, then M1 hot/cold coolant state separation is promoted under the frozen hierarchy rules.

## Source register

Public evidence reviewed 2026-08-21:

1. Ford 2012 Focus parts catalog fitment for CP9Z-8592-G thermostat assembly.
2. Ford/parts cross-reference identifying CP9Z-8592-G and Motorcraft RT-1219 for the 2.0 L DI Ti-VCT application.
3. Motorcraft RT-1219 product listing identifying the thermostat as 190 F.
4. 2012 Ford Focus workshop-manual active grille shutter description and system-operation documentation.
5. 2012 Focus product/source-book documentation describing active grille shutter availability on the model line.

The repository should retain exact URLs in research notes if long-term source auditing is required. The engineering conclusions above distinguish confirmed vehicle-platform facts from unresolved Argonne test-vehicle equipment status.
