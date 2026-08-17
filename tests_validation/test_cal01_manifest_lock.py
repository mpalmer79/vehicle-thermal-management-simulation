from __future__ import annotations

import json
from pathlib import Path

import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneSignalMap
from vtms_validation.manifest import (
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from vtms_validation.physical_bounds import (
    CAL_01_PARAMETER_NAMES,
    argonne_cal_01_bounds,
)
from vtms_validation.synthetic import run_synthetic_bounded_calibration_harness


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "validation_configs" / "argonne_2012_focus_cal_01_manifest.json"


def test_physical_calibration_manifest_requires_preprocessing_and_bound_hashes():
    fingerprint = DatasetFingerprint(
        file_name="physical.txt",
        sha256_hex="a" * 64,
        size_bytes=1,
    )
    with pytest.raises(ValueError, match="preprocessing_snapshot_sha256"):
        ValidationRunManifest(
            run_id="CAL-X",
            dataset_id="PHYSICAL-X",
            role=ValidationRole.CALIBRATION,
            evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
            dataset_fingerprint=fingerprint,
            parameter_snapshot_sha256="b" * 64,
            calibration_parameters=("wall_heat_fraction",),
            physical_evidence=True,
        ).validate()


def test_cal01_lock_matches_frozen_mapping_baseline_and_stage_bounds():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    manifest = lock["manifest"]
    execution = lock["execution"]

    signal_map = ArgonneSignalMap.from_json(ROOT / execution["signal_map_file"])
    assert sha256_mapping(signal_map.snapshot()) == manifest["preprocessing_snapshot_sha256"]

    assert sha256_mapping(ModelParameters().snapshot()) == manifest["parameter_snapshot_sha256"]

    bounds = argonne_cal_01_bounds()
    assert sha256_mapping(bounds.as_dict()) == manifest["calibration_bounds_sha256"]
    assert tuple(manifest["calibration_parameters"]) == CAL_01_PARAMETER_NAMES
    assert "radiator_ua_nominal_w_per_k" not in manifest["calibration_parameters"]


def test_cal01_lock_preserves_original_argonne_source_fingerprint():
    manifest = json.loads(LOCK_PATH.read_text(encoding="utf-8"))["manifest"]
    fingerprint = manifest["dataset_fingerprint"]
    assert fingerprint["file_name"] == "71207062 Test Data.txt"
    assert fingerprint["sha256_hex"] == "4065b06eedefa5728ac6b8cb7c268f5f354021cf8bd98bf204dbdfcd74985e09"
    assert fingerprint["size_bytes"] == 5112912


def test_bounded_calibration_uses_normalized_coordinates_and_moves_on_synthetic_case():
    result = run_synthetic_bounded_calibration_harness(max_nfev=80)
    calibration = result.calibration

    assert calibration.success is True
    assert calibration.optimization_coordinate_system == "normalized_bound_fraction_0_to_1"
    assert calibration.optimizer_diff_step == pytest.approx(0.05)
    assert calibration.final_cost < 0.25 * calibration.initial_cost
    assert calibration.calibrated_parameter_snapshot_sha256 != calibration.initial_parameter_snapshot_sha256
