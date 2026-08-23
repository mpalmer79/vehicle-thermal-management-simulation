# VTMS-V2 M2 Synthetic Identifiability Freeze

## Gate

**V2-M2-I1: PASS FOR MODEL-FORM FEASIBILITY WITH STRONG STAGE RESTRICTIONS.**

The M2 equations, conservation tests, exact nested collapse to M1, and synthetic sensitivity runner execute successfully. The result does **not** authorize fitting the complete M2 parameter set to physical ECT data.

No physical measurement or reserved blind prediction was used in this gate.

## Software verification

GitHub Actions run `32543422581` passed:

- Python 3.11, 3.12, and 3.13 test jobs;
- 126 tests on Python 3.11;
- pre-Argonne V1 identifiability preflight;
- M0 synthetic identifiability preflight;
- M1 synthetic identifiability preflight;
- M2 synthetic identifiability preflight;
- API container;
- web dependency audit, lint, typecheck, unit tests, and build;
- web container smoke test.

The M2 test suite includes the required conservation identity and the exact M2-to-M1 nested-collapse regression.

## New M2 topology result

The three new M2 topology quantities are:

- `head_thermal_capacitance_fraction`;
- `head_heat_fraction`;
- `head_block_ua_w_per_k`.

At the frozen synthetic reference point, the three-column normalized Jacobian is full rank, but practical identifiability is poor:

- numerical rank: **3**;
- condition number: **52.9712**;
- strongest absolute pairwise cosine: **0.997603**;
- weak parameter: `head_block_ua_w_per_k`.

The dominant confounding is:

`head_thermal_capacitance_fraction` vs `head_heat_fraction`

with cosine approximately `-0.997603`.

Their ECT sensitivity magnitudes are also nearly equal:

- head-capacitance fraction RMS sensitivity: **0.05977 C** per 1% fractional perturbation;
- head heat fraction RMS sensitivity: **0.05889 C**;
- head/block UA RMS sensitivity: **0.000338 C**.

The model therefore exposes a physically understandable but ECT-unidentifiable trade: shifting effective storage toward the fast state can be compensated by shifting heat deposition in the opposite direction.

## Relative excitation versus retained M1 quantities

In the six-parameter M2 core diagnostic:

- total engine thermal capacitance RMS sensitivity: **9.0668 C**;
- engine-coolant UA RMS sensitivity: **4.6876 C**;
- hot-coolant capacitance fraction RMS sensitivity: **1.1385 C**;
- head-capacitance fraction RMS sensitivity: **0.05977 C**;
- head heat fraction RMS sensitivity: **0.05889 C**;
- head/block UA RMS sensitivity: **0.000338 C**.

The complete six-parameter diagnostic is full rank mathematically but has:

- condition number: **54.1390**;
- strongest pairwise cosine: **0.997603**;
- all three new M2 topology quantities weak relative to the strongest ECT sensitivity.

A full continuous ECT-only fit would therefore create numerical parameter estimates without defensible physical identification.

## Frozen restrictions

The following rules are now mandatory for the first M2 physical-development stage.

### Prohibited

- Do not continuously optimize `head_thermal_capacitance_fraction`, `head_heat_fraction`, and `head_block_ua_w_per_k` together.
- Do not report any of the three as identified Ford Focus physical properties.
- Do not use a best-fit topology ranking to choose one M2 structure after viewing consumed-development residuals.
- Do not widen a topology bound because a consumed physical trace fails.
- Do not fit hidden hot-start solid temperatures per run.
- Do not open the M2 blind reserve.

### Authorized

- Evaluate the three new M2 topology quantities only as a preregistered discrete engineering envelope.
- Treat `head_block_ua_w_per_k` as a discrete nuisance/model-form case because ECT provides essentially no local information about it.
- Treat head storage split and heat-deposition split as discrete paired model-form cases, not simultaneous continuously identified quantities.
- Continue to vary already-governed engine and coolant parameters only through frozen discrete feasibility grids when required to falsify the model family.
- Use consumed 71207062 and 71207063 as development evidence under a new manifest.

## Physical meaning of the restriction

The M2 question is not "what is the Ford Focus head capacitance fraction?"

The M2 question is:

> Does allowing two engine solid thermal time scales create any bounded, physically interpretable model family that can explain the already-consumed cold-start and hot-start evidence jointly, without changing the thermostat model or opening blind evidence?

That question can be answered by a discrete feasibility envelope even though the individual topology parameters cannot be uniquely estimated from ECT.

## Next gate

Before physical execution, freeze `VTMS-V2-M2-DEV-01` with:

1. consumed development source identities and preprocessing;
2. a discrete M2 topology grid;
3. retained M1 engine/coolant uncertainty cases;
4. explicit hot-start initialization cases for `T_head`, `T_block`, and `T_cold`;
5. the same project acceptance criteria;
6. a staged cold-first joint-feasibility algorithm;
7. a rule for when the existing M1 control-boundary envelope may be opened;
8. zero access to the M2 blind reserve.
