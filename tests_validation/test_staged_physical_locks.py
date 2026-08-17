from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneSignalMap
from vtms_validation.manifest import sha256_mapping
from vtms_validation.physical_bounds import (
    CAL_RAD_01_PARAMETER_NAMES,
    argonne_cal_rad_01_bounds,
)


ROOT = Path(__file__).resolve().parents[1]
CAL01_RESULT = ROOT / "validation_outputs" / "ARGONNE_CAL_01_FORMAL_RESULT.json"
CALRAD_LOCK = ROOT / "validation_configs" / "argonne_2012_focus_cal_rad_01_manifest.json"


def _parameters_from_cal01_result(payload: dict[str, object]) -> ModelParameters:
    snapshot = dict(payload["calibrated_model_parameters"])
    allowed = {item.name for item in fields(ModelParameters)}
    parameters = replace(
        ModelParameters(),
        **{name: float(value) for name, value in snapshot.items() if name in allowed},
    )
    parameters.validate()
    return parameters


def test_cal01_formal_result_is_calibration_only_and_preserves_boundary_warning():
    result = json.loads(CAL01_RESULT.read_text(encoding="utf-8"))
    assert result["acceptance"]["overall_threshold_pass"] is True
    assert result["acceptance"]["formal_validation_pass"] is False
    assert result["execution_identity"]["formal_validation_claim"] is False
    assert result["interpretation"]["holdouts_opened"] is False
    assert result["boundary_parameter_names"] == [
        "wall_heat_fraction",
        "engine_coolant_ua_w_per_k",
    ]


def test_calrad_lock_uses_exact_frozen_cal01_snapshot():
    result = json.loads(CAL01_RESULT.read_text(encoding="utf-8"))
    lock = json.loads(CALRAD_LOCK.read_text(encoding="utf-8"))
    parameters = _parameters_from_cal01_result(result)

    assert sha256_mapping(parameters.snapshot()) == result["calibrated_parameter_snapshot_sha256"]
    assert sha256_mapping(parameters.snapshot()) == lock["manifest"]["parameter_snapshot_sha256"]


def test_calrad_lock_matches_pre_registered_source_map_and_radiator_only_bounds():
    lock = json.loads(CALRAD_LOCK.read_text(encoding="utf-8"))
    execution = lock["execution"]
    manifest = lock["manifest"]

    signal_map = ArgonneSignalMap.from_json(ROOT / execution["signal_map_file"])
    assert sha256_mapping(signal_map.snapshot()) == manifest["preprocessing_snapshot_sha256"]

    bounds = argonne_cal_rad_01_bounds()
    assert sha256_mapping(bounds.as_dict()) == manifest["calibration_bounds_sha256"]
    assert tuple(manifest["calibration_parameters"]) == CAL_RAD_01_PARAMETER_NAMES
    assert tuple(manifest["calibration_parameters"]) == ("radiator_ua_nominal_w_per_k",)


def test_calrad_source_fingerprint_is_the_pre_registered_71207057_file():
    lock = json.loads(CALRAD_LOCK.read_text(encoding="utf-8"))
    fingerprint = lock["manifest"]["dataset_fingerprint"]
    assert fingerprint["file_name"] == "71207057 Test Data.txt"
    assert fingerprint["sha256_hex"] == "57034f3e01e45bae7271cc4f96d3b7eb88055e17bb1bf3522e28c6734b631e3d"
    assert fingerprint["size_bytes"] == 3768884
