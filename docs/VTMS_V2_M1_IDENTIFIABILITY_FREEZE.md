# VTMS-V2 M1 Synthetic Identifiability Freeze

## Gate decision

**Gate V2-M1-I1: PASS WITH STAGE RESTRICTIONS.**

This gate uses deterministic synthetic excitation only. It does not use Argonne residuals, does not inspect reserved blind evidence, and does not authorize physical calibration by itself.

## New topology parameter

M1 introduces one structural parameter that partitions the already-frozen total coolant thermal capacitance:

\[
f_h = C_h / C_{coolant,total}
\]

The synthetic preflight shows that `hot_coolant_capacitance_fraction` produces a measurable and locally distinguishable ECT signature:

- RMS fractional sensitivity: **1.13887 C**
- peak absolute fractional sensitivity: **4.72689 C**
- topology-only condition number: **1.0**

Therefore the new M1 state split is not numerically invisible under the frozen synthetic excitation.

## Topology plus engine-thermal subset

The subset

- `hot_coolant_capacitance_fraction`
- `engine_thermal_capacitance_j_per_k`
- `engine_coolant_ua_w_per_k`

is full rank with:

- condition number: **4.49814**
- strongest absolute pairwise cosine: **0.876891**
- no weak parameters under the preregistered threshold

This subset is mathematically admissible for a future governed development stage. The engine-capacitance / engine-coolant-UA relationship remains strong enough that covariance and parameter-bound pressure must be reported and neither value may be presented as a uniquely measured physical property.

## Heat-rejection restriction remains

The subset

- `hot_coolant_capacitance_fraction`
- `radiator_ua_nominal_w_per_k`
- `f_open`
- `gamma`

is **not** authorized as one fitting stage. Radiator UA and `f_open` remain almost collinear, with absolute cosine approximately **0.982833**.

The complete six-parameter candidate set is therefore also prohibited as a simultaneous physical fit.

## Frozen stage rules

1. Do not optimize all M1 parameters simultaneously.
2. Do not optimize radiator UA and `f_open` in the same stage from ECT alone.
3. `eta_pack` remains an airflow-boundary uncertainty term rather than an ECT calibration parameter.
4. `f_closed` remains fixed for the initial M1 program.
5. The new hot/cold capacitance split may be investigated only under a preregistered physical-development manifest.
6. Hidden cold-side initialization may not be freely fitted per run.
7. Reserved blind evidence remains closed.

## Software verification status

The M1 implementation passed the repository test workflow on Python 3.11, 3.12, and 3.13. Python 3.11 reported **118 passing tests**. The API container, web build, and web-container checks also passed. The M1 synthetic preflight completed successfully in CI.

## Next gate

The next gate is a physical-development manifest using only already-consumed evidence. That manifest must freeze:

- exact dataset identities and fingerprints;
- preprocessing locks;
- airflow boundary treatment;
- hidden `T_cold(0)` handling;
- admissible parameter stages and bounds;
- nuisance sensitivity cases;
- objective functions and acceptance metrics;
- parameter-bound and covariance diagnostics;
- the rule for whether M1 earns access to an independent blind rung.

Until that manifest is committed, **M1 physical calibration remains unauthorized**.
