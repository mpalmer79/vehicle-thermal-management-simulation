# VTMS-V2 M2 Four-State Engine-Storage Topology Freeze

## Status

**Frozen before M2 physical development.**

M2 is authorized only because the governed M1 family produced an empty joint feasible set across the preregistered consumed-development envelope.

M2 adds exactly one structural concept beyond M1: a second engine solid thermal-storage state. The M1 coolant loop, static thermostat law, hydraulic split, airflow boundary, pump, fan, and radiator equations remain unchanged.

M2 does **not** add a thermostat actuator state. Dynamic thermostat behavior remains reserved for M3.

## State vector

\[
x_{M2}=[T_h,T_b,T_{hot},T_{cold}]
\]

where:

- `T_h`: fast head / combustion-facing effective metal temperature;
- `T_b`: slower block / structural effective metal temperature;
- `T_hot`: engine-out / ECT-side coolant temperature;
- `T_cold`: radiator-return coolant temperature.

The observation mapping remains:

\[
ECT_{pred}=T_{hot}
\]

and is not calibratable.

## Retained total thermal quantities

M2 preserves the M1 effective totals rather than introducing independent absolute capacities for each new node.

Total engine effective thermal capacitance:

\[
C_e=C_h+C_b
\]

with:

\[
C_h=f_h C_e,\qquad C_b=(1-f_h)C_e
\]

where `f_h = head_thermal_capacitance_fraction`.

The retained total engine-to-coolant conductance is partitioned by the same storage fraction to avoid introducing an additional unidentifiable conductance-split parameter:

\[
UA_{hc}=f_h UA_{ec}
\]

\[
UA_{bc}=(1-f_h)UA_{ec}
\]

The retained total engine-to-ambient conductance is partitioned identically:

\[
UA_{ha}=f_h UA_{ea}
\]

\[
UA_{ba}=(1-f_h)UA_{ea}
\]

These are model-form constraints, not claims that physical heat-transfer area scales exactly with effective thermal capacitance.

## Heat-input partition

The existing engine thermal heat input remains:

\[
Q_e=\eta_{wall}Q_{fuel}
\]

for controlled physical evidence, or the existing M0/M1 engine-heat input contract for synthetic/reference operation.

M2 partitions that already-defined thermal input as:

\[
Q_h=\beta_h Q_e
\]

\[
Q_b=(1-\beta_h)Q_e
\]

where `beta_h = head_heat_fraction`.

M2 does not yet introduce an operating-dependent heat-partition function. That broader V2 concept remains deferred until the minimum four-state model has been tested.

## Internal solid coupling

The two engine solid states exchange heat through one symmetric internal conductance:

\[
Q_{hb}=UA_{hb}(T_h-T_b)
\]

with `UA_hb = head_block_ua_w_per_k`.

Internal heat removed from the head enters the block with equal magnitude and opposite sign.

## Governing equations

Fast head state:

\[
C_h\dot T_h=Q_h-Q_{hc}-Q_{hb}-Q_{ha}
\]

where:

\[
Q_{hc}=UA_{hc}(T_h-T_{hot})
\]

\[
Q_{ha}=UA_{ha}(T_h-T_a)
\]

Slow block state:

\[
C_b\dot T_b=Q_b+Q_{hb}-Q_{bc}-Q_{ba}
\]

where:

\[
Q_{bc}=UA_{bc}(T_b-T_{hot})
\]

\[
Q_{ba}=UA_{ba}(T_b-T_a)
\]

Hot-side coolant:

\[
C_{hot}\dot T_{hot}=Q_{hc}+Q_{bc}+\dot m_p c_p(T_{cold}-T_{hot})
\]

Cold-side coolant remains exactly the M1 conservative return-mixing equation:

\[
C_{cold}\dot T_{cold}=\dot m_{rad}c_p(T_{rad,out}-T_{cold})+\dot m_{bypass}c_p(T_{hot}-T_{cold})
\]

with:

\[
\dot m_p=\dot m_{rad}+\dot m_{bypass}
\]

## Conservation identity

Adding all four state equations cancels the internal head/block exchange and all internal coolant-loop transport terms:

\[
\frac{dE_{stored}}{dt}=Q_e-Q_{ha}-Q_{ba}-Q_{rad}
\]

This identity is a mandatory software invariant.

## Exact nested collapse to M1

M2 must contain M1 as an exact limiting submanifold.

If:

1. `T_h(0) = T_b(0)`;
2. `head_heat_fraction = head_thermal_capacitance_fraction`;
3. the conductance and ambient partitions remain the frozen proportional definitions above;

then the normalized derivatives of the two solid states are identical while `T_h = T_b`. The two states therefore remain identical for the deterministic ODE solution and their summed equation reduces exactly to the M1 engine equation.

Under that condition, M2 ECT must match M1 ECT to numerical tolerance for identical coolant and control parameters.

This collapse test is mandatory before physical development.

## New M2 topology parameters

Initial synthetic reference values and preregistered engineering bounds are:

| Parameter | Reference | Frozen synthetic/development bound | Meaning |
|---|---:|---:|---|
| `head_thermal_capacitance_fraction` | 0.35 | 0.15 to 0.60 | fraction of existing effective engine capacitance assigned to fast head state |
| `head_heat_fraction` | 0.70 | 0.50 to 0.95 | fraction of existing engine thermal input deposited directly into fast head state |
| `head_block_ua_w_per_k` | 800 W/K | 100 to 3000 W/K | effective internal conductance between fast and slow solids |

These quantities are effective low-order topology parameters and must not be reported as measured Ford Focus physical properties.

## Identifiability restrictions before physical use

No M2 physical optimizer is authorized until synthetic analysis evaluates at minimum:

1. the three new topology parameters together;
2. topology parameters against total engine capacitance;
3. topology parameters against total engine-to-coolant UA;
4. topology parameters against the existing M1 hot/cold coolant capacitance split.

Known M1 restrictions remain active:

- radiator UA and `f_open` may not be optimized in the same ECT-only stage;
- `eta_pack` remains an airflow-boundary uncertainty term rather than an ECT fit parameter;
- `f_closed` remains fixed in the initial hierarchy;
- reserved blind evidence remains closed.

## Initialization governance

Cold-start synthetic verification may initialize all thermal states consistently when appropriate.

Physical hot starts require a separately frozen hidden-state policy because `T_h(0)`, `T_b(0)`, and `T_cold(0)` are not measured by ECT alone. None of those hidden temperatures may be freely fitted per run.

## M2 rejection or promotion

M2 must earn any blind execution through the same sequence used for M0 and M1:

1. equation freeze;
2. software verification;
3. synthetic identifiability;
4. consumed-development manifest;
5. governed joint feasibility/calibration decision.

If the governed M2 family still cannot reconcile consumed development evidence, only then may M3 add a dynamic thermostat state.
