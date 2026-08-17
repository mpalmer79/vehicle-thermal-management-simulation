# Argonne Calibration Bounds and Identifiability Preregistration

## Status

**Frozen before inspection of VTMS-vs-Argonne residuals.**

This document records the first controlled physical-calibration search space for VTMS-V1 and the pre-Argonne identifiability diagnostic. The purpose is to prevent residual-driven boundary selection and to make later calibration decisions auditable.

The Argonne source data have been received and qualified, but no VTMS prediction residual against the selected Argonne calibration or holdout traces was used to select the bounds in this document.

## Governing calibration subset

The existing validation protocol permits only four fitted parameters:

1. `wall_heat_fraction`
2. `engine_thermal_capacitance_j_per_k`
3. `engine_coolant_ua_w_per_k`
4. `radiator_ua_nominal_w_per_k`

No other VTMS-V1 parameter may move in the first Argonne fit without a new protocol version.

## Frozen physical calibration bounds

| Parameter | Lower | Upper | Current generic value | Interpretation |
|---|---:|---:|---:|---|
| `wall_heat_fraction` | 0.20 | 0.50 | 0.28 | effective fraction of measured fuel LHV rate entering the lumped engine thermal state |
| `engine_thermal_capacitance_j_per_k` | 25,000 J/K | 100,000 J/K | 50,000 J/K | effective thermal capacitance of the V1 engine-structure state |
| `engine_coolant_ua_w_per_k` | 400 W/K | 2,200 W/K | 1,000 W/K | effective aggregate engine-structure-to-coolant conductance |
| `radiator_ua_nominal_w_per_k` | 400 W/K | 2,200 W/K | 1,100 W/K | nominal aggregate radiator conductance in the V1 effectiveness-NTU model |

These are **engineering bounds for the frozen VTMS-V1 topology**, not direct measurements of Ford components. A fitted effective parameter must not be relabeled as a physical mass, local heat-transfer coefficient, or bench-rated radiator constant.

These bounds are intentionally different from the synthetic calibration-harness fixtures. The synthetic ranges were software-test inputs and remain prohibited as physical justification.

## Parameter rationale

### 1. Wall heat fraction: 0.20 to 0.50

Transient gasoline-engine start-up work by Lejsek and Kulzer reports combustion-wall heat transfer as a very large term in the start-up energy balance, approximately 40 percent of burned fuel energy in SAE 2009-01-0613 and nearly 45 percent in SAE 2010-01-1270. Those measurements are not identical to the VTMS parameter because V1 collapses multiple engine solids into one state and does not explicitly represent oil, exhaust, or spatial wall temperatures.

The preregistered interval therefore brackets the literature scale without forcing the fitted effective V1 parameter to equal a local combustion-wall measurement. The 0.20 lower bound allows substantial energy to leave through pathways omitted from the single engine state, while 0.50 prevents the calibration from assigning a majority-plus share of fuel LHV directly to the one lumped state.

Primary sources:

- SAE 2009-01-0613, *Investigations on the Transient Wall Heat Transfer at Start-Up for SI Engines with Gasoline Direct Injection*.
- SAE 2010-01-1270, *Novel Transient Wall Heat Transfer Approach for the Start-up of SI Engines with Gasoline Direct Injection*.

### 2. Effective engine thermal capacitance: 25 to 100 kJ/K

Engine warm-up literature routinely represents engine structure using lumped thermal capacitances or lumped masses. SAE 910302 develops an SI-engine warm-up model using lumped thermal capacitance for major engine components. SAE 931153 uses a lumped-capacity block/head model. SAE 971852 describes engine geometry, mass, coolant volume, and lumped-capacity thermal behavior. SAE 2016-01-0197 separates coolant, oil, and engine masses in a four-point warm-up model.

VTMS-V1 is lower order than those models, so its `engine_thermal_capacitance_j_per_k` is an **effective participating capacitance**, not the heat capacity of the complete engine assembly. A broad 25 to 100 kJ/K interval spans a factor of four and contains the current 50 kJ/K generic value. It allows a large change in transient inertia without allowing the engine state to become nearly massless or effectively fixed over a drive-cycle warm-up.

Primary sources:

- SAE 910302, *Modeling the Spark Ignition Engine Warm-Up Process to Predict Component Temperatures and Hydrocarbon Emissions*.
- SAE 931153, *A Model for the Investigation of Temperature, Heat Flow and Friction Characteristics During Engine Warm-Up*.
- SAE 971852, *Progress on Modelling Engine Thermal Behaviour for VTMS Applications*.
- SAE 2016-01-0197, *Prediction of Engine Thermal Behavior during Emission Cycle Using 1D Four Point Mass Model*.

### 3. Engine-to-coolant UA: 400 to 2,200 W/K

Detailed engine thermal models resolve coolant-side convection, conduction through engine solids, spatial wall temperatures, and multiple coolant paths. SAE 931157 uses convection/conduction thermal-network elements. SAE 971852 describes boundary heat exchange with coolant and other flows. Ford-authored SAE 2011-01-0647 uses a detailed coolant circuit with component heat-transfer rates and lumped thermal components.

VTMS-V1 compresses that distributed network into one conductance, `UA_ec`. There is therefore no single literature value that can be transferred directly. The 400 to 2,200 W/K range spans more than a fivefold change in coupling strength around the current 1,000 W/K value. It is intentionally broad because this parameter is expected to trade against effective thermal capacitance in coolant-only calibration.

Primary sources:

- SAE 931157, *A Computer Model for Thermofluid Analysis of Engine Warm-up Process*.
- SAE 971852, *Progress on Modelling Engine Thermal Behaviour for VTMS Applications*.
- SAE 2011-01-0647, *Development of a One-Dimensional Engine Thermal Management Model to Predict Piston and Oil Temperatures*.

### 4. Radiator nominal UA: 400 to 2,200 W/K

The V1 radiator is explicitly an effectiveness-NTU heat exchanger. SAE 940771 applies NTU/effectiveness methods to an automotive radiator and demonstrates that inlet-air distributions influence performance. Ford-authored SAE 2011-01-0647 likewise treats the coolant system and heat-rejection hardware as a coupled thermal network.

A universal passenger-car radiator UA cannot be imported without the exact core, flows, frontal distribution, and test condition. The preregistered 400 to 2,200 W/K interval therefore serves as a broad effective-system range around the generic 1,100 W/K value. It is large enough to permit material correction while preventing the optimizer from escaping into a nearly zero or arbitrarily large conductance.

Primary sources:

- SAE 940771, *Determination of the Effects of Inlet Air Velocity and Temperature Distributions on the Performance of an Automotive Radiator*.
- SAE 2011-01-0647, *Development of a One-Dimensional Engine Thermal Management Model to Predict Piston and Oil Temperatures*.

## Identifiability preflight

The four parameters are not assumed to be separately identifiable simply because an optimizer can return four numbers.

`src/vtms_validation/identifiability.py` performs a pre-physical-data local sensitivity study on a deterministic synthetic excitation profile. For each calibration parameter it uses a central multiplicative perturbation and estimates:

```text
dT_c / d(log theta)
```

The resulting coolant-temperature sensitivity columns are normalized before computing:

- parameter-shape correlation matrix,
- singular values,
- normalized-Jacobian condition number,
- RMS and peak absolute log-sensitivity for each parameter.

A diagnostic warning is raised when the normalized condition number exceeds 100, an absolute cross-parameter correlation exceeds 0.95, or a parameter is effectively unexcited.

Those thresholds are **diagnostic engineering flags**, not statistical confidence criteria and not validation acceptance limits. The analysis is local to the generic V1 point and the synthetic excitation. It cannot prove structural identifiability on the Argonne cycle.

## Interpretation rule for the physical fit

If the first Argonne calibration returns parameters near bounds, strong covariance, or multiple substantially different parameter combinations with similar coolant residuals, VTMS will treat the individual fitted parameters as non-unique effective values. The project will not claim that coolant temperature alone uniquely identifies physical engine mass, wall heat transfer, engine-to-coolant conductance, and radiator conductance.

The correct response to poor identifiability is to add independent observables or stronger physically sourced constraints, not to keep widening the optimizer bounds until one fit looks visually good.

## Change-control rule

These four bounds are preregistered for the first controlled Argonne calibration. Any later change requires:

1. a new documented protocol/bounds version,
2. a reason independent of improving the already-observed residual,
3. disclosure that the original preregistration was superseded,
4. a new immutable calibration manifest before rerunning the fit.

The first Argonne residual must therefore be preserved even if it is poor.
