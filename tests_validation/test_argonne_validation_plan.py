from __future__ import annotations

import json
from pathlib import Path


PLAN_PATH = Path("validation_configs/argonne_validation_plan.json")


def _plan() -> dict[str, object]:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def _run_by_id(plan: dict[str, object], run_id: str) -> dict[str, object]:
    runs = plan["runs"]
    assert isinstance(runs, list)
    return next(run for run in runs if run["run_id"] == run_id)


def test_argonne_calibration_plan_is_staged_before_physical_fit() -> None:
    plan = _plan()
    cal_01 = _run_by_id(plan, "CAL-01")
    cal_rad = _run_by_id(plan, "CAL-RAD-01")

    assert plan["calibration_bounds_status"] == "frozen_before_argonne_residual_inspection"
    assert cal_01["source_test_id"] == "71207062"
    assert cal_01["calibration_parameters"] == [
        "wall_heat_fraction",
        "engine_thermal_capacitance_j_per_k",
        "engine_coolant_ua_w_per_k",
    ]
    assert cal_01["excluded_from_this_fit"] == ["radiator_ua_nominal_w_per_k"]

    assert cal_rad["source_test_id"] == "71207057"
    assert cal_rad["calibration_parameters"] == ["radiator_ua_nominal_w_per_k"]
    assert "frozen output parameter snapshot from CAL-01" in cal_rad["upstream_parameter_policy"]


def test_reserved_holdouts_cannot_declare_calibration_parameters() -> None:
    plan = _plan()
    for run_id, expected_test_id in (
        ("VAL-HOT-01", "71207063"),
        ("VAL-SSS-01", "71207052"),
    ):
        run = _run_by_id(plan, run_id)
        assert run["role"] == "holdout"
        assert run["source_test_id"] == expected_test_id
        assert run["calibration_parameters"] == []


def test_argonne_role_selection_audit_prohibits_residual_contamination() -> None:
    plan = _plan()
    audit = plan["selection_audit"]
    assert audit["model_predictions_run_during_source_qc_or_role_selection"] is False
    assert audit["model_residuals_inspected_during_source_qc_or_role_selection"] is False
    assert audit["pre_fit_sensitivity_used_physical_argonne_data"] is False
    assert audit["physical_bounds_frozen_before_argonne_residual_inspection"] is True
    assert audit["existing_holdout_roles_preserved"] is True


def test_radiator_candidate_mapping_records_source_only_operating_basis() -> None:
    mapping_path = Path(
        "validation_configs/argonne_2012_focus_71207057_radiator_calibration.json"
    )
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    metadata = mapping["metadata"]
    review = metadata["source_operating_condition_review"]

    assert mapping["dataset_id"] == "ARGONNE-D3-71207057"
    assert metadata["authorized_parameter_candidate"] == "radiator_ua_nominal_w_per_k"
    assert metadata["source_file_sha256_expected"] == (
        "57034f3e01e45bae7271cc4f96d3b7eb88055e17bb1bf3522e28c6734b631e3d"
    )
    assert review["ect_min_c"] >= 88.0
    assert review["fraction_samples_at_or_above_40_mph"] > 0.9
    assert "No VTMS prediction or residual was inspected" in metadata["selection_basis"]
