# Argonne D3 2012 Ford Focus Data Qualification

## Status

**Acquisition complete. Source qualification and role allocation are complete enough for preregistration. Physical calibration has not started.**

Argonne National Laboratory supplied VTMS with two 2012 Ford Focus archives on 2026-08-17. The comprehensive archive contains the channels required for thermal-model comparison. VTMS-V1 remains `numerical_verified_generic_uncalibrated`; receipt and qualification of controlled data do not constitute physical validation.

## Source fingerprints

| Receipt artifact | Purpose | Size | SHA-256 |
|---|---|---:|---|
| `2012 Ford Focus (1).zip` | Public D3 package, overview, summary, reduced data | 3,534,204 B | `a217682ffabe97b5ba8df266b0f23c351a9e9f209e8c0a0cf4a2aa9ca9325ff2` |
| `2012 Ford Focus (2).zip` | Argonne-supplied comprehensive test data | 15,304,640 B | `cb9b6d1efbd60903468dd932b587e9c2e3bd71f71c4547f4314144bf971cc5d1` |

Both ZIP archives passed integrity checks. Raw Argonne attachments are intentionally not committed because redistribution permission has not been established. VTMS stores fingerprints, reviewed mappings, qualification findings, and role decisions.

## Data provenance

The included master summary identifies the vehicle as a 2012 Ford Focus conventional vehicle with a 2.0 L Ti-VCT GDI inline-four, six-speed automatic transmission, and 2WD configuration.

Fuel information in the supplied summary:

- density: **0.743 g/mL**
- net heating value: **18,344 BTU/lbm**
- converted value used when explicitly declared by VTMS: **42,668,144 J/kg**

The comprehensive archive contains 18 test files and adds the channels needed for controlled thermal work:

- `Time [s]`
- `EngineCoolantTemp[C]`
- `Eng_Spd[RPM]`
- `Dyno_Spd[mph]`
- `Cell_Temp[C]`
- `Eng_FuelFlow_Direct[cc/s]`
- `MAF[g/s]`
- `Load[%]`

Direct bench fuel flow is preferred over the KIT-style MAF proxy. MAF contains impossible spikes and negative values in several received files and is not used as formal heat-input evidence.

## Reviewed VTMS signal mapping

| VTMS signal | Argonne column | Source unit | Use |
|---|---|---|---|
| `time_s` | `Time [s]` | s | comparison time |
| `engine_coolant_temp_c` | `EngineCoolantTemp[C]` | C | measured target |
| `engine_speed_rpm` | `Eng_Spd[RPM]` | rpm | operating/pump input |
| `vehicle_speed_m_s` | `Dyno_Spd[mph]` | mph | vehicle-speed input |
| `ambient_temp_c` | `Cell_Temp[C]` | C | ambient input |
| `fuel_rate_kg_s` | `Eng_FuelFlow_Direct[cc/s]` | cc/s | direct fuel evidence after density conversion |

`ArgonneD3Adapter` supports explicitly mapped TSV/text input, volumetric fuel conversion with declared density, explicit time selection/exclusions, and source SHA-256 provenance. It does not guess schemas or automatically clean ECT.

## CAL-01: 71207062 cold-start UDDS #1

**Frozen role:** three-parameter warm-up calibration stage.

The ECT signal has an invalid initialization period: it reports 99 C through raw time 8.6 s while companion measured temperatures remain near the cold-soak region, then becomes physically consistent at 8.7 s. A small number of obvious later ECT dropouts were also identified from the measurement trace itself before any VTMS residual inspection.

The reviewed mapping starts at 8.7 s and excludes only these source intervals:

- 315.5 to 315.6 s
- 450.5 to 450.6 s
- 453.1 s
- 757.1 to 757.2 s
- 829.7 to 829.8 s
- 1136.6 to 1136.7 s
- 1151.0 to 1151.2 s
- 1309.7 to 1309.8 s

After synthetic pre-fit experimental-design analysis, CAL-01 is restricted to:

1. `wall_heat_fraction`, frozen bound 0.20 to 0.50
2. `engine_thermal_capacitance_j_per_k`, frozen bound 25,000 to 100,000 J/K
3. `engine_coolant_ua_w_per_k`, frozen bound 400 to 2,200 W/K

`radiator_ua_nominal_w_per_k` is fixed during CAL-01.

## CAL-RAD-01: 71207057 1.2 highway x2

**Frozen role:** radiator-UA-only calibration stage.

The warm-up-stage synthetic diagnostic showed radiator UA to be weakly excited relative to the other parameters. The already-received Argonne source measurements were then reviewed without executing VTMS predictions to locate a radiator-active condition.

For source time 0 through 1287.5 s, test 71207057 has:

- 12,876 samples
- complete ECT coverage
- ECT range **91 to 99 C**
- no greater-than-10 C sample jump
- mean dyno speed about **57.31 mph**
- maximum dyno speed **71.742 mph**
- about **92.653%** of samples at or above 40 mph
- about **92.653%** of samples simultaneously at ECT >= 88 C and speed >= 40 mph

No VTMS prediction or residual for 71207057 was inspected when the role was assigned.

CAL-RAD-01 may adjust only `radiator_ua_nominal_w_per_k` within the already-frozen 400 to 2,200 W/K interval. Every non-radiator parameter must come from the frozen CAL-01 output snapshot and may not be reopened.

## Holdouts

### VAL-HOT-01: 71207063

The hot-start UDDS #2 trace has complete ECT coverage and no greater-than-10 C ECT discontinuities at the start. It remains the primary clean independent holdout.

### VAL-SSS-01: 71207052

The 55 mph warm-up trace has complete ECT coverage and remains a secondary independent holdout. It was **not** repurposed for radiator calibration when the staged-fit decision was made.

### Missing cold-start replicate

No separate clean cold-start UDDS replicate was identified in the received package. The eventual validation statement must disclose that limitation.

## Other received tests

- 71207065 highway: not qualified for full-cycle ECT validation because usable ECT ends at approximately 223 s.
- 71207066 US06: not qualified for full-cycle ECT validation because usable ECT ends at approximately 481 s.
- 71207064 UDDS #3: incomplete trace and excluded from the primary formal set.
- 71207072 cold-start idle/no fan: challenge only because ECT coverage is partial.
- 71207053 through 71207056 remain unassigned to the primary formal sequence.

## Physical bounds and pre-fit decision

The complete governed physical bound set was frozen before Argonne residual inspection:

- wall heat fraction: 0.20 to 0.50
- engine thermal capacitance: 25,000 to 100,000 J/K
- engine-to-coolant UA: 400 to 2,200 W/K
- radiator nominal UA: 400 to 2,200 W/K

The bound set is an audit record for the four-parameter calibration universe. The synthetic warm-up-stage diagnostic subsequently established that the parameters should be split into CAL-01 and CAL-RAD-01 rather than fit simultaneously.

## What remains blocked

Before CAL-01:

1. finalize and hash its normalized mapping/preprocessing configuration,
2. freeze the baseline parameter snapshot hash,
3. create the immutable CAL-01 manifest with the exact three-parameter bound subset,
4. only then execute the first physical fit.

Before CAL-RAD-01:

1. freeze the CAL-01 output parameter snapshot,
2. finalize and hash the 71207057 normalized mapping/preprocessing configuration,
3. create an immutable radiator-only manifest referencing the frozen upstream snapshot,
4. only then execute CAL-RAD-01.

Holdouts remain untouched until both calibration stages are frozen.

## Current evidence statement

> Argonne D3 controlled data have been acquired and fingerprinted. Physical calibration bounds and staged calibration roles are frozen before residual inspection. CAL-01 is a three-parameter cold-start warm-up stage and CAL-RAD-01 is a radiator-UA-only highway stage. Controlled calibration and physical holdout validation have not yet been executed.
