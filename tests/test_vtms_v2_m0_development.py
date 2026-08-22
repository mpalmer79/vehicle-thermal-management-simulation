from __future__ import annotations

import numpy as np
import pytest

from vtms_validation.dataset import ValidationDataset
from vtms_validation.metrics import ValidationMetrics
from vtms_v2.m0.config import M0Parameters
from vtms_v2.m0.development import (
    M0DevelopmentComparison,
    M0FeasibilityGridPoint,
    M0HotRegionResult,
    constant_external_fan_boundary,
    evaluate_hot_region,
    feasibility_grid_points,
    run_m0_development_comparison,
    summarize_feasibility,
    whole_trace_pass,
)


def _metrics(*, rmse: float = 1.0, bias: float = 0.0) -> ValidationMetrics:
    return ValidationMetrics(
        n=100,
        rmse_c=rmse,
        mae_c=1.0,
        bias_c=bias,
        max_abs_error_c=2.0,
        p90_abs_error_c=2.0,
        final_error_c=0.5,
        measured_final_c=95.0,
        predicted_final_c=95.5,
        threshold_arrival_error_s={"60C": 5.0, "80C": -5.0, "90C": 10.0},
    )


def test_hot_region_requires_samples_and_time_coverage() -> None:
    time_s = np.arange(0.0, 41.0, 1.0)
    measured = np.full_like(time_s, 97.0)
    predicted = measured + 2.0
    result = evaluate_hot_region(time_s, measured, predicted)
    assert result.evaluable is True
    assert result.sample_count == 41
    assert result.total_time_coverage_s == pytest.approx(40.0)
    assert result.mean_residual_c == pytest.approx(2.0)
    assert result.passed is True

    short = evaluate_hot_region(
        np.arange(0.0, 20.0, 1.0),
        np.full(20, 97.0),
        np.full(20, 98.0),
    )
    assert short.evaluable is False
    assert short.passed is None


def test_hot_region_can_fail_independently_of_whole_trace() -> None:
    time_s = np.arange(0.0, 41.0, 1.0)
    measured = np.full_like(time_s, 98.0)
    predicted = measured - 4.0
    result = evaluate_hot_region(time_s, measured, predicted)
    assert result.evaluable is True
    assert result.absolute_mean_residual_c == pytest.approx(4.0)
    assert result.passed is False


def test_whole_trace_thresholds_are_frozen() -> None:
    assert whole_trace_pass(_metrics()) is True
    assert whole_trace_pass(_metrics(rmse=5.01)) is False
    assert whole_trace_pass(_metrics(bias=-3.01)) is False


def test_feasibility_plan_grid_contains_810_points() -> None:
    grid = feasibility_grid_points(
        {
            "thermostat_full_c": [97.0, 99.5, 102.0],
            "eta_pack": [0.10, 0.25, 0.40, 0.60, 0.80, 1.00],
            "radiator_ua_nominal_w_per_k": [400.0, 700.0, 1100.0, 1600.0, 2200.0],
            "f_open": [0.85, 0.925, 1.00],
            "gamma": [0.50, 1.00, 2.00],
        }
    )
    assert len(grid) == 810
    assert grid[0] == M0FeasibilityGridPoint(97.0, 0.10, 400.0, 0.85, 0.50)


def test_feasibility_summary_reports_ranges_without_ranking() -> None:
    points = (
        M0FeasibilityGridPoint(97.0, 0.1, 400.0, 0.85, 0.5),
        M0FeasibilityGridPoint(99.5, 0.4, 1100.0, 0.925, 1.0),
    )
    pass_hot = M0HotRegionResult(True, 100, 50.0, 1.0, 1.0, True)
    fail_hot = M0HotRegionResult(True, 100, 50.0, 4.0, 4.0, False)
    results = (
        {
            "cold": M0DevelopmentComparison("cold", _metrics(), pass_hot, True, True),
            "hot": M0DevelopmentComparison("hot", _metrics(), pass_hot, True, True),
        },
        {
            "cold": M0DevelopmentComparison("cold", _metrics(), pass_hot, True, True),
            "hot": M0DevelopmentComparison("hot", _metrics(), fail_hot, True, False),
        },
    )
    summary = summarize_feasibility(points=points, results=results)
    assert summary.joint_feasible_count == 1
    assert summary.joint_feasible_fraction == pytest.approx(0.5)
    assert summary.feasible_parameter_ranges["thermostat_full_c"] == {
        "min": 97.0,
        "max": 97.0,
    }
    assert summary.per_test_pass_counts == {"cold": 2, "hot": 1}
    assert summary.failure_mode_counts["hot_region_failure"] == 1


def test_m0_development_comparison_runs_on_synthetic_equilibrium() -> None:
    time_s = np.arange(0.0, 61.0, 1.0)
    dataset = ValidationDataset(
        dataset_id="SYN-M0-DEV-EQUILIBRIUM",
        source_name="synthetic test",
        time_s=time_s,
        measured_coolant_temp_c=np.full_like(time_s, 25.0),
        engine_speed_rpm=np.full_like(time_s, 1000.0),
        vehicle_speed_m_s=np.zeros_like(time_s),
        ambient_temp_c=np.full_like(time_s, 25.0),
        fuel_rate_kg_s=np.zeros_like(time_s),
    )
    comparison = run_m0_development_comparison(
        dataset,
        parameters=M0Parameters(),
        airflow_boundary=constant_external_fan_boundary(),
        fuel_lhv_j_per_kg=42_668_144.0,
    )
    assert comparison.whole_trace_pass is True
    assert comparison.overall_pass is True
    assert comparison.metrics.rmse_c == pytest.approx(0.0, abs=1.0e-10)
    assert comparison.hot_region.evaluable is False
