# VTMS Pre-Argonne Calibration Readiness

## Status

**CAL-01 remains blocked. No Argonne model residual has been evaluated. Physical calibration bounds are not yet frozen.**

This document records the engineering basis for the pre-fit identifiability gate that must be completed before the 2012 Ford Focus Argonne D3 cold-start calibration run is allowed to influence VTMS-V1 parameters.

The purpose is not to find bounds that make the future fit succeed. The purpose is to determine whether the four preregistered effective parameters can be distinguished by the available coolant-temperature observation and to identify what additional physical rationale is required before numerical limits are frozen.

## Frozen calibration subset

The controlled subset remains unchanged:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

No fifth parameter is introduced by this work.

## Why literature values cannot simply be copied into VTMS

### Wall heat fraction

In controlled execution VTMS applies:

```text
Q_engine = wall_heat_fraction * fuel_energy_rate
```

`wall_heat_fraction` is therefore the fraction of fuel-energy rate entering the effective engine thermal state. It is **not** identical to the fraction of fuel energy measured later at the coolant boundary.

Kaltakkiran, Ceviz, and Bakirci experimentally studied a gasoline Ford EFI spark-ignition engine throughout warm-up and showed that the energy distribution changes during the transient and changes again when the cooling/oil/exhaust thermal-management paths are altered. Their reference thermostat opening time changed from 252 s to 218 s when coolant was not routed through the oil cooler, and another strategy reduced warm-up time by about 30 percent. That evidence supports treating the VTMS wall fraction as an effective transient model parameter rather than a universal coolant-loss percentage.

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

The Argonne evidence provides engine coolant temperature but does not directly measure the VTMS effective engine-structure state `T_e`. As a result, `UA_ec` and `C_e` can potentially trade against one another while producing similar coolant traces. That is an identifiability question and must be tested before either range is frozen.

**Bound status:** unresolved. Positivity is necessary but not sufficient.

### Nominal radiator UA

VTMS uses one nominal radiator conductance inside an effectiveness-NTU calculation. Real automotive radiators do not have one universal flow-independent heat-transfer coefficient.

Taler experimentally characterized an automotive radiator used with a 1.58 L spark-ignition engine. The study used 57 measured operating points, four air velocities from 1.0 to 2.2 m/s, measured liquid/air temperatures and flows, and nonlinear least-squares estimation of the heat-transfer correlations. The paper explicitly constructs a Jacobian of calculated outlet temperatures with respect to unknown heat-transfer parameters and evaluates its derivatives by finite differences. The experiment also reports water/air heat-rate closure within four percent.

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
- pairwise cosine similarity between sensitivity histories
- singular values of the column-normalized sensitivity matrix
- numerical matrix rank
- condition number of the normalized matrix
- explicit diagnostic flags for zero local sensitivity, rank deficiency, high pairwise shape similarity, or strong ill-conditioning

The pairwise `|cosine| >= 0.95` and normalized condition-number `>= 100` flags are **VTMS engineering heuristics only**. They are not SAE, Argonne, or literature acceptance standards.

Most importantly, the function rejects any dataset that is not explicitly marked synthetic and nonphysical. This prevents the identifiability phase from accidentally seeing Argonne prediction residuals before physical calibration bounds and evidence roles are frozen.

## Synthetic profiles used

The diagnostic reuses the already-existing deterministic synthetic calibration and holdout operating profiles. The synthetic test-only calibration bounds are not read or used by the identifiability calculation. Perturbations are local percentages around the generic VTMS-V1 snapshot.

The CI runner evaluates:

1. synthetic calibration profile alone
2. synthetic holdout profile alone
3. both profiles combined

The combined profile is the most informative pre-fit view because it asks whether changes in operating condition improve separation of the four parameter sensitivity shapes.

## Decision rule for the next phase

This work does **not** automatically authorize calibration if the matrix has full numerical rank.

Before CAL-01 can run, the project must still:

1. inspect the synthetic identifiability result,
2. determine whether four-parameter fitting is practically defensible from coolant-only evidence,
3. if necessary, reduce or stage the fitted subset rather than accepting a confounded optimization,
4. establish a documented engineering basis for finite physical bounds on every parameter that remains fitted,
5. freeze those bounds without reference to Argonne residuals,
6. freeze the CAL-01 mapping/preprocessing configuration and manifest hashes,
7. only then execute the first physical calibration.

If the synthetic diagnostic reveals strong confounding, that finding is not a software failure. It is evidence that the calibration problem needs to be constrained or restructured before physical fitting.

## Primary technical sources

- Kaplan, J. A., & Heywood, J. B. (1991). *Modeling the Spark Ignition Engine Warm-Up Process to Predict Component Temperatures and Hydrocarbon Emissions*. SAE Technical Paper 910302. DOI: 10.4271/910302.
- Kaltakkiran, G., Ceviz, M. A., & Bakirci, K. (2022). *Instantaneous energy balance and performance analysis during warm up period of a spark ignition engine under several thermal energy management strategies*. Energy Conversion and Management, 269, 116102. DOI: 10.1016/j.enconman.2022.116102.
- Taler, D. (2013). *Experimental determination of correlations for average heat transfer coefficients in heat exchangers on both fluid sides*. Heat and Mass Transfer, 49, 1125-1139. DOI: 10.1007/s00231-013-1148-5.

## Evidence boundary

Nothing in this document is an Argonne calibration result. Nothing here changes VTMS-V1 equations, the generic parameter snapshot, the formal acceptance thresholds, the already-reserved calibration/holdout roles, or the `numerical_verified_generic_uncalibrated` classification.
