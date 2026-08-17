from __future__ import annotations

import numpy as np

from vtms_validation.acceptance import AcceptanceStatus, evaluate_acceptance
from vtms_validation.manifest import (
    ALLOWED_CALIBRATION_PARAMETERS,
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
)
from vtms_validation.metrics import calculate_metrics
from vtms_validation.runner import ComparisonResult


def _manifest(role: ValidationRole, *, physical_evidence: bool = True) -> ValidationRunManifest:
    grade = {
        ValidationRole.CALIBRATION: EvidenceGrade.CONTROLLED_CALIBRATION,
        ValidationRole.HOLDOUT: EvidenceGrade.INDEPENDENT_HOLDOUT,
        ValidationRole.CHALLENGE: EvidenceGrade.CHALLENGE_ONLY,
    }[role]
    return ValidationRunManifest(
        run_id=f"TEST-{role.value}",
        dataset_id="ACCEPTANCE-DATASET",
        role=role,
        evidence_grade=grade,
        dataset_fingerprint=DatasetFingerprint(
            file_name="acceptance.csv",
            sha256_hex="a" * 64,
            size_bytes=1,
        ),
        parameter_snapshot_sha256="b" * 64,
        calibration_parameters=(
            tuple(ALLOWED_CALIBRATION_PARAMETERS)
            if role is ValidationRole.CALIBRATION
            else ()
        ),
        physical_evidence=physical_evidence,
    )


def _comparison(predicted: np.ndarray) -> ComparisonResult:
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    metrics = calculate_metrics(time_s, measured, predicted)
    return ComparisonResult(
        dataset_id="ACCEPTANCE-DATASET",
        comparison_time_s=time_s,
        measured_coolant_temp_c=measured,
        predicted_coolant_temp_c=predicted,
        residual_c=predicted - measured,
        metrics=metrics,
        simulation_result=object(),
        heat_input_metadata={},
        evidence_label="test",
    )


def test_holdout_pass_is_formal_validation_pass():
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    evaluation = evaluate_acceptance(
        _comparison(measured + 2.0),
        _manifest(ValidationRole.HOLDOUT),
    )

    assert evaluation.overall_threshold_pass is True
    assert evaluation.formal_validation_pass is True
    assert evaluation.claim_label == "formal_holdout_acceptance_pass"
    assert all(
        check.status is AcceptanceStatus.PASS
        for check in evaluation.checks
        if check.status is not AcceptanceStatus.NOT_EVALUABLE
    )


def test_nonphysical_holdout_cannot_become_formal_validation_pass():
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    evaluation = evaluate_acceptance(
        _comparison(measured + 1.0),
        _manifest(ValidationRole.HOLDOUT, physical_evidence=False),
    )

    assert evaluation.overall_threshold_pass is True
    assert evaluation.formal_validation_pass is False
    assert evaluation.claim_label == "nonphysical_holdout_threshold_pass_not_validation"


def test_calibration_can_meet_thresholds_without_becoming_validation_pass():
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    evaluation = evaluate_acceptance(
        _comparison(measured + 1.0),
        _manifest(ValidationRole.CALIBRATION),
    )

    assert evaluation.overall_threshold_pass is True
    assert evaluation.formal_validation_pass is False
    assert evaluation.claim_label == "calibration_fit_within_project_thresholds"


def test_large_temperature_errors_fail_acceptance():
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    evaluation = evaluate_acceptance(
        _comparison(measured + 8.0),
        _manifest(ValidationRole.HOLDOUT),
    )

    assert evaluation.overall_threshold_pass is False
    assert evaluation.formal_validation_pass is False
    failed_ids = {check.check_id for check in evaluation.checks if check.status is AcceptanceStatus.FAIL}
    assert {"rmse", "mae", "abs_bias", "p90_abs_error"} <= failed_ids


def test_prediction_missing_a_measured_threshold_crossing_fails_that_timing_check():
    time_s = np.arange(0.0, 301.0, 10.0)
    measured = 20.0 + 0.30 * time_s
    predicted = np.minimum(measured, 85.0)
    evaluation = evaluate_acceptance(
        _comparison(predicted),
        _manifest(ValidationRole.HOLDOUT),
    )

    arrival_90 = next(check for check in evaluation.checks if check.check_id == "arrival_90c")
    assert arrival_90.status is AcceptanceStatus.FAIL
    assert "prediction did not" in arrival_90.note


def test_threshold_already_exceeded_at_start_is_not_evaluable():
    time_s = np.arange(0.0, 61.0, 10.0)
    measured = np.asarray([98.0, 97.0, 96.0, 95.0, 96.0, 97.0, 98.0])
    predicted = measured - 2.0
    metrics = calculate_metrics(time_s, measured, predicted)
    comparison = ComparisonResult(
        dataset_id="ACCEPTANCE-DATASET",
        comparison_time_s=time_s,
        measured_coolant_temp_c=measured,
        predicted_coolant_temp_c=predicted,
        residual_c=predicted - measured,
        metrics=metrics,
        simulation_result=object(),
        heat_input_metadata={},
        evidence_label="test",
    )

    assert metrics.threshold_arrival_error_s == {"60C": None, "80C": None, "90C": None}
    evaluation = evaluate_acceptance(comparison, _manifest(ValidationRole.HOLDOUT))
    timing = [check for check in evaluation.checks if check.check_id.startswith("arrival_")]
    assert all(check.status is AcceptanceStatus.NOT_EVALUABLE for check in timing)
    assert all("before the observation window" in check.note for check in timing)
