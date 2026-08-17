# Argonne D3 2012 Ford Focus Data Qualification

## Status

**Acquisition complete. Qualification and mapping are in progress. Calibration has not started.**

Argonne National Laboratory supplied VTMS with two 2012 Ford Focus archives on 2026-08-17 in response to the project's request for controlled dynamometer data. The received material includes the public D3 package plus a more comprehensive set of test files containing the channels needed for thermal-model comparison.

VTMS-V1 remains `numerical_verified_generic_uncalibrated`. Receipt of controlled data does not change the model classification and does not constitute physical validation.

## Source fingerprints

| Receipt artifact | Purpose | Size | SHA-256 |
|---|---|---:|---|
| `2012 Ford Focus (1).zip` | Public D3 package, overview, summary, reduced data | 3,534,204 B | `a217682ffabe97b5ba8df266b0f23c351a9e9f209e8c0a0cf4a2aa9ca9325ff2` |
| `2012 Ford Focus (2).zip` | Argonne-supplied comprehensive test data | 15,304,640 B | `cb9b6d1efbd60903468dd932b587e9c2e3bd71f71c4547f4314144bf971cc5d1` |

Both ZIP archives passed ZIP integrity checks before analysis.

The raw Argonne attachments are intentionally **not committed** to this repository. VTMS stores fingerprints, reviewed mappings, test-role decisions, and qualification findings while the original source files remain immutable outside version control. This avoids redistributing Argonne-supplied attachments without an explicit redistribution determination.

## Data provenance and attribution

Data source: Argonne National Laboratory Downloadable Dynamometer Database (D3), 2012 Ford Focus conventional vehicle dataset. The included master summary identifies the test vehicle as a 2012 Ford Focus with a 2.0 L Ti-VCT GDI inline-four, six-speed automatic transmission, and 2WD configuration.

The included master summary reports the test fuel as Tier II EEE HF437 with:

- fuel density: **0.743 g/mL**
- net heating value: **18,344 BTU/lbm**
- converted net heating value used by VTMS when explicitly declared: **42,668,144 J/kg**

Any VTMS publication, report, repository result, or presentation that uses these data must reference the Argonne D3 dataset. VTMS will also keep Argonne informed of notable project progress, consistent with the request from the Argonne contact who supplied the files.

## What the comprehensive files add

The smaller public package contains five reduced test files with nine columns. Those files include time, dyno speed, tractive effort, cell temperature, RH, phase, engine speed, engine oil temperature, and bench modal fuel flow, but **not engine coolant temperature**.

The comprehensive archive contains 18 test files covering test IDs 71207051 through 71207072 and adds the channels required for VTMS thermal comparison, including:

- `Time [s]`
- `EngineCoolantTemp[C]`
- `Eng_Spd[RPM]`
- `Dyno_Spd[mph]`
- `Cell_Temp[C]`
- `Eng_FuelFlow_Direct[cc/s]`
- `MAF[g/s]`
- `Load[%]`

For the five tests present in both packages, the reduced and comprehensive files have identical timestamps. Shared numeric channels agree to within approximately 0.0005 in source units, consistent with formatting/rounding differences. This supports treating the comprehensive files as the same underlying controlled tests with additional instrumentation.

## Reviewed VTMS signal mapping

| VTMS logical signal | Argonne source column | Source unit | VTMS use |
|---|---|---|---|
| `time_s` | `Time [s]` | s | comparison time |
| `engine_coolant_temp_c` | `EngineCoolantTemp[C]` | C | measured validation target |
| `engine_speed_rpm` | `Eng_Spd[RPM]` | rpm | pump/operating input |
| `vehicle_speed_m_s` | `Dyno_Spd[mph]` | mph | controlled vehicle-speed input |
| `ambient_temp_c` | `Cell_Temp[C]` | C | controlled ambient input |
| `fuel_rate_kg_s` | `Eng_FuelFlow_Direct[cc/s]` | cc/s | direct fuel evidence after density conversion |
| `mass_air_flow_g_s` | `MAF[g/s]` | g/s | diagnostic only, not formal heat-input evidence |

The direct bench fuel-flow signal is preferred over the MAF proxy used in the KIT plausibility exercise. `Eng_FuelFlow_Direct[cc/s]` is converted to mass flow using the explicitly documented 0.743 g/mL fuel density. Controlled VTMS execution still requires an explicitly supplied lower heating value before converting fuel mass flow to fuel energy.

MAF contains obvious impossible spikes and negative values in several comprehensive files. It is retained only as optional diagnostic evidence and is not used to derive controlled heat input.

## Primary test qualification

### 71207062: UDDS #1 cold start

**Role candidate:** `CAL-01` calibration.

The master summary identifies test 71207062 as the 21 C UDDS #1 cold-start test. It is the strongest available calibration candidate because it contains the desired cold-start warm-up transient and direct fuel evidence.

The ECT channel is not valid at file initialization. It reports 99 C through raw time 8.6 s while oil temperature is approximately 24 C, then changes to a physically consistent 25 C at 8.7 s. The trace also contains a small number of obvious half-scale/dropout samples later in the cycle.

No model residual was used to identify these artifacts. They were identified from the measurement trace itself before calibration.

The reviewed mapping therefore starts at raw time 8.7 s and explicitly excludes only the following source-time intervals:

- 315.5 to 315.6 s
- 450.5 to 450.6 s
- 453.1 to 453.1 s
- 757.1 to 757.2 s
- 829.7 to 829.8 s
- 1136.6 to 1136.7 s
- 1151.0 to 1151.2 s
- 1309.7 to 1309.8 s

The raw source file fingerprint is recorded in the inventory and mapping configuration.

### 71207063: UDDS #2 hot start

**Role candidate:** `VAL-HOT-01` independent holdout.

Test 71207063 has complete ECT coverage across the received trace and no greater-than-10 C sample-to-sample ECT discontinuities from the test start. It is reserved as the primary clean holdout candidate before any Argonne calibration occurs.

This is a hot-start test, so it cannot replace an independent cold-start replicate. Because the received package does not contain a separate clean cold-start UDDS replicate, the eventual validation claim must explicitly state that limitation.

### 71207065: highway

**Status:** not qualified as a full-cycle holdout.

The received comprehensive file contains ECT only through approximately 223 s, after which the channel is predominantly zero/unavailable. The cycle remains valuable for other signals, but it should not be presented as a full-cycle coolant-temperature holdout without a separately preregistered partial-window protocol.

### 71207066: US06

**Status:** not qualified as a full-cycle holdout.

The received comprehensive file contains usable ECT only through approximately 481 s. The rest of the cycle lacks a valid complete coolant-temperature target. It should not be used as a full-cycle formal holdout under the current protocol.

### 71207064: UDDS #3

**Status:** excluded from the primary formal set.

The Argonne master summary notes that test data stopped and were saved after approximately 505 s. The comprehensive file also has incomplete ECT coverage. This run is therefore not selected as the formal hot-start holdout.

### 71207072: cold-start idle, no fan

**Role candidate:** challenge only.

The master summary identifies this as a cold-start idle test with no fan and later WOT events after oil temperature reached 85 C. Its ECT channel has initialization artifacts and long unavailable periods. It is useful as a challenge/data-quality case, not as a clean substitute for a cold-start UDDS replicate.

## Other useful received tests

Several Day 2 tests have complete ECT coverage and may be reserved as secondary diagnostic or holdout candidates before calibration if needed:

- 71207052: SSS 55 mph warm-up
- 71207053: UDDS cycle beating
- 71207054: 1.2 UDDS aggressive driving
- 71207055: 1.4 UDDS aggressive driving
- 71207056: SSS 0-80-0
- 71207057: 1.2 highway aggressive driving

They are not silently substituted for the originally requested standard-cycle holdouts. Any role change must be recorded before fitting and based on data availability/quality, not on VTMS residuals.

## Adapter changes required by the received data

The original Argonne adapter intentionally supported only explicitly mapped CSV because no D3 schema had been received. The actual comprehensive data use tab-separated text files and direct volumetric fuel flow. The adapter is therefore extended to support:

1. explicitly mapped TSV/text parsing,
2. `cc/s` source fuel-flow conversion using a required positive fuel density,
3. explicit source-time row selection and exclusion intervals,
4. recording row-selection provenance in normalized dataset metadata,
5. preserving the original raw source-file SHA-256,
6. continuing to refuse schema guessing or automatic ECT cleaning.

The adapter does **not** infer bad ECT samples. Any exclusions must be declared in the reviewed mapping.

## Engine-speed reference-domain note

The received Argonne traces include normal idle samples below VTMS-V1's 700 rpm scenario-domain floor. This is measured evidence, not an invalid source record.

The validation dataset contract therefore stores nonnegative measured RPM without forcing it into the model domain. The comparison runner projects nonzero RPM values into the frozen 700 to 6500 rpm VTMS reference domain and records that projection as preprocessing metadata.

For the current validation path this projection does not alter the heat-input evidence because controlled heat input comes from direct fuel flow rather than the generic RPM/load heat estimator. The projection is used only to keep the measured operating profile compatible with the frozen V1 component domain.

## Preregistered role decisions

Before any Argonne parameter fit:

- `CAL-01`: test 71207062, calibration candidate after explicit ECT QC
- `VAL-HOT-01`: test 71207063, independent hot-start holdout candidate
- `VAL-HWY-01`: test 71207065, **not qualified for full-cycle ECT validation**
- `VAL-US06-01`: test 71207066, **not qualified for full-cycle ECT validation**
- `VAL-CS-01`: no separate clean cold-start UDDS replicate identified in the received package
- `CHALLENGE-IDLE-CS-01`: test 71207072, challenge candidate only

No model prediction residuals have been used to select these roles.

## What is still blocked

Physical calibration must **not** start yet.

The following remain required before the first controlled fit:

1. freeze physically justified bounds for the four preregistered calibration parameters,
2. finalize and hash the CAL-01 normalized mapping/preprocessing configuration,
3. create the immutable CAL-01 manifest with the exact raw-file and parameter-snapshot hashes,
4. freeze the holdout role reservations before observing model residuals,
5. execute calibration only after those controls are complete.

Synthetic demonstration bounds are not Argonne bounds and must not be reused.

## Current evidence statement

After receipt of these files, the correct VTMS status is:

> Argonne D3 controlled data have been acquired and fingerprinted. Signal mapping and data qualification are in progress. Controlled calibration and physical holdout validation have not yet been executed.

That statement should remain until the governed calibration/holdout workflow produces actual physical comparison results.
