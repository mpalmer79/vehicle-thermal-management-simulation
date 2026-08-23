# VTMS-V2 M1 Three-State Coolant Topology Freeze

## Status

**Frozen before M1 physical development fitting.**

M1 is the first structural model promoted after the governed M0 two-state family failed TFEAS-01 with zero hot-start survivors out of 29,160 preregistered configurations.

## State vector

\[
x=[T_e,T_h,T_c]
\]

with:

- `T_e`: effective engine-structure temperature;
- `T_h`: engine-out / hot-side coolant temperature;
- `T_c`: radiator-return / cold-side coolant temperature.

The predicted engine-coolant-temperature observation is:

\[
ECT_{pred}=T_h
\]

This observation mapping is structural and may not be changed by calibration.

## Governing equations

Engine structure:

\[
C_e\dot T_e=Q_{engine}-Q_{ec}-Q_{ea}
\]

\[
Q_{ec}=UA_{ec}(T_e-T_h)
\]

\[
Q_{ea}=UA_{ea}(T_e-T_a)
\]

Hot-side coolant:

\[
C_h\dot T_h=Q_{ec}+\dot m_p c_p(T_c-T_h)
\]

Cold-side coolant:

\[
C_c\dot T_c=\dot m_{rad}c_p(T_{rad,out}-T_c)+\dot m_{bypass}c_p(T_h-T_c)
\]

Flow continuity:

\[
\dot m_p=\dot m_{rad}+\dot m_{bypass}
\]

The radiator model is evaluated with `T_h` as radiator inlet temperature. Its outlet temperature is algebraic when radiator flow is active.

## Coolant thermal-capacitance partition

M1 preserves the total M0 coolant thermal capacitance:

\[
C_h+C_c=C_{coolant,total}
\]

with one topology parameter:

\[
C_h=f_h C_{coolant,total},\qquad C_c=(1-f_h)C_{coolant,total}
\]

The initial synthetic reference value is `f_h = 0.50`. This is an engineering topology assumption, not a vehicle-specific identified quantity. Physical fitting of `f_h` is prohibited until M1 synthetic identifiability review is complete.

## Conservation identity

Adding the hot and cold coolant equations and applying flow continuity gives:

\[
C_h\dot T_h+C_c\dot T_c=Q_{ec}-Q_{rad}
\]

because all internal advective transport and bypass mixing terms cancel exactly. Adding the engine equation gives:

\[
\frac{dE_{stored}}{dt}=Q_{engine}-Q_{ea}-Q_{rad}
\]

This identity is a mandatory software invariant.

## Retained M0 components

M1 retains the governed M0 implementations of the static thermostat opening law, nonlinear radiator/bypass hydraulic split, RPM-based pump, explicit airflow boundary classes, internal fan controller, effectiveness-NTU radiator model, and engine heat-input contract.

The thermostat and fan are driven by `T_h`, not `T_c`.

## M1 does not add

M1 intentionally does not add a second engine solid state, dynamic thermostat actuator, hysteresis state memory, explicit oil state, active grille shutter dynamics, CFD/distributed jacket geometry, or ML residual correction.

## Initialization governance

For synthetic verification, M1 may initialize `T_c = T_h` unless an explicit cold-side initial temperature is supplied. This equal-temperature initialization is not authorized automatically for physical hot-start comparisons. A physical-development manifest must freeze the hidden-state initialization rule before use of consumed Argonne traces.

## Verification gates before physical fitting

M1 must demonstrate hydraulic mass balance, internal coolant transport cancellation, stored-energy conservation, correct zero/full radiator-flow limits, deterministic solutions, RK45 convergence, unchanged V1/M0 behavior, and synthetic identifiability review of `f_h` and any M1-only candidate subset.

M2 is not pre-authorized by this specification.
