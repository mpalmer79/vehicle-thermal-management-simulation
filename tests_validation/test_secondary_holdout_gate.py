from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneSignalMap
from vtms_validation.manifest import sha256_mapping


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "validation_configs" / "argonne_2012_focus_val_sss_01_manifest.json"
PRIMARY_RESULT = ROOT / "validation_outputs" / "ARGONNE_VAL_HOT_01_FORMAL_RESULT.json"
FINAL_STAGED_RESULT = ROOT / "validation_outputs" / "ARGONNE_CAL_RAD_01_FORMAL_RESULT.json"


def _parameters_from_final_staged_result(payload: dict[str, object]) -> ModelParameters:
    snapshot = dict(payload["calibrated_model_parameters"])
    allowed = {item.name for item in fields(ModelParameters)}
    parameters = replace(
        ModelParameters(),
        **{name: float(value) for name, value in snapshot.items() if name in allowed},
    )
    parameters.validate()
    return parameters


def test_secondary_holdout_is_locked_only_after_primary_failure_is_frozen():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))

    assert primary["acceptance"]["claim_label"] == "formal_holdout_acceptance_fail"
    assert lock["audit"]["primary_holdout_failure_already_frozen"] is True
    assert lock["audit"]["secondary_result_may_not_overturn_primary_formal_failure"] is True


def test_secondary_holdout_uses_final_staged_snapshot_and_forbids_fitting():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    final_result = json.loads(FINAL_STAGED_RESULT.read_text(encoding="utf-8"))
    parameters = _parameters_from_final_staged_result(final_result)

    assert sha256_mapping(parameters.snapshot()) == lock["manifest"]["parameter_snapshot_sha256"]
    assert lock["manifest"]["role"] == "holdout"
    assert lock["manifest"]["evidence_grade"] == "independent_holdout"
    assert lock["manifest"]["calibration_parameters"] == []
    assert lock["manifest"]["physical_evidence"] is True


def test_secondary_holdout_mapping_is_frozen_before_source_residual_inspection():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    execution = lock["execution"]
    manifest = lock["manifest"]
    signal_map = ArgonneSignalMap.from_json(ROOT / execution["signal_map_file"])

    assert sha256_mapping(signal_map.snapshot()) == manifest["preprocessing_snapshot_sha256"]
    assert manifest["preprocessing_snapshot_sha256"] == "4099b937418f78b393b536f59528d00ac8dd301339a43aa9b190b4e420391137"
    assert signal_map.start_time_s == 0.0
    assert signal_map.end_time_s == 446.1
    assert signal_map.exclude_time_intervals_s == ()


def test_secondary_holdout_source_identity_matches_pre_fit_inventory():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    assert lock["manifest"]["dataset_fingerprint"] == {
        "file_name": "71207052 Test Data.txt",
        "sha256_hex": "b5a837449f824ad76b00a6ab7da7ae92486b4feec0b4e3a81eb126bac14b0f02",
        "size_bytes": 1301807,
    }
