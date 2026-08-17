# VTMS Pre-Argonne Calibration Readiness

## Status

**CAL-01 remains blocked. No Argonne model residual has been evaluated. Physical calibration bounds are not yet frozen.**

The synthetic pre-fit identifiability gate is now implemented and has produced its first governed result. The four-parameter local sensitivity matrix is numerically full-rank, but the current warm-up profiles provide very weak excitation of `radiator_ua_nominal_w_per_k`. A four-parameter simultaneous CAL-01 fit is therefore not authorized by this readiness review.

This document records the engineering basis for the pre-fit identifiability gate that must be completed before the 2012 Ford Focus Argonne D3 cold-start calibration run is allowed to influence VTMS-V1 parameters.

The purpose is not to find bounds that make the future fit succeed. The purpose is to determine whether the preregistered effective parameters can be distinguished by the available coolant-temperature observation and to identify what additional physical rationale is required before numerical limits are frozen.

## Frozen calibration subset

The governance-approved calibration universe remains unchanged:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

A calibration manifest may declare a governed subset of these parameters. No fifth parameter is introduced by this work.

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

Most importantly, the function rejects any dataset that is not explicitly marked synthetic and nonphysical. This prevents the identifiability phase from accidentally seeing Argonne prediction residuals before physical calibration bounds and evidence roles are frozen.

## Synthetic profiles used

The diagnostic reuses the already-existing deterministic synthetic calibration and holdout operating profiles. The synthetic test-only calibration bounds are not read or used by the identifiability calculation. Perturbations are local percentages around the generic VTMS-V1 snapshot.

The CI runner evaluates:

1. synthetic calibration profile alone
2. synthetic holdout profile alone
3. both profiles combined

The combined profile is the most informative pre-fit view because it asks whether changes in operating condition improve separation of the four parameter sensitivity shapes.

## Observed synthetic result

The first CI execution used the generic VTMS-V1 parameter snapshot and a 1 percent central perturbation.

### Synthetic calibration profile, `SYN-CAL-01`

- samples: 61
- numerical rank: 4 of 4
- normalized-matrix condition number: **5.855**
- smallest normalized singular value: **0.1708**
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `|cosine| = 0.7118`

RMS coolant-temperature sensitivities per unit fractional parameter change:

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 6.0726 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 1.4170 | 23.34% |
| `engine_coolant_ua_w_per_k` | 4.0274 | 66.32% |
| `radiator_ua_nominal_w_per_k` | 0.1078 | **1.78%** |

The radiator term is already below the 2 percent weak-excitation heuristic in this profile.

### Synthetic holdout profile, `SYN-HOLD-01`

- samples: 53
- numerical rank: 4 of 4
- normalized-matrix condition number: **10.957**
- smallest normalized singular value: **0.0913**
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `|cosine| = 0.9375`

RMS sensitivities:

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 10.4328 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 3.2195 | 30.86% |
| `engine_coolant_ua_w_per_k` | 4.3725 | 41.91% |
| `radiator_ua_nominal_w_per_k` | 0.00461 | **0.044%** |

The holdout profile provides essentially no practical radiator-UA excitation around the generic operating point.

### Combined synthetic profiles

- samples: 114
- numerical rank: 4 of 4
- normalized-matrix condition number: **8.123**
- normalized singular values relative to the largest: `1.0000, 0.6685, 0.5926, 0.1231`
- strongest pairwise similarity: wall heat fraction versus engine thermal capacitance, `cosine = -0.8800`

Combined RMS sensitivities:

| Parameter | RMS sensitivity, C | Relative to strongest |
|---|---:|---:|
| `wall_heat_fraction` | 8.3866 | 100.0% |
| `engine_thermal_capacitance_j_per_k` | 2.4276 | 28.95% |
| `engine_coolant_ua_w_per_k` | 4.1914 | 49.98% |
| `radiator_ua_nominal_w_per_k` | 0.07894 | **0.94%** |

### Interpretation

The normalized Jacobian is neither rank deficient nor severely ill-conditioned at this local synthetic point. That means the four sensitivity histories are mathematically distinct.

However, mathematical rank does not make a weak parameter practically estimable. `radiator_ua_nominal_w_per_k` produces less than one percent of the strongest RMS coolant response across the combined warm-up profiles. A nonlinear optimizer could still move that parameter, but the coolant trace would supply little information with which to distinguish a genuine radiator-UA correction from optimizer freedom, noise, or compensation through other parameters.

Wall heat fraction and effective engine thermal capacitance also show a notable inverse similarity (`cosine = -0.8800` combined and `-0.9375` on the second profile). That is not severe enough to trigger the 0.95 shape heuristic in the combined analysis, but it is a reason to keep both bounds conservative and to inspect post-fit covariance or profile behavior before treating their fitted values as independently identified physical properties.

## Readiness decision

**Do not execute a four-parameter CAL-01 fit.**

The current evidence supports a staged calibration strategy:

1. `CAL-01` may eventually fit only a defensible manifest-declared subset of the warm-up-sensitive parameters after their physical bounds are independently justified and frozen.
2. `radiator_ua_nominal_w_per_k` should remain fixed during CAL-01 unless a separately preregistered calibration case is shown, from source operating conditions rather than VTMS residuals, to provide meaningful radiator-active excitation.
3. Existing holdout reservations must not be converted into calibration cases after their model residuals are observed.
4. A separate radiator-active calibration case, if selected from the already-received Argonne package, must be assigned before its VTMS residual is inspected.

This is a calibration-structure decision, not a statement that the generic 1100 W/K radiator value is correct. The present analysis only establishes that the warm-up profiles are a poor place to estimate it.

## Decision rule for the next phase

Before CAL-01 can run, the project must still:

1. establish the final manifest-declared CAL-01 fitted subset,
2. establish a documented engineering basis for finite physical bounds on every parameter that remains fitted,
3. freeze those bounds without reference to Argonne residuals,
4. decide whether a separate radiator-active calibration case is needed and reserve it before residual inspection,
5. freeze the CAL-01 mapping/preprocessing configuration and exact hashes,
6. create the immutable CAL-01 manifest,
7. only then execute the first physical calibration.

The synthetic identifiability concern is not a software failure. It is useful evidence that the calibration problem should be staged rather than allowing a four-variable optimizer to absorb model mismatch indiscriminately.

## Primary technical sources

- Kaplan, J. A., & Heywood, J. B. (1991). *Modeling the Spark Ignition Engine Warm-Up Process to Predict Component Temperatures and Hydrocarbon Emissions*. SAE Technical Paper 910302. DOI: 10.4271/910302.
- Kaltakkiran, G., Ceviz, M. A., & Bakirci, K. (2022). *Instantaneous energy balance and performance analysis during warm up period of a spark ignition engine under several thermal energy management strategies*. Energy Conversion and Management, 269, 116102. DOI: 10.1016/j.enconman.2022.116102.
- Taler, D. (2013). *Experimental determination of correlations for average heat transfer coefficients in heat exchangers on both fluid sides*. Heat and Mass Transfer, 49, 1125-1139. DOI: 10.1007/s00231-013-1148-5.

## Evidence boundary

Nothing in this document is an Argonne calibration result. Nothing here changes VTMS-V1 equations, the generic parameter snapshot, the formal acceptance thresholds, or the already-reserved holdout roles. VTMS-V1 remains `numerical_verified_generic_uncalibrated`.
