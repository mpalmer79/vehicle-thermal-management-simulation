from __future__ import annotations

import argparse
from dataclasses import fields, replace
import json
from pathlib import Path

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap
from vtms_validation.calibration import run_bounded_calibration
from vtms_validation.manifest import (
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from vtms_validation.physical_bounds import argonne_cal_rad_01_bounds


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "validation_configs" / "argonne_2012_focus_cal_rad_01_manifest.json"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_manifest(payload: dict[str, object]) -> ValidationRunManifest:
    manifest_payload = dict(payload["manifest"])
    fingerprint_payload = dict(manifest_payload["dataset_fingerprint"])
    return ValidationRunManifest(
        run_id=str(manifest_payload["run_id"]),
        dataset_id=str(manifest_payload["dataset_id"]),
        role=ValidationRole(str(manifest_payload["role"])),
        evidence_grade=EvidenceGrade(str(manifest_payload["evidence_grade"])),
        dataset_fingerprint=DatasetFingerprint(
            file_name=str(fingerprint_payload["file_name"]),
            sha256_hex=str(fingerprint_payload["sha256_hex"]),
            size_bytes=int(fingerprint_payload["size_bytes"]),
        ),
        parameter_snapshot_sha256=str(manifest_payload["parameter_snapshot_sha256"]),
        calibration_parameters=tuple(str(value) for value in manifest_payload["calibration_parameters"]),
        physical_evidence=bool(manifest_payload["physical_evidence"]),
        preprocessing_snapshot_sha256=str(manifest_payload["preprocessing_snapshot_sha256"]),
        calibration_bounds_sha256=str(manifest_payload["calibration_bounds_sha256"]),
        notes=str(manifest_payload.get("notes", "")),
    )


def _upstream_parameters(result_payload: dict[str, object]) -> ModelParameters:
    snapshot = dict(result_payload["calibrated_model_parameters"])
    parameter_fields = {item.name for item in fields(ModelParameters)}
    updates = {
        name: float(value)
        for name, value in snapshot.items()
        if name in parameter_fields
    }
    parameters = replace(ModelParameters(), **updates)
    parameters.validate()
    return parameters


def run(source_path: Path) -> dict[str, object]:
    lock = _load_json(LOCK_PATH)
    execution = dict(lock["execution"])
    optimizer = dict(execution["optimizer"])
    manifest = _build_manifest(lock)
    manifest.validate()

    upstream_path = ROOT / str(lock["upstream_calibration_result"])
    upstream = _load_json(upstream_path)
    initial_parameters = _upstream_parameters(upstream)
    initial_parameter_sha = sha256_mapping(initial_parameters.snapshot())
    if initial_parameter_sha != manifest.parameter_snapshot_sha256:
        raise RuntimeError("CAL-RAD-01 upstream CAL-01 parameter snapshot does not match the frozen manifest")

    signal_map_path = ROOT / str(execution["signal_map_file"])
    signal_map = ArgonneSignalMap.from_json(signal_map_path)
    signal_map_sha = sha256_mapping(signal_map.snapshot())
    if signal_map_sha != manifest.preprocessing_snapshot_sha256:
        raise RuntimeError("CAL-RAD-01 signal-map snapshot does not match the frozen manifest")

    bounds = argonne_cal_rad_01_bounds()
    bounds_sha = sha256_mapping(bounds.as_dict())
    if bounds_sha != manifest.calibration_bounds_sha256:
        raise RuntimeError("CAL-RAD-01 staged bound snapshot does not match the frozen manifest")

    dataset = ArgonneD3Adapter().load(source_path, signal_map)
    if dataset.metadata.get("source_sha256") != manifest.dataset_fingerprint.sha256_hex:
        raise RuntimeError("CAL-RAD-01 source file SHA-256 does not match the frozen manifest")
    if int(dataset.metadata.get("source_size_bytes", -1)) != manifest.dataset_fingerprint.size_bytes:
        raise RuntimeError("CAL-RAD-01 source file size does not match the frozen manifest")

    result = run_bounded_calibration(
        dataset,
        manifest,
        initial_parameters=initial_parameters,
        bounds=bounds,
        initial_engine_temp_c=None,
        fuel_lhv_j_per_kg=float(execution["fuel_lhv_j_per_kg"]),
        max_nfev=int(optimizer["max_nfev"]),
        optimizer_diff_step=float(optimizer["diff_step"]),
        boundary_fraction=float(optimizer["boundary_fraction"]),
    )

    return {
        "run_id": manifest.run_id,
        "evidence_grade": manifest.evidence_grade.value,
        "formal_validation_claim": False,
        "calibration_stage": "CAL-RAD-01 radiator-active highway",
        "source_test_id": signal_map.metadata.get("source_test_id"),
        "source_sha256": dataset.metadata.get("source_sha256"),
        "signal_map_sha256": signal_map_sha,
        "upstream_cal01_parameter_snapshot_sha256": initial_parameter_sha,
        "calibration_bounds_sha256": bounds_sha,
        "initial_engine_temp_policy": execution["initial_engine_temp_policy"],
        "fuel_lhv_j_per_kg": float(execution["fuel_lhv_j_per_kg"]),
        "optimizer": optimizer,
        "result": result.as_dict(),
        "interpretation": {
            "calibration_threshold_pass_is_not_validation": True,
            "boundary_hugging_parameters_require_caution": list(result.boundary_parameter_names),
            "upstream_cal01_parameters_remained_frozen": True,
            "next_stage_if_frozen": (
                "Freeze the final staged parameter snapshot. Only then may the preregistered holdouts be executed without retuning."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute the locked VTMS CAL-RAD-01 Argonne radiator calibration against a local source file."
    )
    parser.add_argument("source", type=Path, help="Path to the original 71207057 Test Data.txt file")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    payload = run(args.source)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
