# VTMS-V2 M0 FEAS-01 Development Feasibility Findings

## Status

**FEAS-01 complete. Corrected-control M0 has zero jointly feasible configurations under the preregistered envelope with the inherited CAL-01 thermal snapshot.**

This is consumed-development evidence, not validation. No reserved V2 blind prediction was generated or inspected. No best-fit grid point is selected or reported as a vehicle-specific parameter estimate.

## Question tested

FEAS-01 asked a deliberately narrow question:

> Holding the previously consumed CAL-01 effective thermal snapshot fixed, can any globally shared M0 combination of thermostat full-open uncertainty, external-fan-to-core transfer, radiator UA, fully-open radiator branch fraction, and hydraulic shape satisfy both the consumed cold-start and hot-start development runs?

The two development tests were:

- `71207062`, UDDS #1 cold start;
- `71207063`, UDDS #2 hot start.

Both are documented as constant-speed external-cooling-fan, hood-up tests, allowing one common M0 boundary class without using dyno speed as radiator-core airflow.

## Frozen grid

The preregistered grid contained 810 globally shared M0 configurations:

```text
thermostat_full_c = 97.0, 99.5, 102.0
eta_pack = 0.10, 0.25, 0.40, 0.60, 0.80, 1.00
radiator_ua_nominal_w_per_k = 400, 700, 1100, 1600, 2200
f_open = 0.85, 0.925, 1.00
gamma = 0.50, 1.00, 2.00
```

Fixed terms included:

- thermostat opening onset = 87.8 C;
- `f_closed = 0.02`;
- V1 RPM-based pump model;
- AGS absent/full-open primary case;
- external fan protocol capacity = 2.50 m3/s;
- CAL-01 effective thermal snapshot:
  - wall heat fraction = 0.4999228433;
  - engine thermal capacitance = 52393.9078 J/K;
  - engine-to-coolant UA = 2198.4326 W/K.

The CAL-01 thermal values retain their historical boundary-pressure warning. FEAS-01 does not reinterpret them as uniquely identified physical properties.

## Result

```text
Grid points evaluated:                    810
Jointly feasible grid points:               0
Joint feasible fraction:                   0%
Cold-start 71207062 passing grid points:  272
Hot-start 71207063 passing grid points:      0
```

Because no grid point passed both development runs, there is no feasible parameter range to report for any varied term.

### Failure accounting

Across 1,620 test/grid comparisons:

- whole-trace acceptance failures: 1,348;
- hot-region failures: 810;
- hot-region non-evaluable cases: 810.

The hot-region non-evaluable cases belong to the cold-start development run because its selected measured trace does not provide the required 96 to 100 C coverage. The hot-start run does provide that coverage, and all 810 M0 grid configurations fail the frozen hot-region criterion there.

## Interpretation

The result is stronger than the earlier one-parameter counterfactuals.

M0 was given broad preregistered freedom in the major corrected heat-rejection/control uncertainties while preserving:

- a physically anchored thermostat opening onset;
- a wide thermostat full-open envelope;
- a six-level external-fan-to-core transfer uncertainty;
- the complete frozen radiator-UA range;
- the complete frozen `f_open` range;
- the complete frozen hydraulic-shape range.

Despite that flexibility, **no configuration can satisfy the consumed hot-start development run under the inherited CAL-01 thermal snapshot.**

This means the earlier V1 hot-region failure cannot be repaired solely by choosing a different credible combination of these M0 thermostat, hydraulic, airflow-transfer, and radiator-UA terms while retaining that thermal snapshot.

## What FEAS-01 does not prove

FEAS-01 does not prove that every mathematically possible two-state engine/coolant model must fail.

Specifically, it did not refit simultaneously:

- wall heat fraction;
- effective engine thermal capacitance;
- engine-to-coolant UA;
- pump-flow coefficients;
- operating-dependent heat partition;
- dynamic thermostat behavior;
- additional thermal states.

The first three were intentionally inherited from CAL-01 to test whether corrected controls alone could rescue the existing thermal topology. The remaining items are excluded or reserved by the model hierarchy.

Therefore the correct conclusion is:

> **M0 corrected-control feasibility fails with the inherited V1/CAL-01 thermal snapshot. A further two-state thermal re-identification would be required to exhaust M0 completely, but control-boundary correction alone is no longer a viable explanation of the hot-start failure.**

## Solver execution check

The 810-point envelope was accelerated by integrating the independent M0 systems in one vectorized RK45 calculation per development test using the same:

- governing equations;
- RK45 method;
- `rtol = 1e-6`;
- `atol = 1e-8`;
- maximum step = 1 s.

Three deterministic grid locations were then rerun through the scalar M0 equations independently. Pass/fail classifications matched for both development tests at all three locations, including one cold-start passing configuration and the corresponding hot-start failure.

No parameter ranking or best-fit selection was performed.

## Governance consequence

FEAS-01 does **not** open the M0 blind holdout `71207054`.

Before M1 can be formally promoted, the project must make one final M0 decision:

1. either preregister and execute a globally constrained two-state thermal re-identification on consumed development evidence; or
2. document why the existing CAL-01 thermal bound pressure plus FEAS-01 failure is sufficient to reject further M0 identification as likely compensating-parameter tuning.

The preferred engineering path is to perform one final **M0 global thermal feasibility test**, not an unconstrained optimizer. It should preserve the existing physical bounds and ask whether any globally shared two-state thermal parameter set can satisfy both cold-start and hot-start development evidence under fixed, preregistered M0 boundary cases.

Only after that result should the project formally pass or fail the M0-to-M1 promotion gate.
