# VTMS-V2 M0 Model Hierarchy Freeze

## Status

**Gate V2-H1: Model Hierarchy Freeze.**

This document freezes the model-selection hierarchy, the V2-M0 falsification baseline, the blind-validation ladder, and the rules that govern promotion from M0 to M1. It does not authorize physical calibration until the remaining M0 input-boundary prerequisites are satisfied.

VTMS-V1 remains unchanged. All V1 formal calibration and holdout results remain preserved as historical evidence.

## Purpose

The Phase 2 full-trace residual reconstruction showed that VTMS-V1's dominant independent errors develop primarily in the regulated hot-temperature region. It also showed that a post-hoc thermostat-threshold change can numerically remove much of the error without adding states, although the required threshold shift is not physically credible for the identified 190 F Ford/Motorcraft thermostat application.

The correct next step is therefore not to assume a higher-order state vector. The correct next step is to falsify the lowest-order model after correcting known control and boundary assumptions.

The hierarchy is frozen as:

```text
M0 = [T_engine, T_coolant]
M1 = [T_engine, T_hot, T_cold]
M2 = [T_head, T_slow, T_hot, T_cold]
M3 = [T_head, T_slow, T_hot, T_cold, x_th]
```

State promotion is evidence-driven. A higher-order model may not be promoted solely because it fits consumed data better.

---

## 1. M0 role

M0 is a **corrected-control two-state falsification baseline**.

M0 answers one question:

> Can a two-state thermal model generalize once vehicle-specific thermostat behavior, coolant branch hydraulics, and the physical cooling-air boundary are represented credibly?

M0 is not intended to become the final VTMS-V2 architecture by default.

If M0 succeeds under the frozen criteria, the project must retain the lower-order model unless independent evidence justifies additional states.

If M0 fails under the frozen criteria after unresolved boundary uncertainty has been reduced sufficiently, the first authorized structural promotion is M1.

---

## 2. M0 state vector

The M0 state vector is frozen as:

```text
x_M0 = [T_engine, T_coolant]
```

where:

- `T_engine` is the effective lumped engine-structure temperature;
- `T_coolant` is the effective lumped coolant temperature used by the two-state falsification baseline.

M0 intentionally retains the V1 thermal-state count so that control and boundary corrections can be tested without confounding state expansion.

No hot/cold coolant split is authorized inside M0.

No thermostat dynamic state is authorized inside M0.

No second engine-structure state is authorized inside M0.

---

## 3. M0 thermal equations

M0 retains the V1 energy-balance topology for the initial falsification program:

```text
C_engine dT_engine/dt = Q_engine
                         - Q_engine_to_coolant
                         - Q_engine_to_ambient

C_coolant dT_coolant/dt = Q_engine_to_coolant
                           - Q_radiator
```

with:

```text
Q_engine_to_coolant = UA_engine_coolant (T_engine - T_coolant)
Q_engine_to_ambient = UA_engine_ambient (T_engine - T_ambient)
```

The thermal topology remains deliberately unchanged from V1 at this stage. The following constitutive and boundary laws are changed or governed separately:

1. thermostat opening law;
2. radiator/bypass branch-flow relationship;
3. test-cell/road cooling-air boundary;
4. active grille shutter treatment if equipment presence is established.

The radiator effectiveness-NTU framework remains permitted in M0.

---

## 4. Thermostat boundary freeze

### 4.1 Component identity

The 2012 Focus 2.0 L DI Ti-VCT application is associated with:

```text
Ford thermostat assembly: CP9Z-8592-G
Motorcraft cross-reference: RT-1219
Nominal rating: 190 F, approximately 87.8 C
```

The nominal opening rating is treated as sourced component evidence.

### 4.2 Opening onset

M0 thermostat opening onset is not calibratable against consumed VTMS residuals.

Frozen nominal onset:

```text
T_open_nominal = 87.8 C
```

For numerical implementation, 88.0 C is an acceptable rounded value if the metadata preserves the 87.8 C source value.

### 4.3 Full-open uncertainty envelope

An exact Ford RT-1219 full-open temperature has not been established by the current evidence set.

M0 therefore does not freeze one exact full-open temperature as a physical fact.

Instead, a preregistered engineering envelope is permitted for falsification sensitivity:

```text
T_full_open in [97 C, 102 C]
```

This interval is an engineering uncertainty envelope for a conventional approximately 190 F wax thermostat. It is not an identified Ford RT-1219 specification.

The envelope must be evaluated through a predefined discrete design or bounded uncertainty analysis. It may not be optimized continuously against the consumed residuals and then reported as the vehicle's physical thermostat setting.

### 4.4 Static opening law

M0 uses a bounded monotonic static opening law. The default form is:

```text
z = clip((T_coolant - T_open) / (T_full_open - T_open), 0, 1)
thermostat_position = z
```

A smoothstep replacement may be evaluated only if it is frozen before M0 physical fitting. Static-law shape selection may not be made after inspecting the blind M0 holdout.

### 4.5 Dynamic thermostat behavior

Thermostat lag and hysteresis are excluded from M0.

A dynamic thermostat state is reserved for M3 unless independent actuator evidence or reproducible opening-versus-closing residual structure establishes a lower-level need.

---

## 5. Coolant branch-flow law

### 5.1 Rejected V1 assumption

The V1 identity:

```text
radiator_flow_fraction = thermostat_position
```

is rejected for M0 because valve position is not generally equal to hydraulic branch-flow fraction.

### 5.2 Frozen M0 law family

M0 uses a bounded monotonic static branch-flow law:

```text
z = clip(thermostat_position, 0, 1)
shape = z ** gamma
f_rad = f_closed + (f_open - f_closed) * shape

m_dot_rad = f_rad * m_dot_pump
m_dot_bypass = (1 - f_rad) * m_dot_pump
```

### 5.3 Engineering bounds

The following are engineering assumptions for M0, not Ford component specifications:

```text
f_closed in [0.00, 0.05]
f_open   in [0.85, 1.00]
gamma    in [0.50, 2.00]
```

Required invariants:

```text
0 <= f_rad <= 1
m_dot_rad >= 0
m_dot_bypass >= 0
m_dot_rad + m_dot_bypass = m_dot_pump
```

The same globally frozen hydraulic parameters apply across every M0 run. Per-run branch-flow parameters are prohibited.

A pressure-loss branch network may replace this law in a later model only if its additional coefficients are independently constrained and preregistered.

---

## 6. Pump model

M0 retains the V1 RPM-based pump-flow model as a provisional fixed upstream model.

Pump parameters are not included in the initial M0 calibration subset.

Reason:

Allowing pump-flow coefficients, branch-flow coefficients, radiator conductance, and cooling-air transfer to move simultaneously would create an underidentified heat-rejection subsystem.

If M0 fails and residual/sensitivity evidence points strongly to pump-flow error, pump-model revision must be proposed explicitly rather than hidden inside another coefficient.

---

## 7. Radiator model

### 7.1 Effectiveness-NTU framework

M0 retains the existing crossflow effectiveness-NTU radiator calculation.

### 7.2 Radiator conductance

M0 initially retains one global effective radiator UA.

Flow-dependent radiator UA is not part of the minimum M0 correction because Phase 2 established that state/control/boundary ambiguity must be resolved first.

A flow-dependent UA law is reserved as a later constitutive-law candidate if M0 or M1 evidence requires it.

### 7.3 Global parameter rule

Radiator UA may not be calibrated separately for each test.

One globally frozen M0 radiator parameter must apply to the complete development set under the applicable cooling-air boundary model.

---

## 8. Engine heat input

Controlled M0 evidence continues to use direct Argonne fuel-flow evidence with the declared lower heating value.

```text
Q_fuel = m_dot_fuel * LHV
Q_engine = wall_heat_fraction * Q_fuel
```

M0 retains a constant wall heat fraction.

Operating-dependent heat partition is not authorized inside M0.

This is deliberate. If M0 requires an operating-dependent heat partition to pass, that constitutes evidence for a later model revision rather than permission to expand M0 indefinitely.

---

## 9. Cooling-air boundary

### 9.1 Fundamental rule

`Dyno_Spd` is an operating signal. It is not automatically radiator-core air velocity.

Every M0 development or validation run must have an explicit cooling-air boundary class.

Allowed classes:

```text
CONSTANT_SPEED_EXTERNAL_FAN
SPEED_MATCHED_EXTERNAL_FAN
MEASURED_CORE_AIRFLOW
OTHER_DOCUMENTED_BOUNDARY
UNKNOWN
```

### 9.2 Tests 71207062 and 71207063

The Argonne public master-summary table records:

```text
71207062: constant-speed external vehicle cooling fan, hood up
71207063: constant-speed external vehicle cooling fan, hood up
```

These runs must not derive radiator airflow directly from `Dyno_Spd`.

The relevant certification-style external-fan protocol permits approximately 5300 cfm, approximately 2.50 m3/s, for the external vehicle cooling fan. This value is a fan-capacity protocol boundary, not measured radiator-core flow.

M0 must preserve a separate cooling-pack transfer factor between external fan capacity and effective radiator air mass flow.

### 9.3 Tests 71207052 and 71207057

The exact cooling-fan setup for these two consumed V1 runs is not established by the currently frozen public setup table.

They are classified for M0 as:

```text
71207052: UNKNOWN
71207057: UNKNOWN
```

Until stronger evidence is obtained, these runs may be used for residual diagnostics and uncertainty stress testing, but they may not independently identify radiator UA or cooling-pack transfer coefficients.

### 9.4 Cooling-pack transfer

For constant-speed external-fan tests, effective core airflow may be represented initially as:

```text
m_dot_air_core = rho_air * eta_pack * V_dot_external_fan
```

where `eta_pack` is a global dimensionless effective transfer coefficient that absorbs known unresolved effects such as:

- fan-to-grille geometry;
- grille restriction;
- cooling-pack pressure loss;
- hood-up flow field;
- recirculation;
- unmeasured upstream restriction.

`eta_pack` must use one globally frozen value or one preregistered uncertainty interval. Per-run values are prohibited unless the physical test setup itself changed and that change is documented.

### 9.5 Active grille shutters

The 2012 Focus platform supports PCM-controlled active grille shutters when equipped, but the current Argonne vehicle evidence does not prove whether the tested vehicle had them.

Frozen status:

```text
AGS_STATUS_UNRESOLVED
```

M0 may not infer AGS presence from exterior photographs, wheel design, body style, or likely trim.

Until equipment status is resolved:

- no PCM-style shutter command law is fitted to ECT;
- no time-varying shutter state is inferred from residuals;
- an `AGS_ABSENT_OR_FULL_OPEN` case may be used as the primary baseline;
- a bounded static upstream-restriction sensitivity may be used as a secondary uncertainty case;
- radiator UA may not silently absorb a claimed shutter effect.

If AGS presence is confirmed later, its boundary law must be separately frozen before it is used for parameter identification.

---

## 10. M0 parameter governance

### 10.1 Parameters eligible for staged M0 calibration

The initial M0 calibration universe remains deliberately small.

Thermal stage candidates:

```text
wall_heat_fraction                 [0.20, 0.50]
engine_thermal_capacitance_j_per_k [25000, 100000]
engine_coolant_ua_w_per_k          [400, 2200]
```

Heat-rejection/control stage candidates may include only the minimum subset selected after synthetic identifiability review from:

```text
radiator_ua_nominal_w_per_k
eta_pack
f_closed
f_open
gamma
```

Not every candidate may be fitted simultaneously.

### 10.2 Fixed in M0

Initially fixed:

- thermostat nominal opening onset;
- pump-flow coefficients;
- coolant properties;
- radiator geometry;
- air properties;
- solver tolerances;
- heat-input lower heating value;
- M0 state count;
- model hierarchy;
- blind-validation roles.

### 10.3 Identifiability rule

Before any physical M0 fit, a synthetic sensitivity and parameter-correlation study must establish a permissible stage-specific subset.

A candidate parameter is excluded from a stage if it is weakly excited or strongly non-identifiable relative to the other parameters in that stage.

No stage may be expanded after seeing its physical residuals without declaring a new development iteration and invalidating any blind role that has already been inspected.

---

## 11. M0 development evidence

The following V1-consumed controlled tests are now classified as V2 development evidence:

```text
71207062  cold-start UDDS #1
71207057  highway calibration run
71207063  hot-start UDDS #2
71207052  55 mph warm-up
```

They have no blind V2 status.

They may support:

- model-form diagnosis;
- M0 calibration under preregistered stages;
- uncertainty analysis;
- residual localization;
- parameter-sensitivity analysis.

They may not support a new claim of independent V2 validation.

---

## 12. Reserved blind-validation ladder

The model hierarchy requires new evidence to remain uninspected by predictions until the corresponding model is frozen.

The following reservation is frozen before M0 physical fitting:

### 12.1 M0 primary blind holdout

```text
Test ID: 71207054
Cycle: 1.2 UDDS ED
Role: V2-M0 primary blind holdout
Source SHA-256: 664a6ee52569fc0ca807675f5850136ef06a3f3075fc2b67c7d84143fb8db250
Source size: 3335603 bytes
```

Source-only qualification indicates complete clean ECT coverage over the selected full test and a hot regulated range suitable for testing M0 generalization.

No M0 prediction may be generated for 71207054 until the complete M0 parameter snapshot, preprocessing mapping, thresholds, and acceptance criteria are frozen.

### 12.2 M1 reserve

```text
Test ID: 71207055
Cycle: 1.4 UDDS ED
Role: V2-M1 blind reserve if M1 promotion occurs
Source SHA-256: 664bedb0ab6685d82b5d3823e840031dc45f86c076f249f9b2f47beaa7c97289
Source size: 2869287 bytes
```

If M0 passes and no M1 promotion occurs, this run remains unused and may be reserved for a later confirmatory V2 test.

If M0 fails 71207054 and M1 is promoted, 71207054 becomes consumed development evidence and 71207055 becomes the primary blind M1 holdout.

### 12.3 M2 reserve

```text
Test ID: 71207056
Cycle: SSS 0-80-0
Role: V2-M2 blind reserve / high-speed challenge
Source SHA-256: 9085b79c69cce4d9d29b5965d988a2a7e08859044e68f5524fa94f21db98d389
Source size: 1583034 bytes
```

This run remains blind unless and until its assigned rung is reached under the hierarchy.

### 12.4 Final challenge reserve

```text
Test ID: 71207053
Cycle: UDDS Cycle Beating
Role: secondary/final challenge reserve
Source SHA-256: 2d2b6e3236770f499e7b1fc4d9f9272cbac06bae411708d3d408df0186685c95
Source size: 3977672 bytes
```

The cycle label and role make this better suited to secondary challenge evidence than the first M0 blind decision.

### 12.5 Cold-start limitation

No separate clean cold-start replicate has been identified in the current Argonne package.

Therefore even a successful V2 hierarchy may not claim independent cold-start generalization from this dataset alone.

---

## 13. Frozen M0 acceptance metrics

Unless a later governance document tightens them before blind execution, M0 uses the existing controlled-comparison thresholds as the primary whole-trace acceptance criteria:

```text
RMSE <= 5.0 C
MAE <= 4.0 C
absolute mean bias <= 3.0 C
P90 absolute error <= 7.0 C
threshold arrival-time error <= 60 s where evaluable
```

M0 also adds one preregistered hot-region diagnostic because Phase 2 localized the dominant failure there:

```text
For measured ECT in [96 C, 100 C]:
absolute mean residual <= 3.0 C
```

The hot-region metric is evaluated only when the retained trace contains enough samples to support it. A minimum sample count must be frozen in the M0 execution manifest before blind evaluation.

One metric may not be silently dropped because it fails.

---

## 14. Parameter-bound pressure diagnostic

Parameter-bound saturation is a model-form warning, not an automatic failure by itself.

Define:

```text
near_bound = calibrated value lies within 1% of its permitted interval width from either bound
```

Interpretation:

- one near-bound parameter: warning and sensitivity review;
- two or more near-bound parameters combined with acceptance-metric failure: strong evidence against M0 adequacy;
- parameter-bound widening after blind inspection: prohibited.

A failed blind test may not be repaired by widening bounds unless the blind status is explicitly consumed and a new higher-level holdout remains reserved.

---

## 15. M0 to M1 promotion rule

M1 may be promoted only after all of the following are true:

1. M0 equations and boundary laws were frozen before physical fitting.
2. M0 used one global parameter set under the documented boundary classes.
3. Known external-fan/hood boundaries were represented explicitly rather than inferred from dyno speed.
4. Thermostat onset remained physically anchored near the sourced 190 F rating.
5. The hydraulic branch-flow law remained inside its frozen engineering bounds.
6. The failed result cannot reasonably be attributed to an unresolved input boundary that has enough sensitivity leverage to explain the failure.
7. M0 fails one or more frozen acceptance criteria on its primary blind holdout or exhibits a reproducible structural residual on development evidence that cannot be removed within credible M0 bounds.
8. No M1 prediction has been inspected before the promotion decision.

If M0 fails the primary blind 71207054 run:

```text
71207054 -> consumed M1 development evidence
71207055 -> primary M1 blind holdout
```

The M1 promotion decision must be committed before any 71207055 prediction is generated.

---

## 16. M1 scope if promoted

M1 is limited to the first structural expansion:

```text
x_M1 = [T_engine, T_hot, T_cold]
```

Its purpose is to test whether spatial coolant separation is the missing structure.

M1 does not automatically authorize:

- a second engine metal state;
- a thermostat dynamic state;
- machine-learned residual correction;
- arbitrary operating-dependent heat partition;
- per-run radiator parameters.

Those remain later hypotheses.

---

## 17. M2 and M3 promotion discipline

### M2

M2 may add a second engine thermal-storage state only if M1 leaves reproducible transient/storage error or forces engine thermal parameters outside credible ranges.

Argonne engine-oil temperature is an auxiliary observable for evaluating the need for slower thermal storage. It must not be treated automatically as equal to the added state.

### M3

M3 may add a dynamic thermostat state only if static sourced thermostat behavior leaves reproducible lag/hysteresis evidence or independent actuator evidence supports a dynamic state.

No thermostat state is added solely because additional dynamics improve curve fit.

---

## 18. Pre-implementation verification requirements

Before M0 physical fitting, implementation tests must establish:

- energy conservation under zero-loss configurations;
- pump-flow conservation;
- branch-flow conservation;
- thermostat command bounded in [0, 1];
- radiator-flow fraction bounded in [0, 1];
- monotonic flow split versus thermostat position for fixed pump flow;
- zero-flow radiator behavior;
- explicit constant-external-fan boundary independent of dyno speed;
- explicit speed-matched boundary behavior when selected;
- AGS unresolved case does not silently modify radiator UA;
- deterministic solver convergence against step refinement;
- V1 code path remains unchanged.

---

## 19. M0 unresolved prerequisites

Model Hierarchy Freeze does not imply every M0 physical input is known.

The following remain open prerequisites for M0 calibration/execution:

1. exact or sufficiently bounded external-fan-to-core airflow transfer for the known constant-fan Argonne tests;
2. stronger evidence for the cooling setup of 71207052 and 71207057, or an explicit decision to exclude them from heat-rejection parameter identification;
3. final selection of the thermostat full-open uncertainty design within the frozen 97-102 C envelope;
4. synthetic identifiability review for the permitted branch-flow and cooling-pack parameters;
5. exact minimum sample count for the 96-100 C hot-region acceptance metric;
6. source/preprocessing manifests for reserved blind tests before execution.

These are implementation/calibration gates. They do not reopen the frozen model hierarchy.

---

## 20. Gate decision

**Gate V2-H1 Model Hierarchy Freeze: PASS.**

Frozen decisions:

- M0 through M3 state hierarchy;
- M0 two-state role;
- thermostat onset physical anchor;
- static thermostat only in M0;
- nonlinear hydraulic branch-flow requirement;
- explicit cooling-air boundary requirement;
- AGS unresolved status policy;
- staged/global parameter governance;
- M0 acceptance metrics;
- parameter-bound pressure diagnostic;
- M0 to M1 promotion rules;
- blind-validation ladder 71207054 -> 71207055 -> 71207056, with 71207053 reserved as secondary challenge evidence.

M0 implementation may begin after this freeze.

M0 physical calibration remains separately blocked until the required boundary and identifiability prerequisites are frozen.
