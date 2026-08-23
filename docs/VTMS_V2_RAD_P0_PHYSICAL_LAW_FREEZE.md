# VTMS-V2 RAD-P0 Physical-Law and Bounds Freeze

## Status

**Frozen before variable-UA implementation or physical development execution.**

RAD-D1 concluded `RADIATOR_HYPOTHESIS_INCONCLUSIVE`. The documented constant-external-fan primary runs did not localize a radiator-specific residual signature, but they also did not provide sufficient independent air-flow excitation to identify or falsify an air-flow exponent.

RAD-P0 therefore defines a deliberately small, source-informed model-form candidate. It does not claim that variable UA caused the VTMS-V1 validation failure.

## Engineering question

> Does replacing the inherited constant-UA radiator with a physically bounded air-flow-dependent effective UA produce a distinguishable and useful model-form correction without introducing an unidentifiable tuning surface?

The first candidate is **air-side only**. Coolant-side flow dependence is intentionally excluded from the minimum model until a separate identifiability gate earns it.

## Source basis

### Louvered-fin air-side heat transfer

Automotive radiators use compact, typically louvered-fin air-side surfaces. Published correlations are commonly expressed with the Colburn factor `j` as a function of louver-pitch Reynolds number.

For approximately fixed geometry and air properties:

`j = St * Pr^(2/3)` and `St = h / (G * cp)`.

Because `Re` is proportional to air mass velocity `G`, a correlation `j ∝ Re^(-a)` implies approximately:

`h_air ∝ G^(1-a)`.

Publicly reproduced louver-fin correlations include:

- Davenport: `j ∝ Re^-0.42`, implying an air-side `h` exponent near `0.58` over its stated Reynolds-number range. A vehicle-engine-cooling thesis reproduces the correlation and states validity for approximately `100 < Re < 4000` for the cited surface family. Source: https://fileserver-az.core.ac.uk/download/pdf/15618130.pdf
- Chang and Wang generalized louver-fin correlation: `j ∝ Re^-0.49`, implying an `h` exponent near `0.51`; the reviewed correlation is reported over roughly `Re = 100-3000` depending on geometry. A modern review/table reproduces this relation: https://www.mdpi.com/1996-1073/10/6/823
- Chang et al. correlation reported as `j ∝ Re^-0.589` over a lower Reynolds-number range, implying an `h` exponent near `0.41`. A literature table reproducing this and other louver-fin correlations appears in Lin et al. / 1535-RP supporting literature: https://www.researchgate.net/publication/305806908_A_heat_transfer_and_friction_factor_correlation_for_low_air-side_Reynolds_number_applications_of_compact_heat_exchangers_1535-RP

These are geometry-dependent **air-side convection** correlations, not direct Ford Focus overall-UA measurements.

### Low-airflow caution

ASHRAE RP-1535 experimentally studied compact louvered-fin heat exchangers at very low air-side Reynolds number and concluded that separate power-law correlations better represent different low-Re flow regimes. This specifically argues against extending one simple exponent all the way to stagnant air without a zero-flow guard.

Source: https://store.accuristech.com/standards/rp-1535-a-heat-transfer-and-friction-factor-correlation-for-low-air-side-reynolds-number-applications-of-compact

Article DOI: `10.1080/23744731.2016.1203240`.

### Overall radiator resistance

Automotive-radiator experiments using effectiveness-NTU analysis express total thermal resistance as the sum of air-side convection, wall/conduction, and liquid-side convection terms. Experiments report overall heat-transfer coefficient increasing with both air and liquid flow rate.

Source: S.M. Peyghambarzadeh et al., *Applied Thermal Engineering* 52 (2013), DOI `10.1016/j.applthermaleng.2012.11.013`.

This supports rejecting a globally constant effective UA as a universal physical law, but it does **not** provide a unique power-law exponent for this Ford Focus radiator.

### Coolant-side dependence exists but is not frozen into the minimum model

Internal forced-convection correlations can have strong Reynolds-number dependence in the turbulent regime. NASA documentation reproduces the Dittus-Boelter relation `Nu = 0.023 Re^0.8 Pr^0.4` for fully developed turbulent internal flow.

Source: NASA/TM-20220012716, https://ntrs.nasa.gov/api/citations/20220012716/downloads/TM-20220012716.pdf

However, the modeled M0 radiator branch spends substantial time at very low coolant flow. A turbulent `Re^0.8` law therefore cannot be transferred blindly to the complete modeled branch-flow range. A separate automotive modeling source also treats laminar, transitional, and turbulent liquid-side regimes separately and notes that air-side resistance is commonly dominant.

Source: https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/QSHERU/TC-QSHERU-11143_6615.pdf

For this reason RAD-P0 does not add a coolant-flow exponent to the minimum candidate.

## Frozen minimum candidate: RAD-UA-A

For positive radiator air flow:

`UA_eff = radiator_health * UA_ref * (m_air / m_air_ref)^n_air`

with:

- `UA_ref = 1100 W/K` for the minimum structural test
- `m_air_ref = 1.80 kg/s`
- `n_air` discrete envelope: `{0.40, 0.50, 0.60}`
- zero air flow retains the existing radiator zero-heat-transfer branch
- no coolant-flow exponent
- no new thermostat state
- no flow-dependent hydraulic parameter

### Why `m_air_ref = 1.80 kg/s`

This is a **model reference**, not a measured Ford parameter. It is chosen before new model execution because it is approximately the central M0 corrected constant-external-fan effective core-airflow boundary for the primary RAD-D1 runs at `eta_pack = 0.60` and protocol fan capacity `2.50 m3/s`.

Using the central boundary as the normalization point keeps `UA_ref` interpretable: the new law reduces exactly to nominal `UA_ref` near the already-frozen central diagnostic condition.

### Why the exponent set is discrete

The literature supports geometry-dependent louver-fin air-side exponents in roughly the low-0.4 to high-0.5 range after conversion from published `j(Re)` relations. The project therefore freezes `{0.40, 0.50, 0.60}` as a bounded **model-form envelope**, not as three candidate Ford measurements.

The staff review's approximate `n ≈ 0.65` suggestion is retained as hypothesis-generating context but is not promoted to a source-anchored project value.

## Secondary candidate explicitly deferred

A multiplicative coolant-side term such as:

`(m_cool / m_cool_ref)^n_cool`

is **not authorized** in RAD-UA-A.

It may be considered only after RAD-S0 if:

1. the air-only candidate is demonstrably non-identifiable or non-explanatory,
2. a physically defensible liquid-side regime treatment is frozen,
3. a reference radiator-branch flow is sourced or preregistered without residual fitting, and
4. synthetic identifiability shows the new term is distinguishable from `UA_ref`, thermostat/hydraulic behavior, and air-side scaling.

## Existing uncertainty terms

RAD-P0 does not reopen the M0 uncertainty envelope by itself.

The following remain separate variables whose simultaneous fitting is prohibited unless RAD-S0 demonstrates identifiability:

- `UA_ref`
- `eta_pack`
- `f_open`
- `gamma`
- any future `n_cool`

The prior M0 synthetic preflight already found strong confounding between radiator UA and `f_open`. That restriction remains in force.

## Required RAD-S0 synthetic checks

Before any Argonne physical execution of RAD-UA-A:

1. zero air flow produces zero radiator heat rejection,
2. `UA_eff > 0` for positive flow and valid health,
3. `UA_eff = radiator_health * UA_ref` at `m_air = m_air_ref`,
4. heat rejection remains finite and continuous as air flow approaches zero from above,
5. radiator effectiveness remains in `[0,1]`,
6. heat rejection is nondecreasing with air flow across the frozen synthetic operating domain when all other inputs are fixed,
7. existing crossflow zero-flow and equal-temperature limits remain intact,
8. thermal energy conservation remains intact,
9. constant-UA behavior is recovered exactly when `n_air = 0` in a collapse test even though `n_air = 0` is not part of the physical candidate envelope,
10. sensitivity/identifiability is evaluated against `UA_ref`, `eta_pack`, `f_open`, and `gamma` before any fit subset is authorized.

## RAD-F0 physical-use restriction

If RAD-S0 passes, physical feasibility uses only already-consumed development evidence and starts with the lowest-order corrected topology.

Because the primary constant-fan runs sit close to the normalization flow, a weak result is expected to be informative: if RAD-UA-A cannot materially alter the residual under its own frozen physical envelope, that is evidence that the review's air-side variable-UA mechanism is not the principal cause of the Argonne failure even though flow-dependent UA remains a better general radiator formulation.

No blind evidence may be opened in RAD-F0.

## Claims prohibited by this freeze

RAD-P0 does not establish:

- the Ford Focus radiator geometry,
- Ford-specific louver Reynolds number,
- a measured core air-flow rate,
- a measured `UA_ref`,
- a measured air exponent,
- a radiator root cause,
- validation of a revised model.
