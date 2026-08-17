from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.dataset import ValidationDataset
from vtms_validation.identifiability import analyze_synthetic_identifiability
from vtms_validation.manifest import ALLOWED_CALIBRATION_PARAMETERS
from vtms_validation.synthetic import (
    _default_calibration_case,
    _default_holdout_case,
    generate_synthetic_dataset,
)


def _datasets() -> tuple[ValidationDataset, ValidationDataset]:
    parameters = ModelParameters()
    calibration, _ = generate_synthetic_dataset(_default_calibration_case(), parameters)
    holdout, _ = generate_synthetic_dataset(_default_holdout_case(), parameters)
    return calibration, holdout


def test_synthetic_identifiability_analyzes_exact_frozen_subset() -> None:
    calibration, _ = _datasets()
    diagnostics = analyze_synthetic_identifiability(calibration)

    assert diagnostics.parameter_names == tuple(ALLOWED_CALIBRATION_PARAMETERS)
    assert diagnostics.sample_count == len(calibration.time_s)
    assert diagnostics.sensitivity_matrix.shape == (
        len(calibration.time_s),
        len(ALLOWED_CALIBRATION_PARAMETERS),
    )
    assert diagnostics.numerical_rank <= len(ALLOWED_CALIBRATION_PARAMETERS)
    assert len(diagnostics.sensitivities) == len(ALLOWED_CALIBRATION_PARAMETERS)
    assert len(diagnostics.pairwise) == 6
    assert all(np.isfinite(diagnostics.sensitivity_matrix.ravel()))
    assert all(0.0 <= item.absolute_cosine_similarity <= 1.0 for item in diagnostics.pairwise)
    assert all(0.0 <= item.relative_rms_to_strongest <= 1.0 for item in diagnostics.sensitivities)


def test_combined_profiles_stack_without_using_measured_residuals() -> None:
    calibration, holdout = _datasets()
    diagnostics = analyze_synthetic_identifiability((calibration, holdout))

    assert diagnostics.dataset_ids == (calibration.dataset_id, holdout.dataset_id)
    assert diagnostics.sample_count == len(calibration.time_s) + len(holdout.time_s)
    assert diagnostics.sensitivity_matrix.shape[0] == diagnostics.sample_count
    assert "physical" in diagnostics.disclaimer.lower()
    assert "argonne" in diagnostics.disclaimer.lower()


def test_default_profiles_flag_weak_radiator_ua_excitation() -> None:
    calibration, holdout = _datasets()
    diagnostics = analyze_synthetic_identifiability((calibration, holdout))
    radiator = next(
        item for item in diagnostics.sensitivities if item.name == "radiator_ua_nominal_w_per_k"
    )

    assert radiator.relative_rms_to_strongest < 0.02
    assert diagnostics.assessment == "practical_identifiability_concern_detected"
    assert any(
        flag.startswith("weak_relative_sensitivity:radiator_ua_nominal_w_per_k:")
        for flag in diagnostics.diagnostic_flags
    )


def test_identifiability_is_deterministic() -> None:
    calibration, holdout = _datasets()
    first = analyze_synthetic_identifiability((calibration, holdout)).as_dict()
    second = analyze_synthetic_identifiability((calibration, holdout)).as_dict()
    assert first == second


def test_identifiability_refuses_physical_dataset() -> None:
    calibration, _ = _datasets()
    physical = replace(
        calibration,
        metadata={
            **calibration.metadata,
            "synthetic": False,
            "physical_validation_evidence": True,
        },
    )
    with pytest.raises(ValueError, match="synthetic-only"):
        analyze_synthetic_identifiability(physical)


def test_identifiability_refuses_parameter_subset_changes() -> None:
    calibration, _ = _datasets()
    with pytest.raises(ValueError, match="exactly the frozen calibration subset"):
        analyze_synthetic_identifiability(
            calibration,
            parameter_names=("wall_heat_fraction",),
        )


def test_identifiability_validates_relative_step() -> None:
    calibration, _ = _datasets()
    with pytest.raises(ValueError, match="relative_step"):
        analyze_synthetic_identifiability(calibration, relative_step=0.0)
