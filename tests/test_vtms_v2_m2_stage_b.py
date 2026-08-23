import numpy as np

from vtms_validation.metrics import calculate_metrics
from vtms_v2.m2.stage_b import (
    GLOBAL_CASE_COUNT,
    case_from_global_index,
    evaluate_stage_b_acceptance,
)


def test_stage_b_global_index_decoder_is_stable() -> None:
    first = case_from_global_index(0)
    assert first.structural_index == 0
    assert first.control_index == 0
    assert first.head_thermal_capacitance_fraction == 0.15
    assert first.engine_coolant_ua_w_per_k == 400.0
    assert first.thermostat_full_c == 97.0
    assert first.gamma == 0.5

    end_of_first_structure = case_from_global_index(242)
    assert end_of_first_structure.structural_index == 0
    assert end_of_first_structure.control_index == 242
    assert end_of_first_structure.thermostat_full_c == 102.0
    assert end_of_first_structure.eta_pack == 0.80
    assert end_of_first_structure.radiator_ua_nominal_w_per_k == 2200.0
    assert end_of_first_structure.f_open == 1.0
    assert end_of_first_structure.gamma == 2.0

    next_structure = case_from_global_index(243)
    assert next_structure.structural_index == 1
    assert next_structure.control_index == 0
    assert next_structure.engine_coolant_ua_w_per_k == 1000.0

    audit_case = case_from_global_index(3248)
    assert audit_case.structural_index == 13
    assert audit_case.control_index == 89
    assert audit_case.head_thermal_capacitance_fraction == 0.15
    assert audit_case.head_heat_fraction == 0.50
    assert audit_case.head_block_ua_w_per_k == 100.0
    assert audit_case.hot_coolant_capacitance_fraction == 0.20
    assert audit_case.wall_heat_fraction == 0.35
    assert audit_case.engine_thermal_capacitance_j_per_k == 25000.0
    assert audit_case.engine_coolant_ua_w_per_k == 1000.0
    assert audit_case.thermostat_full_c == 99.5
    assert audit_case.eta_pack == 0.25
    assert audit_case.radiator_ua_nominal_w_per_k == 400.0
    assert audit_case.f_open == 1.0
    assert audit_case.gamma == 2.0

    adjacent_audit_case = case_from_global_index(3257)
    assert adjacent_audit_case.structural_index == 13
    assert adjacent_audit_case.control_index == 98
    assert adjacent_audit_case.head_thermal_capacitance_fraction == 0.15
    assert adjacent_audit_case.head_heat_fraction == 0.50
    assert adjacent_audit_case.head_block_ua_w_per_k == 100.0
    assert adjacent_audit_case.hot_coolant_capacitance_fraction == 0.20
    assert adjacent_audit_case.wall_heat_fraction == 0.35
    assert adjacent_audit_case.engine_thermal_capacitance_j_per_k == 25000.0
    assert adjacent_audit_case.engine_coolant_ua_w_per_k == 1000.0
    assert adjacent_audit_case.thermostat_full_c == 99.5
    assert adjacent_audit_case.eta_pack == 0.25
    assert adjacent_audit_case.radiator_ua_nominal_w_per_k == 1100.0
    assert adjacent_audit_case.f_open == 1.0
    assert adjacent_audit_case.gamma == 2.0

    last = case_from_global_index(GLOBAL_CASE_COUNT - 1)
    assert last.structural_index == 6479
    assert last.control_index == 242
    assert last.head_thermal_capacitance_fraction == 0.60
    assert last.head_heat_fraction == 0.95
    assert last.head_block_ua_w_per_k == 3000.0
    assert last.hot_coolant_capacitance_fraction == 0.80
    assert last.wall_heat_fraction == 0.50
    assert last.engine_thermal_capacitance_j_per_k == 100000.0
    assert last.engine_coolant_ua_w_per_k == 2200.0


def test_stage_b_missing_predicted_crossing_is_a_failure() -> None:
    time_s = np.arange(0.0, 101.0, 1.0)
    measured = 50.0 + 0.5 * time_s
    predicted = np.minimum(89.9, 50.0 + 0.45 * time_s)
    metrics = calculate_metrics(time_s, measured, predicted)

    acceptance = evaluate_stage_b_acceptance(time_s, measured, predicted, metrics)

    assert acceptance.arrival_pass is False
    assert 90.0 in acceptance.missing_predicted_crossings_c
    assert acceptance.passed is False


def test_stage_b_hot_region_is_not_applicable_without_measured_coverage() -> None:
    time_s = np.arange(0.0, 121.0, 1.0)
    measured = 25.0 + 0.5 * time_s
    predicted = measured.copy()
    metrics = calculate_metrics(time_s, measured, predicted)

    acceptance = evaluate_stage_b_acceptance(time_s, measured, predicted, metrics)

    assert acceptance.hot_region_evaluable is False
    assert acceptance.hot_region_pass is True
    assert acceptance.hot_region_mean_residual_c is None
    assert acceptance.passed is True


def test_stage_b_hot_region_bias_is_enforced_when_evaluable() -> None:
    time_s = np.arange(0.0, 121.0, 1.0)
    measured = np.full_like(time_s, 98.0)
    predicted = measured - 4.0
    metrics = calculate_metrics(time_s, measured, predicted)

    acceptance = evaluate_stage_b_acceptance(time_s, measured, predicted, metrics)

    assert acceptance.hot_region_evaluable is True
    assert acceptance.hot_region_mean_residual_c == -4.0
    assert acceptance.hot_region_pass is False
    assert acceptance.passed is False
