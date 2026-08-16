# KIT Automotive OBD-II Dataset Audit

## Status

**Metadata audit: complete. File-level signal screening: partial. Formal VTMS validation suitability: insufficient by itself.**

The Karlsruhe Institute of Technology Automotive OBD-II Dataset is being used only as an independent, real-world plausibility source while the project waits for the controlled Argonne D3 dynamometer data requested for formal validation.

## Official dataset provenance

- Creator: Marc Weber
- Institution: Karlsruhe Institute of Technology (KIT)
- Official KITopen identifier: 1000085073
- RADAR DOI: 10.35097/1130
- License: CC BY 4.0
- Collection period reported by KITopen: 2017-07-05 through 2018-04-23
- Archive size reported by RADAR4KIT: 11.6 MB
- Acquisition: KIWI 3 OBD-II dongle with OBD Auto Doctor on iOS

Official metadata pages:

- https://publikationen.bibliothek.kit.edu/1000085073
- https://radar.kit.edu/radar/en/dataset/bCtGxdTklQlfQcAq

## Published channels

KIT documents ten logged OBD-II signals:

1. Engine coolant temperature
2. Intake manifold absolute pressure
3. Engine RPM
4. Vehicle speed
5. Intake air temperature
6. Mass air flow
7. Absolute throttle position
8. Ambient air temperature
9. Accelerator pedal position D
10. Accelerator pedal position E

These channels make the dataset useful for testing the validation pipeline and for checking the gross shape and timing of a coolant warm-up trajectory. The published channel set does not include a directly measured fuel-mass-flow signal, cooling fan state, thermostat position, coolant flow, radiator inlet/outlet temperatures, or HVAC state.

## Repository mirror inventory

A public GitHub mirror of the dataset was inspected at:

https://github.com/hayatu4islam/Automotive_Diagnostics/tree/main/OBD-II-Dataset

The mirror exposes dozens of Seat Leon CSV drives spanning the same 2017-07 through 2018-04 period. Filename labels include normal traffic, `Frei` (free-flow), `Stau` (congestion), `Glatteis` (ice), acceleration, and full-braking conditions. One file is explicitly labeled `Messfehler` (measurement error) and should be excluded from validation work without an independent reason to retain it.

## Source file selected for the first pipeline test

`2018-02-20_Seat_Leon_KA_KA_Frei.csv`

This file was selected because it contains a substantial coolant warm-up trajectory in cool ambient conditions. A coarse 60-second sample extracted from the source file begins at approximately:

- coolant: 18 °C
- ambient: 8 °C
- engine speed: 1040 rpm
- vehicle speed: 18 km/h

and reaches approximately 90 °C coolant after 17 minutes.

The sampled input file included with this toolkit contains 18 representative points from 19:24 through 19:41.

## Important source-data behavior

The OBD file should be treated as an asynchronous telemetry log. Individual PIDs do not necessarily update at the same instant. The full `KITAdapter` therefore:

1. parses native timestamps,
2. preserves timestamp order,
3. forward-fills only the most recently observed value for each required PID after that PID has appeared,
4. converts vehicle speed from km/h to m/s,
5. preserves the original measured coolant trajectory separately from model predictions.

This is preferable to assuming every repeated CSV row represents a new simultaneous observation of every signal.

## Why KIT is not the primary calibration dataset

The dataset is not a controlled thermal validation experiment. Key limitations are:

- no directly measured fuel flow in the published ten-channel schema,
- no documented coolant-system component instrumentation,
- no fan command or thermostat signal,
- no known cabin HVAC/heater-core state,
- road-driving disturbances rather than a prescribed dynamometer cycle,
- vehicle-specific thermal parameters are unknown,
- coolant sensor location is not mapped to the VTMS lumped coolant state,
- a road run may begin from a partially warmed engine even when coolant is relatively cool.

Therefore KIT is classified as **external plausibility evidence**, not the preregistered pass/fail validation source.

## Heat-input treatment for KIT only

Because no measured fuel-rate channel is available in the published schema, the toolkit contains an explicitly secondary heat proxy:

`fuel_rate_estimate = MAF / 14.7`

`Q_engine_estimate = fuel_rate_estimate × 43.7 MJ/kg × 0.28`

The 14.7:1 air-fuel ratio is a gasoline stoichiometric approximation, not a measured lambda value. The 43.7 MJ/kg value is a representative net heat of combustion from a NIST gasoline test. The 0.28 wall-heat fraction is the unchanged VTMS-V1 parameter.

This proxy can be wrong during enrichment, deceleration fuel cut, EGR operation, transient air-path behavior, and any condition where measured MAF is not a direct surrogate for stoichiometric combustion air. The derived fuel rate SHALL NOT be labeled measured fuel consumption.

## First untouched comparison result

VTMS-V1 was run with the existing frozen parameter set. No calibration was performed.

Using the coarse 60-second sample and MAF heat proxy:

- RMSE: 21.40 °C
- MAE: 16.50 °C
- Bias, predicted minus measured: +16.13 °C
- Maximum absolute error: 40.46 °C
- P90 absolute error: 36.50 °C
- 60 °C crossing: VTMS about 276 s early
- 80 °C crossing: VTMS about 496 s early
- 90 °C crossing: VTMS about 273 s early
- Final measured coolant: 90.00 °C
- Final predicted coolant: 89.21 °C

The model reaches its regulated temperature region much too quickly in this comparison, even though the final temperature is close.

## Interpretation

This result is useful because it demonstrates that the validation pipeline can expose a major transient mismatch. It does **not** justify changing the V1 parameters yet.

At least four explanations remain confounded:

1. The MAF-to-fuel heat proxy may overstate combustion heat during portions of the run.
2. The generic engine thermal capacitance and wall-heat partition may not resemble the Seat Leon.
3. The effective engine-structure initial temperature was assumed equal to initial coolant temperature.
4. VTMS-V1 omits heater-core, oil-circuit, A/C/condenser, and other thermal loads that can materially alter warm-up.

The correct action is to preserve this mismatch as evidence, not tune it away.

## Dataset qualification decision

| Use | Decision |
|---|---|
| Validation-pipeline development | ACCEPT |
| External real-world plausibility checks | ACCEPT WITH LIMITATIONS |
| Parameter calibration | REJECT for V1 formal protocol |
| Blind pass/fail physical validation | REJECT |
| Replacement for Argonne controlled data | REJECT |

## Next qualification step

When full native files are locally available, batch-screen all drives for initial coolant-to-ambient temperature difference, duration, coolant temperature rise, RPM completeness, speed completeness, MAF completeness, ambient completeness, obvious sensor discontinuities, and files explicitly marked with measurement errors.

That batch audit should rank candidate warm-up and hot-running traces but should not alter the preregistered Argonne validation hierarchy.
