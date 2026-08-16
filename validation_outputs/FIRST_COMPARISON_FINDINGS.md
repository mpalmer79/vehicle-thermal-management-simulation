# First Real-World Comparison Findings

The first external comparison used an untouched VTMS-V1 parameter set against a coarse 60-second sample from the KIT `2018-02-20_Seat_Leon_KA_KA_Frei.csv` road log.

## Result

The predicted warm-up is substantially faster than the measured coolant trace:

- RMSE: 21.40 °C
- MAE: 16.50 °C
- mean bias: +16.13 °C
- maximum absolute error: 40.46 °C
- 60 °C arrival: approximately 276 seconds early
- 80 °C arrival: approximately 496 seconds early
- final error after 1020 seconds: -0.79 °C

The shape indicates that VTMS enters its temperature-regulation region much earlier than the sampled real vehicle, then converges to a similar final coolant temperature.

## Engineering interpretation

Do not recalibrate to this run.

The mismatch is currently confounded by the MAF-based heat estimate, generic reference parameters, an assumed engine-structure initial temperature, and unmodeled thermal sinks. The purpose of this comparison is to prove the toolkit can expose such discrepancies before controlled validation data arrive.

## Decision

- Pipeline: working
- Model equations: unchanged
- V1 parameters: unchanged
- KIT formal validation status: not applicable
- Argonne protocol: unchanged
