# KIT External Plausibility Comparison

## Classification

**External plausibility check only. Not formal VTMS validation.**

VTMS-V1 parameters were not changed or calibrated for this comparison. The source is a real KIT Seat Leon OBD-II drive, represented here by 60-second samples extracted from the source CSV. Engine heat input is not measured. It is estimated from measured mass-air flow using a fixed 14.7:1 air-fuel mass ratio, gasoline lower heating value of 43.7 MJ/kg, and the frozen VTMS wall-heat fraction of 0.28.

## Results

- Samples: 18
- Duration: 1020 s
- RMSE: 21.40 °C
- MAE: 16.50 °C
- Bias (predicted minus measured): 16.13 °C
- Maximum absolute error: 40.46 °C
- 90th-percentile absolute error: 36.50 °C
- Final measured coolant temperature: 90.00 °C
- Final predicted coolant temperature: 89.21 °C
- Final error: -0.79 °C
- 60 °C arrival error: -276.46644334983773 s
- 80 °C arrival error: -496.2444710131209 s
- 90 °C arrival error: -273.3571827760827 s

## What this can tell us

This comparison can reveal order-of-magnitude warm-up errors, directional inconsistencies, adapter problems, and gross mismatches between generic VTMS behavior and a real vehicle temperature trajectory.

## What this cannot tell us

It cannot establish vehicle-specific physical accuracy. The Seat Leon is not the generic VTMS reference vehicle, heat input is derived rather than directly measured, the data used here are coarse 60-second samples, HVAC state is unknown, and the source is a road drive rather than a controlled dynamometer test. The preregistered Argonne protocol remains the formal validation path.
