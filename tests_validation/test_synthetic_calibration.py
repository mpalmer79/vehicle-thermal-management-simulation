from __future__ import annotations

from vtms_validation.synthetic import run_synthetic_bounded_calibration_harness


def test_synthetic_bounded_calibration_and_holdout_pipeline():
    result = run_synthetic_bounded_calibration_harness(max_nfev=80)

    assert result.calibration.success is True
    assert result.calibration.final_cost < result.calibration.initial_cost
    assert result.calibration.calibrated_parameter_snapshot_sha256 != (
        result.calibration.initial_parameter_snapshot_sha256
    )

    bounds = result.synthetic_bounds.as_dict()
    for fitted in result.calibration.parameters:
        assert bounds[fitted.name]["lower"] <= fitted.fitted <= bounds[fitted.name]["upper"]

    assert result.holdout_acceptance.overall_threshold_pass is True
    assert result.holdout_acceptance.formal_validation_pass is True
    assert "not physical validation" in result.disclaimer.lower()
    assert "must not be reused for argonne" in result.disclaimer.lower()
