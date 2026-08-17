import numpy as np
import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.dataset import ValidationDataset
from vtms_validation.manifest import (
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from vtms_validation.runner import run_controlled_comparison


def _dataset(*, include_fuel_energy: bool = True) -> ValidationDataset:
    return ValidationDataset(
        dataset_id="ARGONNE-D3-HOLDOUT",
        source_name="synthetic controlled-run fixture",
        time_s=np.array([0.0, 1.0, 2.0]),
        measured_coolant_temp_c=np.array([20.0, 20.1, 20.2]),
        engine_speed_rpm=np.array([900.0, 900.0, 900.0]),
        vehicle_speed_m_s=np.array([0.0, 0.0, 0.0]),
        ambient_temp_c=np.array([20.0, 20.0, 20.0]),
        fuel_energy_rate_w=np.array([20000.0, 20000.0, 20000.0]) if include_fuel_energy else None,
        mass_air_flow_g_s=np.array([5.0, 5.0, 5.0]) if not include_fuel_energy else None,
        metadata={"source_sha256": "b" * 64},
    )


def _manifest(parameters: ModelParameters) -> ValidationRunManifest:
    return ValidationRunManifest(
        run_id="VAL-CS-01",
        dataset_id="ARGONNE-D3-HOLDOUT",
        role=ValidationRole.HOLDOUT,
        evidence_grade=EvidenceGrade.INDEPENDENT_HOLDOUT,
        dataset_fingerprint=DatasetFingerprint(
            file_name="holdout.csv",
            sha256_hex="b" * 64,
            size_bytes=500,
        ),
        parameter_snapshot_sha256=sha256_mapping(parameters.snapshot()),
    )


def test_controlled_holdout_executes_with_manifest_locked_direct_fuel_energy():
    parameters = ModelParameters()
    result = run_controlled_comparison(_dataset(), _manifest(parameters), parameters=parameters)
    assert result.evidence_label == "independent_holdout"
    assert result.metrics.n == 3
    assert result.validation_manifest is not None
    assert result.validation_manifest["role"] == "holdout"
    assert result.heat_input_metadata["maf_proxy_used"] is False


def test_controlled_runner_rejects_parameter_snapshot_mismatch():
    parameters = ModelParameters()
    changed = ModelParameters(wall_heat_fraction=0.30)
    with pytest.raises(ValueError, match="parameter.*snapshot"):
        run_controlled_comparison(_dataset(), _manifest(parameters), parameters=changed)


def test_controlled_runner_rejects_maf_proxy_as_formal_heat_evidence():
    parameters = ModelParameters()
    with pytest.raises(ValueError, match="MAF-derived heat"):
        run_controlled_comparison(
            _dataset(include_fuel_energy=False),
            _manifest(parameters),
            parameters=parameters,
        )


def test_controlled_runner_rejects_wrong_raw_file_hash():
    parameters = ModelParameters()
    dataset = _dataset()
    dataset.metadata["source_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="source SHA-256"):
        run_controlled_comparison(dataset, _manifest(parameters), parameters=parameters)


def test_controlled_runner_projects_measured_idle_rpm_only_at_model_boundary():
    parameters = ModelParameters()
    dataset = ValidationDataset(
        dataset_id="ARGONNE-D3-HOLDOUT",
        source_name="measured idle-rpm fixture",
        time_s=np.array([0.0, 1.0, 2.0]),
        measured_coolant_temp_c=np.array([20.0, 20.1, 20.2]),
        engine_speed_rpm=np.array([650.0, 900.0, 6600.0]),
        vehicle_speed_m_s=np.array([0.0, 0.0, 0.0]),
        ambient_temp_c=np.array([20.0, 20.0, 20.0]),
        fuel_energy_rate_w=np.array([20000.0, 20000.0, 20000.0]),
        metadata={"source_sha256": "b" * 64},
    )
    raw_rpm = dataset.engine_speed_rpm.copy()

    result = run_controlled_comparison(dataset, _manifest(parameters), parameters=parameters)

    np.testing.assert_allclose(dataset.engine_speed_rpm, raw_rpm)
    rpm_meta = result.input_preprocessing_metadata["engine_speed_rpm"]
    assert rpm_meta["projected_sample_count"] == 2
    assert rpm_meta["projected_low_sample_count"] == 1
    assert rpm_meta["projected_high_sample_count"] == 1
    assert rpm_meta["raw_dataset_values_preserved"] is True
    assert rpm_meta["engine_heat_uses_rpm_load_estimator"] is False
