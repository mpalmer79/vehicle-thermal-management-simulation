from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

import numpy as np
import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneSignalMap
from vtms_validation.dataset import ValidationDataset
from vtms_validation.manifest import (
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from vtms_validation.runner import run_controlled_comparison


ROOT = Path(__file__).resolve().parents[1]
CALRAD_RESULT = ROOT / "validation_outputs" / "ARGONNE_CAL_RAD_01_FORMAL_RESULT.json"
HOLDOUT_LOCK = ROOT / "validation_configs" / "argonne_2012_focus_val_hot_01_manifest.json"


def _parameters_from_final_staged_result(payload: dict[str, object]) -> ModelParameters:
    snapshot = dict(payload["calibrated_model_parameters"])
    allowed = {item.name for item in fields(ModelParameters)}
    parameters = replace(
        ModelParameters(),
        **{name: float(value) for name, value in snapshot.items() if name in allowed},
    )
    parameters.validate()
    return parameters


def test_calrad_failure_and_lower_bound_are_frozen_not_hidden():
    result = json.loads(CALRAD_RESULT.read_text(encoding="utf-8"))
    assert result["acceptance_after_pre_holdout_protocol_clarification"]["overall_threshold_pass"] is False
    assert result["acceptance_after_pre_holdout_protocol_clarification"]["formal_validation_pass"] is False
    assert result["boundary_parameter_names"] == ["radiator_ua_nominal_w_per_k"]
    assert result["parameters"][0]["normalized_bound_fraction"] < 0.01
    assert result["interpretation"]["holdouts_opened"] is False


def test_primary_holdout_lock_uses_final_staged_snapshot_and_forbids_fitting():
    result = json.loads(CALRAD_RESULT.read_text(encoding="utf-8"))
    lock = json.loads(HOLDOUT_LOCK.read_text(encoding="utf-8"))
    parameters = _parameters_from_final_staged_result(result)

    assert sha256_mapping(parameters.snapshot()) == result["calibrated_parameter_snapshot_sha256"]
    assert sha256_mapping(parameters.snapshot()) == lock["manifest"]["parameter_snapshot_sha256"]
    assert lock["manifest"]["role"] == "holdout"
    assert lock["manifest"]["evidence_grade"] == "independent_holdout"
    assert lock["manifest"]["calibration_parameters"] == []
    assert lock["manifest"]["physical_evidence"] is True


def test_primary_holdout_mapping_and_source_identity_are_locked_before_execution():
    lock = json.loads(HOLDOUT_LOCK.read_text(encoding="utf-8"))
    execution = lock["execution"]
    manifest = lock["manifest"]
    signal_map = ArgonneSignalMap.from_json(ROOT / execution["signal_map_file"])

    assert sha256_mapping(signal_map.snapshot()) == manifest["preprocessing_snapshot_sha256"]
    assert manifest["dataset_fingerprint"] == {
        "file_name": "71207063 Test Data.txt",
        "sha256_hex": "8a1953112752e35ade720ab9a64201b05b37c70d172839234f12504e68f2aa8d",
        "size_bytes": 5112305,
    }


def test_controlled_comparison_rejects_preprocessing_drift_before_simulation():
    parameters = ModelParameters()
    dataset = ValidationDataset(
        dataset_id="LOCKED-HOLDOUT",
        source_name="test fixture",
        time_s=np.asarray([0.0, 1.0]),
        measured_coolant_temp_c=np.asarray([20.0, 20.1]),
        engine_speed_rpm=np.asarray([1000.0, 1000.0]),
        vehicle_speed_m_s=np.asarray([0.0, 0.0]),
        ambient_temp_c=np.asarray([20.0, 20.0]),
        fuel_energy_rate_w=np.asarray([10000.0, 10000.0]),
        metadata={"source_sha256": "a" * 64, "signal_map_sha256": "b" * 64},
    )
    manifest = ValidationRunManifest(
        run_id="VAL-LOCK",
        dataset_id="LOCKED-HOLDOUT",
        role=ValidationRole.HOLDOUT,
        evidence_grade=EvidenceGrade.INDEPENDENT_HOLDOUT,
        dataset_fingerprint=DatasetFingerprint(
            file_name="holdout.txt",
            sha256_hex="a" * 64,
            size_bytes=1,
        ),
        parameter_snapshot_sha256=sha256_mapping(parameters.snapshot()),
        preprocessing_snapshot_sha256="c" * 64,
        physical_evidence=True,
    )

    with pytest.raises(ValueError, match="preprocessing snapshot"):
        run_controlled_comparison(dataset, manifest, parameters=parameters)
