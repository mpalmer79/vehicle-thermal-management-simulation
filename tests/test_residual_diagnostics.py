from __future__ import annotations

import math

import pytest

from vtms_validation.residual_diagnostics import analyze_residuals


def test_residual_sign_and_bias_fraction() -> None:
    report = analyze_residuals(
        measured_coolant_temp_c=[80.0, 90.0, 100.0],
        predicted_coolant_temp_c=[75.0, 85.0, 95.0],
    )

    assert report.count == 3
    assert report.mean_residual_c == pytest.approx(-5.0)
    assert report.mae_c == pytest.approx(5.0)
    assert report.rmse_c == pytest.approx(5.0)
    assert report.max_abs_residual_c == pytest.approx(5.0)
    assert report.bias_fraction_of_mse == pytest.approx(1.0)
    assert report.negative_fraction == pytest.approx(1.0)
    assert report.positive_fraction == pytest.approx(0.0)


def test_temperature_bins_and_transition_window() -> None:
    report = analyze_residuals(
        measured_coolant_temp_c=[70.0, 87.0, 90.0, 96.0, 101.0],
        predicted_coolant_temp_c=[70.0, 86.0, 88.0, 93.0, 97.0],
        thermostat_open_c=88.0,
        thermostat_full_c=98.0,
        thermostat_transition_half_width_c=2.0,
    )

    bins = report.temperature_bins
    assert sum(item.count for item in bins) == 5
    assert bins[1].count == 1
    assert bins[2].count == 1
    assert bins[3].count == 2
    assert bins[4].count == 1

    transition = report.thermostat_transition
    assert transition.count == 3
    assert transition.mean_residual_c == pytest.approx(-2.0)
    assert transition.mae_c == pytest.approx(2.0)
    assert transition.rmse_c == pytest.approx(math.sqrt(14.0 / 3.0))


def test_correlations_are_reported_for_available_inputs() -> None:
    report = analyze_residuals(
        measured_coolant_temp_c=[80.0, 85.0, 90.0, 95.0],
        predicted_coolant_temp_c=[79.0, 83.0, 87.0, 91.0],
        engine_speed_rpm=[1000.0, 1500.0, 2000.0, 2500.0],
        vehicle_speed_m_s=[0.0, 10.0, 20.0, 30.0],
        fuel_energy_rate_w=[20_000.0, 30_000.0, 40_000.0, 50_000.0],
    )

    correlations = {item.name: item.pearson_r for item in report.correlations}
    assert set(correlations) == {
        "measured_coolant_temp_c",
        "engine_speed_rpm",
        "vehicle_speed_m_s",
        "fuel_energy_rate_w",
    }
    assert correlations["engine_speed_rpm"] == pytest.approx(-1.0)
    assert correlations["vehicle_speed_m_s"] == pytest.approx(-1.0)
    assert correlations["fuel_energy_rate_w"] == pytest.approx(-1.0)


def test_constant_independent_variable_has_no_correlation() -> None:
    report = analyze_residuals(
        measured_coolant_temp_c=[80.0, 90.0, 100.0],
        predicted_coolant_temp_c=[79.0, 88.0, 97.0],
        engine_speed_rpm=[1500.0, 1500.0, 1500.0],
    )

    correlations = {item.name: item.pearson_r for item in report.correlations}
    assert correlations["engine_speed_rpm"] is None


def test_rejects_misaligned_inputs() -> None:
    with pytest.raises(ValueError, match="shape"):
        analyze_residuals(
            measured_coolant_temp_c=[80.0, 90.0],
            predicted_coolant_temp_c=[80.0],
        )
