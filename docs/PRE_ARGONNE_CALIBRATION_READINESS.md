# VTMS Pre-Argonne Calibration Readiness

## Status

**Physical calibration remains blocked. No Argonne model residual has been evaluated. Physical calibration bounds are not yet frozen.**

The synthetic pre-fit identifiability gate is implemented and has produced its first governed result. The four-parameter local sensitivity matrix is numerically full-rank, but the warm-up profiles provide very weak excitation of `radiator_ua_nominal_w_per_k`. A four-parameter simultaneous CAL-01 fit is therefore prohibited.

The resulting staged calibration roles have now been frozen before residual inspection:

- `CAL-01`: Argonne test 71207062, fitted subset limited to `wall_heat_fraction`, `engine_thermal_capacitance_j_per_k`, and `engine_coolant_ua_w_per_k`.
- `CAL-RAD-01`: Argonne test 71207057, fitted subset limited to `radiator_ua_nominal_w_per_k` after the CAL-01 snapshot is frozen.
- `VAL-HOT-01`: 71207063 remains an untouched holdout.
- `VAL-SSS-01`: 71207052 remains an untouched secondary holdout.

This document records the engineering basis for those decisions before any Argonne model prediction is compared with measured ECT.

## Governance-approved calibration universe

The overall calibration universe remains unchanged:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

No fifth parameter is introduced. The parameters are now split across two calibration runs because the pre-fit diagnostic shows they are not equally informed by the same operating regime.

## Why literature values cannot simply be copied into VTMS

### Wall heat fraction

In controlled execution VTMS applies:

```text
Q_engine = wall_heat_fraction * fuel_energy_rate
```

`wall_heat_fraction` is therefore the fraction of fuel-energy rate entering the effective engine thermal state. It is **not** identical to the fraction of fuel energy measured later at the coolant boundary.

Kaltakkiran, Ceviz, and Bakirci experimentally studied a gasoline Ford EFI spark-ignition engine throughout warm-up and showed that the energy distribution changes during the transient and changes again when the cooling, oil, and exhaust thermal-management paths are altered. Their reference thermostat opening time changed from 252 s to 218 s when coolant was not routed through the oil cooler, and another strategy reduced warm-up time by about 30 percent. That evidence supports treating the VTMS wall fraction as an effective transient model parameter rather than a universal coolant-loss percentage.

**Bound status:** unresolved. The mathematical constraint `0 <= wall_heat_fraction <= 1` is necessary but far too broad to qualify as a physically useful calibration envelope.

### Effective engine thermal capacitance

VTMS represents the engine structure with one state and one effective thermal capacitance:

```text
C_e * dT_e/dt = Q_engine - Q_ec - Q_ea
```

Kaplan and Heywood's spark-ignition warm-up model explicitly used lumped thermal capacitance methods for major engine components while separately representing coolant and oil heat transfer. That supports the reduced-order modeling approach, but it does not provide a vehicle-independent value for a single aggregate `C_e`. A VTMS value necessarily absorbs the mass, material heat capacities, spatial temperature nonuniformity, and omitted thermal nodes represented by the single state.

**Bound status:** unresolved. Positivity is a hard physical constraint, not a sufficient calibration range.

### Engine-to-coolant effective conductance

VTMS uses:

```text
Q_ec = UA_ec * (T_e - T_c)
```

The Argonne evidence provides engine coolant temperature but does not directly measure the VTMS effective engine-structure state `T_e`. As a result, `UA_ec`, `C_e`, and wall heat fraction can trade against one another while producing partially similar coolant-temperature responses. That is an identifiability question and must be tested before their ranges are frozen.

**Bound status:** unresolved. Positivity is necessary but not sufficient.

### Nominal radiator UA

VTMS uses one nominal radiator conductance inside an effectiveness-NTU calculation. Real automotive radiators do not have one universal flow-independent heat-transfer coefficient.

Taler experimentally characterized an automotive radiator used with a 1.58 L spark-ignition engine. The study used 57 measured operating points, four air velocities from 1.0 to 2.2 m/s, measured liquid and air temperatures and flows, and nonlinear least-squares estimation of heat-transfer correlations. The paper explicitly constructs a Jacobian of calculated outlet temperatures with respect to unknown heat-transfer parameters and evaluates its derivatives by finite differences. The experiment also reports water/air heat-rate closure within four percent.

That evidence supports treating VTMS `radiator_ua_nominal_w_per_k` as a calibrated effective nominal parameter for the frozen reduced-order radiator, not as a literal universal radiator property that can be copied from another vehicle.

**Bound status:** unresolved. Positivity is necessary but not sufficient.

## Pre-fit identifiability diagnostic

`src/vtms_validation/identifiability.py` implements a local, synthetic-only sensitivity analysis around the generic VTMS-V1 parameter snapshot.

For each of the four frozen parameters it performs a central relative perturbation and computes:

```text
S_j(t) ~= [T_c(p_j*(1+h)) - T_c(p_j*(1-h))] / (2*h)
```

where `h = 0.01` by default. This approximates `p_j * dT_c/dp_j`, so parameters with different engineering units can be compared on a fractional-change basis.

The diagnostic reports:

- RMS, maximum absolute, and L2 sensitivity for each parameter
- each parameter's RMS sensitivity relative to the strongest parameter in that profile
- pairwise cosine similarity between sensitivity histories
- singular values of the column-normalized sensitivity matrix
- numerical matrix rank
- condition number of the normalized matrix
- explicit diagnostic flags for zero local sensitivity, weak relative sensitivity, rank deficiency, high pairwise shape similarity, or strong ill-conditioning

The current diagnostic thresholds are **VTMS engineering heuristics only**, not SAE, Argonne, or literature acceptance standards:

- pairwise `|cosine| >= 0.95`: high sensitivity-shape similarity
- normalized condition number `>= 100`: strong ill-conditioning
- RMS sensitivity `< 2%` of the strongest parameter: weak practical excitation

Most importantly, the function rejects any dataset that is not explicitly marked synthetic and nonphysical. This prevents the identifiability phase from seeing Argonne prediction residuals before physical calibration bounds and evidence roles are frozen.

## Synthetic profiles used

The diagnostic reuses the already-existing deterministic synthetic calibration and holdout operating profiles. The synthetic test-only calibration bounds are not read or used by the identifiability calculation. Perturbations are local percentages around the generic VTMS-V1 snapshot.

The CI runner evaluates:

1. synthetic calibration profile alone
2. synthetic holdout profile alone
3. both profiles combined

## Observed synthetic result

The first CI execution used the generic VTMS-V1 parameter snapshot and a 1 percent central perturbation.

### Synthetic calibration profile, `SYN-CAL-01`

- samples: 61
- numerical rank: 4 of 4
- normalized-matrix condition number: **5.855**
- smallest normalized singular value: **0.1708**
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `|cosine| = 0.7118`

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 6.0726 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 1.4170 | 23.34% |
| `engine_coolant_ua_w_per_k` | 4.0274 | 66.32% |
| `radiator_ua_nominal_w_per_k` | 0.1078 | **1.78%** |

### Synthetic holdout profile, `SYN-HOLD-01`

- samples: 53
- numerical rank: 4 of 4
- normalized-matrix condition number: **10.957**
- smallest normalized singular value: **0.0913**
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `|cosine| = 0.9375`

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 10.4328 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 3.2195 | 30.86% |
| `engine_coolant_ua_w_per_k` | 4.3725 | 41.91% |
| `radiator_ua_nominal_w_per_k` | 0.00461 | **0.044%** |

### Combined synthetic profiles

- samples: 114
- numerical rank: 4 of 4
- normalized-matrix condition number: **8.123**
- normalized singular values relative to the largest: `1.0000, 0.6685, 0.5926, 0.1231`
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `cosine = -0.8800`

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 8.3866 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 2.4276 | 28.95% |
| `engine_coolant_ua_w_per_k` | 4.1914 | 49.98% |
| `radiator_ua_nominal_w_per_k` | 0.07894 | **0.94%** |

### Interpretation

The normalized Jacobian is neither rank deficient nor severely ill-conditioned at this local synthetic point. The four sensitivity histories are mathematically distinct, but `radiator_ua_nominal_w_per_k` produces less than one percent of the strongest RMS coolant response across the combined warm-up profiles. That parameter is therefore not practically supported by the same warm-up fit.

Wall heat fraction and effective engine thermal capacitance also show notable inverse similarity (`cosine = -0.8800` combined and `-0.9375` on the second profile). This is a reason to keep their future physical bounds conservative and to inspect post-fit covariance or profile behavior before treating fitted values as independently identified physical properties.

## Source-only selection of CAL-RAD-01

After the synthetic weak-excitation finding, the received Argonne source measurements were reviewed **without running VTMS predictions** to locate an operating condition that actually exercises the radiator path.

Test `71207057`, identified in the Argonne material as `1.2 HWYx2 ED`, was selected as `CAL-RAD-01` because its post-zero source record has:

- 12,876 samples through 1287.5 s
- complete ECT coverage
- ECT range **91 to 99 °C**
- no greater-than-10 °C ECT sample jump
- average dyno speed **57.31 mph**
- maximum dyno speed **71.742 mph**
- **92.653%** of samples at or above 40 mph
- **92.653%** of samples simultaneously at ECT >= 88 °C and speed >= 40 mph

These are measured source conditions only. They were not selected because VTMS fit this test well or poorly. No VTMS residual for 71207057 has been observed.

The mapping and role reservation are frozen in `validation_configs/argonne_2012_focus_71207057_radiator_calibration.json` and `validation_configs/argonne_validation_plan.json`.

## Frozen staged calibration structure

### CAL-01, warm-up stage

Source test: **71207062**, cold-start UDDS #1.

Manifest-declared fitted subset:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`

`radiator_ua_nominal_w_per_k` is explicitly excluded from this fit.

### CAL-RAD-01, radiator stage

Source test: **71207057**, 1.2 highway x2.

Manifest-declared fitted subset:

1. `radiator_ua_nominal_w_per_k`

All non-radiator parameters must come from the frozen CAL-01 output snapshot. CAL-RAD-01 must not reopen or retune the three CAL-01 parameters.

### Holdout protection

- `VAL-HOT-01`, test 71207063, remains reserved as an independent holdout.
- `VAL-SSS-01`, test 71207052, remains reserved as a secondary independent holdout.

Neither was repurposed after the identifiability finding.

## Decision rule for the next phase

The calibration structure is now frozen, but **neither physical fit is authorized yet**.

Before CAL-01 can run, the project must still:

1. establish a documented engineering basis for finite physical bounds on its three fitted parameters,
2. freeze those bounds without reference to Argonne residuals,
3. freeze the CAL-01 mapping/preprocessing configuration and exact hashes,
4. create the immutable CAL-01 manifest,
5. only then execute CAL-01.

Before CAL-RAD-01 can run, the project must additionally:

1. freeze the successful or otherwise governed CAL-01 output snapshot,
2. establish and freeze a physical bound for radiator UA,
3. freeze the 71207057 normalized mapping/preprocessing hash,
4. create an immutable radiator-only calibration manifest referencing the frozen upstream snapshot,
5. only then execute CAL-RAD-01.

The synthetic identifiability concern is useful evidence that the calibration problem should be staged rather than allowing a four-variable optimizer to absorb model mismatch indiscriminately.

## Primary technical sources

- Kaplan, J. A., & Heywood, J. B. (1991). *Modeling the Spark Ignition Engine Warm-Up Process to Predict Component Temperatures and Hydrocarbon Emissions*. SAE Technical Paper 910302. DOI: 10.4271/910302.
- Kaltakkiran, G., Ceviz, M. A., & Bakirci, K. (2022). *Instantaneous energy balance and performance analysis during warm up period of a spark ignition engine under several thermal energy management strategies*. Energy Conversion and Management, 269, 116102. DOI: 10.1016/j.enconman.2022.116102.
- Taler, D. (2013). *Experimental determination of correlations for average heat transfer coefficients in heat exchangers on both fluid sides*. Heat and Mass Transfer, 49, 1125-1139. DOI: 10.1007/s00231-013-1148-5.

## Evidence boundary

Nothing in this document is an Argonne calibration result. Nothing here changes VTMS-V1 equations, the generic parameter snapshot, the formal acceptance thresholds, or the reserved holdout roles. VTMS-V1 remains `numerical_verified_generic_uncalibrated`.
