from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product
from typing import Iterable

import numpy as np

from vtms_v1.scenario import Scenario
from vtms_v1.types import FaultState
from vtms_v2.m0.airflow import AirflowBoundary, AirflowBoundaryClass
from vtms_validation.dataset import ValidationDataset
from vtms_validation.metrics import ValidationMetrics, calculate_metrics

from .config import M2Parameters
from .simulation import M2SimulationRunner


FUEL_DENSITY_G_PER_ML = 0.743
FUEL_LHV_J_PER_KG = 42_668_144.0

HEAD_THERMAL_CAPACITANCE_FRACTIONS = (0.15, 0.35, 0.50, 0.60)
HEAD_HEAT_FRACTIONS = (0.50, 0.70, 0.95)
HEAD_BLOCK_UA_W_PER_K = (100.0, 800.0, 3000.0)
HOT_COOLANT_CAPACITANCE_FRACTIONS = (0.20, 0.35, 0.50, 0.65, 0.80)
WALL_HEAT_FRACTIONS = (0.20, 0.35, 0.50)
ENGINE_THERMAL_CAPACITANCES_J_PER_K = (25_000.0, 52_393.90776670539, 100_000.0)
ENGINE_COOLANT_UA_W_PER_K = (400.0, 1000.0, 1600.0, 2200.0)

THERMOSTAT_FULL_C = (97.0, 99.5, 102.0)
ETA_PACK = (0.25, 0.40, 0.80)
RADIATOR_UA_W_PER_K = (400.0, 1100.0, 2200.0)
F_OPEN = (0.85, 0.95, 1.0)
GAMMA = (0.5, 1.0, 2.0)

STRUCTURAL_GRID = tuple(
    product(
        HEAD_THERMAL_CAPACITANCE_FRACTIONS,
        HEAD_HEAT_FRACTIONS,
        HEAD_BLOCK_UA_W_PER_K,
        HOT_COOLANT_CAPACITANCE_FRACTIONS,
        WALL_HEAT_FRACTIONS,
        ENGINE_THERMAL_CAPACITANCES_J_PER_K,
        ENGINE_COOLANT_UA_W_PER_K,
    )
)
CONTROL_GRID = tuple(
    product(
        THERMOSTAT_FULL_C,
        ETA_PACK,
        RADIATOR_UA_W_PER_K,
        F_OPEN,
        GAMMA,
    )
)

STRUCTURAL_CASE_COUNT = len(STRUCTURAL_GRID)
CONTROL_CASE_COUNT = len(CONTROL_GRID)
GLOBAL_CASE_COUNT = STRUCTURAL_CASE_COUNT * CONTROL_CASE_COUNT

if STRUCTURAL_CASE_COUNT != 6480:
    raise RuntimeError("M2 Stage B structural grid must contain exactly 6480 cases")
if CONTROL_CASE_COUNT != 243:
    raise RuntimeError("M2 Stage B control grid must contain exactly 243 cases")
if GLOBAL_CASE_COUNT != 1_574_640:
    raise RuntimeError("M2 Stage B complete cross must contain exactly 1,574,640 cases")


@dataclass(frozen=True)
class StageBCase:
    global_index: int
    structural_index: int
    control_index: int
    head_thermal_capacitance_fraction: float
    head_heat_fraction: float
    head_block_ua_w_per_k: float
    hot_coolant_capacitance_fraction: float
    wall_heat_fraction: float
    engine_thermal_capacitance_j_per_k: float
    engine_coolant_ua_w_per_k: float
    thermostat_full_c: float
    eta_pack: float
    radiator_ua_nominal_w_per_k: float
    f_open: float
    gamma: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)

    def parameters(self) -> M2Parameters:
        return M2Parameters(
            head_thermal_capacitance_fraction=self.head_thermal_capacitance_fraction,
            head_heat_fraction=self.head_heat_fraction,
            head_block_ua_w_per_k=self.head_block_ua_w_per_k,
            hot_coolant_capacitance_fraction=self.hot_coolant_capacitance_fraction,
            wall_heat_fraction=self.wall_heat_fraction,
            engine_thermal_capacitance_j_per_k=self.engine_thermal_capacitance_j_per_k,
            engine_coolant_ua_w_per_k=self.engine_coolant_ua_w_per_k,
            thermostat_open_c=87.8,
            thermostat_full_c=self.thermostat_full_c,
            f_closed=0.02,
            f_open=self.f_open,
            gamma=self.gamma,
            eta_pack=self.eta_pack,
            external_fan_capacity_m3_s=2.50,
            ags_static_restriction_factor=1.0,
            radiator_ua_nominal_w_per_k=self.radiator_ua_nominal_w_per_k,
        )


def case_from_global_index(global_index: int) -> StageBCase:
    if not 0 <= global_index < GLOBAL_CASE_COUNT:
        raise IndexError(
            f"global_index must be in [0, {GLOBAL_CASE_COUNT}), got {global_index}"
        )
    structural_index, control_index = divmod(global_index, CONTROL_CASE_COUNT)
    structural = STRUCTURAL_GRID[structural_index]
    control = CONTROL_GRID[control_index]
    return StageBCase(
        global_index=global_index,
        structural_index=structural_index,
        control_index=control_index,
        head_thermal_capacitance_fraction=float(structural[0]),
        head_heat_fraction=float(structural[1]),
        head_block_ua_w_per_k=float(structural[2]),
        hot_coolant_capacitance_fraction=float(structural[3]),
        wall_heat_fraction=float(structural[4]),
        engine_thermal_capacitance_j_per_k=float(structural[5]),
        engine_coolant_ua_w_per_k=float(structural[6]),
        thermostat_full_c=float(control[0]),
        eta_pack=float(control[1]),
        radiator_ua_nominal_w_per_k=float(control[2]),
        f_open=float(control[3]),
        gamma=float(control[4]),
    )


def iter_stage_b_cases(start: int = 0, stop: int = GLOBAL_CASE_COUNT) -> Iterable[StageBCase]:
    if not 0 <= start <= stop <= GLOBAL_CASE_COUNT:
        raise ValueError("Stage B iteration range must satisfy 0 <= start <= stop <= GLOBAL_CASE_COUNT")
    for global_index in range(start, stop):
        yield case_from_global_index(global_index)


def _project_engine_speed(engine_speed_rpm: np.ndarray) -> np.ndarray:
    projected = np.asarray(engine_speed_rpm, dtype=float).copy()
    projected[(projected > 0.0) & (projected < 700.0)] = 700.0
    projected[projected > 6500.0] = 6500.0
    return projected


def _profile(dataset: ValidationDataset, values: np.ndarray):
    return lambda time_s: dataset.interp(values, time_s)


def _first_crossing(time_s: np.ndarray, values: np.ndarray, threshold_c: float) -> float | None:
    idx = np.flatnonzero(values >= threshold_c)
    if idx.size == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(time_s[0])
    t0, t1 = float(time_s[i - 1]), float(time_s[i])
    y0, y1 = float(values[i - 1]), float(values[i])
    if y1 == y0:
        return t1
    return t0 + (threshold_c - y0) / (y1 - y0) * (t1 - t0)


@dataclass(frozen=True)
class StageBAcceptance:
    passed: bool
    rmse_pass: bool
    mae_pass: bool
    bias_pass: bool
    p90_pass: bool
    arrival_pass: bool
    hot_region_pass: bool
    hot_region_evaluable: bool
    arrival_errors_s: dict[str, float | None]
    missing_predicted_crossings_c: tuple[float, ...]
    hot_region_sample_count: int
    hot_region_coverage_s: float
    hot_region_mean_residual_c: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_stage_b_acceptance(
    time_s: np.ndarray,
    measured_c: np.ndarray,
    predicted_c: np.ndarray,
    metrics: ValidationMetrics | None = None,
) -> StageBAcceptance:
    time_s = np.asarray(time_s, dtype=float)
    measured_c = np.asarray(measured_c, dtype=float)
    predicted_c = np.asarray(predicted_c, dtype=float)
    metrics = metrics or calculate_metrics(time_s, measured_c, predicted_c)

    rmse_pass = metrics.rmse_c <= 5.0
    mae_pass = metrics.mae_c <= 4.0
    bias_pass = abs(metrics.bias_c) <= 3.0
    p90_pass = metrics.p90_abs_error_c <= 7.0

    arrival_errors: dict[str, float | None] = {}
    missing: list[float] = []
    arrival_pass = True
    for threshold_c in (60.0, 80.0, 90.0):
        key = f"{threshold_c:g}C"
        if float(measured_c[0]) >= threshold_c:
            arrival_errors[key] = None
            continue
        measured_t = _first_crossing(time_s, measured_c, threshold_c)
        if measured_t is None:
            arrival_errors[key] = None
            continue
        predicted_t = _first_crossing(time_s, predicted_c, threshold_c)
        if predicted_t is None:
            arrival_errors[key] = None
            missing.append(threshold_c)
            arrival_pass = False
            continue
        error_s = float(predicted_t - measured_t)
        arrival_errors[key] = error_s
        if abs(error_s) > 60.0:
            arrival_pass = False

    hot_mask = (measured_c >= 96.0) & (measured_c <= 100.0)
    hot_indices = np.flatnonzero(hot_mask)
    hot_count = int(hot_indices.size)
    hot_coverage_s = (
        float(time_s[hot_indices[-1]] - time_s[hot_indices[0]])
        if hot_count >= 2
        else 0.0
    )
    hot_evaluable = hot_count >= 30 and hot_coverage_s >= 30.0
    if hot_evaluable:
        hot_mean_residual = float(np.mean(predicted_c[hot_mask] - measured_c[hot_mask]))
        hot_pass = abs(hot_mean_residual) <= 3.0
    else:
        hot_mean_residual = None
        hot_pass = True

    passed = bool(
        rmse_pass
        and mae_pass
        and bias_pass
        and p90_pass
        and arrival_pass
        and hot_pass
    )
    return StageBAcceptance(
        passed=passed,
        rmse_pass=rmse_pass,
        mae_pass=mae_pass,
        bias_pass=bias_pass,
        p90_pass=p90_pass,
        arrival_pass=arrival_pass,
        hot_region_pass=hot_pass,
        hot_region_evaluable=hot_evaluable,
        arrival_errors_s=arrival_errors,
        missing_predicted_crossings_c=tuple(missing),
        hot_region_sample_count=hot_count,
        hot_region_coverage_s=hot_coverage_s,
        hot_region_mean_residual_c=hot_mean_residual,
    )


@dataclass(frozen=True)
class StageBRunResult:
    case: StageBCase
    metrics: ValidationMetrics
    acceptance: StageBAcceptance
    predicted_c: np.ndarray


def run_stage_b_case_reference(
    dataset: ValidationDataset,
    case: StageBCase,
    *,
    initial_head_offset_c: float = 0.0,
    initial_block_offset_c: float = 0.0,
    initial_cold_offset_c: float = 0.0,
) -> StageBRunResult:
    dataset.validate()
    if dataset.fuel_rate_kg_s is None and dataset.fuel_energy_rate_w is None:
        raise ValueError("M2 Stage B requires direct fuel-rate or fuel-energy evidence")

    parameters = case.parameters()
    parameters.validate()
    reference_rpm = _project_engine_speed(dataset.engine_speed_rpm)
    if dataset.fuel_energy_rate_w is not None:
        fuel_energy_rate_w = np.asarray(dataset.fuel_energy_rate_w, dtype=float)
    else:
        assert dataset.fuel_rate_kg_s is not None
        fuel_energy_rate_w = np.asarray(dataset.fuel_rate_kg_s, dtype=float) * FUEL_LHV_J_PER_KG

    # A2 freezes this arithmetic order: form the wall-heat source samples first,
    # then interpolate that already-partitioned source inside Scenario.at().
    engine_heat_w = fuel_energy_rate_w * case.wall_heat_fraction
    initial_ect = float(dataset.measured_coolant_temp_c[0])
    scenario = Scenario(
        scenario_id=f"M2-STAGE-B-{case.global_index}",
        name="VTMS-V2 M2 Stage B independent development case",
        duration_s=dataset.duration_s,
        ambient_temp_c=_profile(dataset, dataset.ambient_temp_c),
        engine_speed_rpm=_profile(dataset, reference_rpm),
        effective_load=0.0,
        vehicle_speed_m_s=_profile(dataset, dataset.vehicle_speed_m_s),
        initial_engine_temp_c=initial_ect,
        initial_coolant_temp_c=initial_ect,
        engine_heat_override_w=_profile(dataset, engine_heat_w),
        faults=FaultState(),
        output_interval_s=1.0,
    )
    airflow = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN,
        hood_position="up",
        source_note=(
            "Argonne documented constant-speed external cooling fan; 2.50 m3/s is "
            "protocol capacity, not measured radiator-core flow."
        ),
    )
    simulation = M2SimulationRunner(parameters).run(
        scenario,
        airflow_boundary=airflow,
        initial_head_temp_c=initial_ect + initial_head_offset_c,
        initial_block_temp_c=initial_ect + initial_block_offset_c,
        initial_cold_temp_c=initial_ect + initial_cold_offset_c,
        rtol=1.0e-6,
        atol=1.0e-8,
        max_step_s=1.0,
    )
    sim_time = np.asarray([point.time_s for point in simulation.time_series], dtype=float)
    sim_ect = np.asarray([point.ect_predicted_c for point in simulation.time_series], dtype=float)
    predicted = np.interp(dataset.time_s, sim_time, sim_ect)
    measured = np.asarray(dataset.measured_coolant_temp_c, dtype=float)
    metrics = calculate_metrics(dataset.time_s, measured, predicted)
    acceptance = evaluate_stage_b_acceptance(dataset.time_s, measured, predicted, metrics)
    return StageBRunResult(
        case=case,
        metrics=metrics,
        acceptance=acceptance,
        predicted_c=predicted,
    )


HOT_HEAD_OFFSETS_C = (0.0, 15.0, 30.0)
HOT_BLOCK_OFFSETS_C = (0.0, 10.0, 20.0)
HOT_COLD_OFFSETS_C = (0.0, -5.0, -10.0)
HOT_INITIALIZATION_GRID = tuple(product(HOT_HEAD_OFFSETS_C, HOT_BLOCK_OFFSETS_C, HOT_COLD_OFFSETS_C))

if len(HOT_INITIALIZATION_GRID) != 27:
    raise RuntimeError("M2 hot-start initialization grid must contain exactly 27 cases")
