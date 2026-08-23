from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from itertools import product
from typing import Iterable

import numpy as np

from vtms_v1.scenario import Scenario
from vtms_validation.dataset import ValidationDataset
from vtms_validation.metrics import ValidationMetrics, calculate_metrics

from .airflow import AirflowBoundary, AirflowBoundaryClass
from .config import M0Parameters
from .simulation import M0SimulationRunner

_REFERENCE_MIN_NONZERO_RPM = 700.0
_REFERENCE_MAX_RPM = 6500.0


@dataclass(frozen=True)
class M0HotRegionResult:
    evaluable: bool
    sample_count: int
    total_time_coverage_s: float
    mean_residual_c: float | None
    absolute_mean_residual_c: float | None
    passed: bool | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class M0DevelopmentComparison:
    dataset_id: str
    metrics: ValidationMetrics
    hot_region: M0HotRegionResult
    whole_trace_pass: bool
    overall_pass: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "metrics": self.metrics.as_dict(),
            "hot_region": self.hot_region.as_dict(),
            "whole_trace_pass": self.whole_trace_pass,
            "overall_pass": self.overall_pass,
        }


@dataclass(frozen=True)
class M0FeasibilityGridPoint:
    thermostat_full_c: float
    eta_pack: float
    radiator_ua_nominal_w_per_k: float
    f_open: float
    gamma: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class M0FeasibilitySummary:
    grid_size: int
    evaluated_grid_points: int
    joint_feasible_count: int
    joint_feasible_fraction: float
    feasible_parameter_ranges: dict[str, dict[str, float] | None]
    per_test_pass_counts: dict[str, int]
    failure_mode_counts: dict[str, int]
    interpretation: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _profile(dataset: ValidationDataset, values: np.ndarray):
    return lambda time_s: dataset.interp(values, time_s)


def _project_engine_speed(engine_speed_rpm: np.ndarray) -> np.ndarray:
    projected = np.asarray(engine_speed_rpm, dtype=float).copy()
    low = (projected > 0.0) & (projected < _REFERENCE_MIN_NONZERO_RPM)
    high = projected > _REFERENCE_MAX_RPM
    projected[low] = _REFERENCE_MIN_NONZERO_RPM
    projected[high] = _REFERENCE_MAX_RPM
    return projected


def _total_mask_time_s(time_s: np.ndarray, mask: np.ndarray) -> float:
    if len(time_s) < 2:
        return 0.0
    dt = np.diff(time_s)
    active = mask[:-1] & mask[1:]
    return float(np.sum(dt[active]))


def evaluate_hot_region(
    time_s: np.ndarray,
    measured_c: np.ndarray,
    predicted_c: np.ndarray,
    *,
    lower_c: float = 96.0,
    upper_c: float = 100.0,
    abs_mean_residual_limit_c: float = 3.0,
    minimum_samples: int = 30,
    minimum_time_coverage_s: float = 30.0,
) -> M0HotRegionResult:
    mask = (measured_c >= lower_c) & (measured_c <= upper_c)
    sample_count = int(np.count_nonzero(mask))
    coverage = _total_mask_time_s(time_s, mask)
    evaluable = bool(
        sample_count >= minimum_samples
        and coverage >= minimum_time_coverage_s
    )
    if not evaluable:
        return M0HotRegionResult(
            evaluable=False,
            sample_count=sample_count,
            total_time_coverage_s=coverage,
            mean_residual_c=None,
            absolute_mean_residual_c=None,
            passed=None,
        )

    residual = predicted_c[mask] - measured_c[mask]
    mean_residual = float(np.mean(residual))
    absolute_mean = abs(mean_residual)
    return M0HotRegionResult(
        evaluable=True,
        sample_count=sample_count,
        total_time_coverage_s=coverage,
        mean_residual_c=mean_residual,
        absolute_mean_residual_c=absolute_mean,
        passed=bool(absolute_mean <= abs_mean_residual_limit_c),
    )


def whole_trace_pass(metrics: ValidationMetrics) -> bool:
    arrival_ok = all(
        value is None or abs(float(value)) <= 60.0
        for value in metrics.threshold_arrival_error_s.values()
    )
    return bool(
        metrics.rmse_c <= 5.0
        and metrics.mae_c <= 4.0
        and abs(metrics.bias_c) <= 3.0
        and metrics.p90_abs_error_c <= 7.0
        and arrival_ok
    )


def run_m0_development_comparison(
    dataset: ValidationDataset,
    *,
    parameters: M0Parameters,
    airflow_boundary: AirflowBoundary,
    fuel_lhv_j_per_kg: float,
) -> M0DevelopmentComparison:
    dataset.validate()
    parameters.validate()
    airflow_boundary.validate()
    if dataset.fuel_rate_kg_s is None:
        raise ValueError("M0 development comparison requires direct fuel rate")
    if fuel_lhv_j_per_kg <= 0.0:
        raise ValueError("fuel_lhv_j_per_kg must be > 0")

    q_engine = (
        np.asarray(dataset.fuel_rate_kg_s, dtype=float)
        * fuel_lhv_j_per_kg
        * parameters.wall_heat_fraction
    )
    projected_rpm = _project_engine_speed(dataset.engine_speed_rpm)
    scenario = Scenario(
        scenario_id=f"M0-DEV-{dataset.dataset_id}",
        name="VTMS-V2 M0 consumed development comparison",
        duration_s=dataset.duration_s,
        ambient_temp_c=_profile(dataset, dataset.ambient_temp_c),
        engine_speed_rpm=_profile(dataset, projected_rpm),
        effective_load=0.0,
        vehicle_speed_m_s=_profile(dataset, dataset.vehicle_speed_m_s),
        initial_engine_temp_c=float(dataset.measured_coolant_temp_c[0]),
        initial_coolant_temp_c=float(dataset.measured_coolant_temp_c[0]),
        engine_heat_override_w=_profile(dataset, q_engine),
        output_interval_s=1.0,
    )
    result = M0SimulationRunner(parameters).run(
        scenario,
        airflow_boundary=airflow_boundary,
    )
    sim_t = np.asarray([point.time_s for point in result.time_series], dtype=float)
    sim_c = np.asarray([point.coolant_temp_c for point in result.time_series], dtype=float)
    predicted = np.interp(dataset.time_s, sim_t, sim_c)
    measured = np.asarray(dataset.measured_coolant_temp_c, dtype=float)
    metrics = calculate_metrics(dataset.time_s, measured, predicted)
    hot = evaluate_hot_region(dataset.time_s, measured, predicted)
    trace_pass = whole_trace_pass(metrics)
    overall = bool(trace_pass and (hot.passed is not False))
    return M0DevelopmentComparison(
        dataset_id=dataset.dataset_id,
        metrics=metrics,
        hot_region=hot,
        whole_trace_pass=trace_pass,
        overall_pass=overall,
    )


def feasibility_grid_points(
    design_grid: dict[str, Iterable[float]],
) -> tuple[M0FeasibilityGridPoint, ...]:
    required = (
        "thermostat_full_c",
        "eta_pack",
        "radiator_ua_nominal_w_per_k",
        "f_open",
        "gamma",
    )
    missing = [name for name in required if name not in design_grid]
    if missing:
        raise ValueError(f"feasibility design grid missing keys: {missing}")
    return tuple(
        M0FeasibilityGridPoint(*map(float, values))
        for values in product(*(design_grid[name] for name in required))
    )


def summarize_feasibility(
    *,
    points: Iterable[M0FeasibilityGridPoint],
    results: Iterable[dict[str, M0DevelopmentComparison]],
) -> M0FeasibilitySummary:
    point_list = tuple(points)
    result_list = tuple(results)
    if len(point_list) != len(result_list):
        raise ValueError("points and results must have equal length")

    feasible_indices = [
        index
        for index, per_test in enumerate(result_list)
        if per_test and all(item.overall_pass for item in per_test.values())
    ]
    test_ids = sorted({key for result in result_list for key in result})
    pass_counts = {
        test_id: sum(
            1
            for result in result_list
            if test_id in result and result[test_id].overall_pass
        )
        for test_id in test_ids
    }

    failure_counts = {
        "whole_trace_failure": 0,
        "hot_region_failure": 0,
        "hot_region_non_evaluable": 0,
    }
    for per_test in result_list:
        for item in per_test.values():
            if not item.whole_trace_pass:
                failure_counts["whole_trace_failure"] += 1
            if item.hot_region.evaluable and item.hot_region.passed is False:
                failure_counts["hot_region_failure"] += 1
            if not item.hot_region.evaluable:
                failure_counts["hot_region_non_evaluable"] += 1

    parameter_names = tuple(M0FeasibilityGridPoint.__dataclass_fields__)
    ranges: dict[str, dict[str, float] | None] = {}
    for name in parameter_names:
        values = [
            float(getattr(point_list[index], name))
            for index in feasible_indices
        ]
        ranges[name] = (
            {"min": min(values), "max": max(values)} if values else None
        )

    feasible_count = len(feasible_indices)
    evaluated = len(result_list)
    interpretation = (
        "one_or_more_joint_feasible_grid_points_m0_remains_viable_without_parameter_identification"
        if feasible_count
        else "zero_joint_feasible_grid_points_under_frozen_feasibility_plan"
    )
    return M0FeasibilitySummary(
        grid_size=len(point_list),
        evaluated_grid_points=evaluated,
        joint_feasible_count=feasible_count,
        joint_feasible_fraction=(
            float(feasible_count / evaluated) if evaluated else 0.0
        ),
        feasible_parameter_ranges=ranges,
        per_test_pass_counts=pass_counts,
        failure_mode_counts=failure_counts,
        interpretation=interpretation,
    )


def parameters_for_grid_point(
    base_parameters: M0Parameters,
    point: M0FeasibilityGridPoint,
) -> M0Parameters:
    parameters = replace(
        base_parameters,
        thermostat_full_c=point.thermostat_full_c,
        eta_pack=point.eta_pack,
        radiator_ua_nominal_w_per_k=point.radiator_ua_nominal_w_per_k,
        f_open=point.f_open,
        gamma=point.gamma,
    )
    parameters.validate()
    return parameters


def constant_external_fan_boundary(
    *,
    capacity_m3_s: float = 2.50,
) -> AirflowBoundary:
    return AirflowBoundary(
        boundary_class=AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN,
        external_fan_vol_flow_m3_s=capacity_m3_s,
        hood_position="up",
        source_note="FEAS-01 frozen constant external fan development boundary",
    )
