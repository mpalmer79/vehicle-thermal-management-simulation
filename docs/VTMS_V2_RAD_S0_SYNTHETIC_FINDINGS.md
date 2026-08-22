# VTMS-V2 RAD-S0 Synthetic Verification and Identifiability Findings

## Decision

**RAD-S0 FAIL. The minimum RAD-UA-A air-flow-dependent radiator candidate is numerically verified but is not sufficiently distinguishable from the existing radiator/control compensators to authorize physical Argonne execution.**

This is synthetic development evidence only. No new Argonne residual was used, no reserved blind evidence was opened, no physical parameter was fitted, and no preregistered threshold was changed after inspection.

## Candidate tested

The frozen minimum candidate was:

```text
UA_eff = UA_ref * (m_air / m_air_ref)^n_air
```

for active coolant and air flow, with:

```text
UA_ref = 1100 W/K
m_air_ref = 1.8 kg/s
n_air = {0.40, 0.50, 0.60}
```

The local identifiability reference used `n_air = 0.50`.

A coolant-side exponent remained excluded.

## Numerical verification

The candidate passed every preregistered numerical/limiting-behavior check:

- zero coolant or zero air flow gives zero radiator heat transfer;
- at `m_air = 1.8 kg/s`, the candidate collapses exactly to the inherited constant-UA radiator;
- with `n_air = 0`, it collapses exactly to constant UA across the active-flow test domain;
- effectiveness remains in `[0, 1]`;
- heat rejection is monotonic with increasing air flow over the frozen synthetic domain;
- deterministic reruns are identical;
- normalized energy residual = `5.59722443237863e-4`, below the frozen `0.001` ceiling.

The default-versus-tight solver coolant-trace difference was small:

```text
RMS  = 0.001888 C
peak = 0.010165 C
```

The discrete exponent candidates were separated by far more than that numerical noise.

## Discrete exponent separation

### 0.40 versus 0.50

```text
RMS coolant-trace difference  = 2.12218 C
peak coolant-trace difference = 3.89070 C
required RMS separation       = 0.03776 C
required peak separation      = 0.20330 C
PASS
```

### 0.50 versus 0.60

```text
RMS coolant-trace difference  = 2.23766 C
peak coolant-trace difference = 4.09036 C
required RMS separation       = 0.03776 C
required peak separation      = 0.20330 C
PASS
```

Therefore the exponent itself is not numerically invisible.

## Local sensitivity

Fractional coolant-trace sensitivity at the frozen reference point:

| Parameter | RMS sensitivity C | Relative to strongest |
|---|---:|---:|
| `radiator_ua_nominal_w_per_k` | 45.1591 | 1.0000 |
| `eta_pack` | 40.6674 | 0.9005 |
| `f_open` | 14.0600 | 0.3113 |
| `n_air` | 10.8910 | 0.2412 |
| `gamma` | 0.7975 | 0.01766 |

`n_air` therefore passes the frozen minimum relative-sensitivity requirement of `0.02` by a wide margin.

## Why the gate failed

The normalized five-column sensitivity Jacobian had:

```text
condition number = 393.747
frozen maximum   = 100
FAIL
```

The strongest absolute cosine involving `n_air` was:

```text
|cos(n_air, eta_pack)| = 0.950693
frozen exclusive limit = 0.95
FAIL
```

Other major confounding is even stronger:

```text
|cos(UA_ref, eta_pack)| = 0.998513
|cos(UA_ref, f_open)|   = 0.992483
|cos(eta_pack, f_open)| = 0.992090
|cos(n_air, f_open)|    = 0.947094
|cos(n_air, UA_ref)|    = 0.933761
```

The smallest normalized-Jacobian singular value was only `0.0050768`, producing the high condition number.

## Interpretation

The negative result is more specific than saying "variable UA does not matter."

It shows three things simultaneously:

1. The proposed air-side power law is numerically coherent.
2. The discrete exponent choices create a large enough synthetic temperature signature to be observable in principle.
3. In the current M0 radiator/control parameterization, that signature is not sufficiently independent of `UA_ref`, `eta_pack`, and radiator hydraulic terms to support a governed physical inference.

Accordingly, an Argonne fit or feasibility sweep using `n_air` now would risk adding another compensating parameter rather than resolving the model-form question.

## Governance consequence

The machine-readable RAD-S0 manifest froze the consequence before execution:

> If RAD-S0 fails, preserve the negative result and resume the frozen M2 Stage B execution without variable UA.

Therefore:

- RAD-UA-A physical Argonne execution is **blocked**;
- no exponent is promoted or fitted;
- the radiator-UA reference and airflow bounds are not changed;
- the M2 grid, solver settings, and acceptance thresholds remain unchanged;
- M3 remains unauthorized;
- reserved blind evidence remains unopened.

The next scientific task is to resume the authoritative independent-solver M2 Stage B sequence from the last durable committed checkpoint.

## Reproducibility

Authoritative result artifact:

`validation_outputs/VTMS_V2_RAD_S0_SYNTHETIC_IDENTIFIABILITY.json`

Frozen preregistration:

`validation_configs/vtms_v2_rad_s0_identifiability_manifest.json`

Implementation:

`src/vtms_v2/rad_s0.py`

The result was reproduced in GitHub Actions on Python 3.11.16 with NumPy 2.4.6 and SciPy 1.17.1.
