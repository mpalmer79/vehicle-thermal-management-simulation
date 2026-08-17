from __future__ import annotations

import argparse
from dataclasses import fields, replace
import json
from pathlib import Path

from vtms_v1.config import ModelParameters
from vtms_validation.acceptance import evaluate_acceptance
from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap
from vtms_validation.manifest import (
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from vtms_validation.runner import run_controlled_comparison


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "validation_configs" / "argonne_2012_focus_val_sss_01_manifest.json"


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
        calibration_parameters=(),
        physical_evidence=bool(manifest_payload["physical_evidence"]),
        preprocessing_snapshot_sha256=str(manifest_payload["preprocessing_snapshot_sha256"]),
        notes=str(manifest_payload.get("notes", "")),
    )


def _frozen_parameters(result_payload: dict[str, object]) -> ModelParameters:
    snapshot = dict(result_payload["calibrated_model_parameters"])
    parameter_fields = {item.name for item in fields(ModelParameters)}
    parameters = replace(
        ModelParameters(),
        **{
            name: float(value)
            for name, value in snapshot.items()
            if name in parameter_fields
        },
    )
    parameters.validate()
    return parameters


def run(source_path: Path) -> dict[str, object]:
    lock = _load_json(LOCK_PATH)
    execution = dict(lock["execution"])
    manifest = _build_manifest(lock)
    manifest.validate()
    if manifest.permits_parameter_fitting:
        raise RuntimeError("VAL-SSS-01 must never permit parameter fitting")

    primary = _load_json(ROOT / str(lock["primary_holdout_result"]))
    if primary["acceptance"]["claim_label"] != "formal_holdout_acceptance_fail":
        raise RuntimeError("VAL-SSS-01 requires the primary holdout failure to be frozen first")

    upstream = _load_json(ROOT / str(lock["upstream_calibration_result"]))
    parameters = _frozen_parameters(upstream)
    parameter_sha = sha256_mapping(parameters.snapshot())
    if parameter_sha != manifest.parameter_snapshot_sha256:
        raise RuntimeError("VAL-SSS-01 final staged parameter snapshot does not match the frozen manifest")

    signal_map_path = ROOT / str(execution["signal_map_file"])
    signal_map = ArgonneSignalMap.from_json(signal_map_path)
    signal_map_sha = sha256_mapping(signal_map.snapshot())
    if signal_map_sha != manifest.preprocessing_snapshot_sha256:
        raise RuntimeError("VAL-SSS-01 signal-map snapshot does not match the frozen manifest")

    dataset = ArgonneD3Adapter().load(source_path, signal_map)
    if dataset.metadata.get("source_sha256") != manifest.dataset_fingerprint.sha256_hex:
        raise RuntimeError("VAL-SSS-01 source file SHA-256 does not match the frozen manifest")
    if int(dataset.metadata.get("source_size_bytes", -1)) != manifest.dataset_fingerprint.size_bytes:
        raise RuntimeError("VAL-SSS-01 source file size does not match the frozen manifest")

    comparison = run_controlled_comparison(
        dataset,
        manifest,
        parameters=parameters,
        initial_engine_temp_c=None,
        fuel_lhv_j_per_kg=float(execution["fuel_lhv_j_per_kg"]),
    )
    acceptance = evaluate_acceptance(comparison, manifest)

    return {
        "run_id": manifest.run_id,
        "evidence_grade": manifest.evidence_grade.value,
        "source_test_id": signal_map.metadata.get("source_test_id"),
        "source_sha256": dataset.metadata.get("source_sha256"),
        "signal_map_sha256": signal_map_sha,
        "parameter_snapshot_sha256": parameter_sha,
        "fuel_lhv_j_per_kg": float(execution["fuel_lhv_j_per_kg"]),
        "metrics": comparison.metrics.as_dict(),
        "acceptance": acceptance.as_dict(),
        "input_preprocessing_metadata": comparison.input_preprocessing_metadata,
        "interpretation": {
            "parameter_fitting_performed": False,
            "retuning_permitted_after_result": False,
            "secondary_result_may_overturn_primary_formal_failure": False,
            "purpose": "confirmatory_generalization_evidence_only",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute the locked VTMS VAL-SSS-01 secondary independent Argonne holdout."
    )
    parser.add_argument("source", type=Path, help="Path to the original 71207052 Test Data.txt file")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    payload = run(args.source)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
