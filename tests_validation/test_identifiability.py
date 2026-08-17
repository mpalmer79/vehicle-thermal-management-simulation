import numpy as np

from vtms_validation.identifiability import (
    evaluate_synthetic_identifiability,
    evaluate_warmup_stage_identifiability,
)
from vtms_validation.manifest import ALLOWED_CALIBRATION_PARAMETERS


def test_synthetic_identifiability_returns_finite_structured_diagnostics():
    result = evaluate_synthetic_identifiability(perturbation_fraction=0.05)

    assert result.parameter_names == tuple(ALLOWED_CALIBRATION_PARAMETERS)
    assert len(result.sensitivities) == 4
    assert result.correlation_matrix.shape == (4, 4)
    assert result.singular_values.shape == (4,)
    assert np.all(np.isfinite(result.correlation_matrix))
    assert np.all(np.isfinite(result.singular_values))
    assert np.allclose(np.diag(result.correlation_matrix), 1.0)
    assert 0.0 <= result.max_abs_parameter_correlation <= 1.0 + 1.0e-12
    assert result.normalized_jacobian_condition_number > 0.0
    assert result.note


def test_synthetic_identifiability_is_deterministic():
    first = evaluate_synthetic_identifiability(perturbation_fraction=0.05)
    second = evaluate_synthetic_identifiability(perturbation_fraction=0.05)

    assert first.warning == second.warning
    assert np.allclose(first.correlation_matrix, second.correlation_matrix)
    assert np.allclose(first.singular_values, second.singular_values)
    assert first.normalized_jacobian_condition_number == second.normalized_jacobian_condition_number


def test_identifiability_rejects_unreasonable_perturbation():
    for value in (0.0, 0.5):
        try:
            evaluate_synthetic_identifiability(perturbation_fraction=value)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for invalid perturbation fraction")


def test_warmup_stage_diagnostic_blocks_four_parameter_cal_01():
    result = evaluate_warmup_stage_identifiability()

    assert result.parameter_names == tuple(ALLOWED_CALIBRATION_PARAMETERS)
    assert result.dataset_ids == ("SYN-CAL-01", "SYN-HOLD-01")
    assert result.numerical_rank == 4
    assert result.sample_count == 114
    assert result.weakest_parameter == "radiator_ua_nominal_w_per_k"
    assert result.weakest_relative_rms < 0.02
    assert "radiator_ua_nominal_w_per_k" in result.weak_parameter_names
    assert result.four_parameter_cal_01_authorized is False
    assert np.all(np.isfinite(result.singular_values))
    assert result.normalized_jacobian_condition_number > 0.0


def test_warmup_stage_diagnostic_is_deterministic():
    first = evaluate_warmup_stage_identifiability().as_dict()
    second = evaluate_warmup_stage_identifiability().as_dict()
    assert first == second
