from pathlib import Path

import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap
from vtms_validation.manifest import (
    ALLOWED_CALIBRATION_PARAMETERS,
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)


def _fingerprint() -> DatasetFingerprint:
    return DatasetFingerprint(file_name="argonne.csv", sha256_hex="a" * 64, size_bytes=123)


def _parameter_hash() -> str:
    return sha256_mapping(ModelParameters().snapshot())


def test_dataset_fingerprint_detects_byte_changes(tmp_path: Path):
    source = tmp_path / "source.csv"
    source.write_bytes(b"alpha")
    first = DatasetFingerprint.from_path(source)
    source.write_bytes(b"alphb")
    second = DatasetFingerprint.from_path(source)
    assert first.sha256_hex != second.sha256_hex
    assert first.size_bytes == second.size_bytes == 5


def test_holdout_manifest_prohibits_parameter_fitting():
    manifest = ValidationRunManifest(
        run_id="VAL-CS-01",
        dataset_id="ARGONNE-D3-HOLDOUT",
        role=ValidationRole.HOLDOUT,
        evidence_grade=EvidenceGrade.INDEPENDENT_HOLDOUT,
        dataset_fingerprint=_fingerprint(),
        parameter_snapshot_sha256=_parameter_hash(),
    )
    manifest.validate()
    with pytest.raises(PermissionError, match="prohibited"):
        manifest.assert_parameter_fit_allowed(["wall_heat_fraction"])


def test_calibration_manifest_allows_only_preregistered_subset():
    manifest = ValidationRunManifest(
        run_id="CAL-01",
        dataset_id="ARGONNE-D3-CAL",
        role=ValidationRole.CALIBRATION,
        evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
        dataset_fingerprint=_fingerprint(),
        parameter_snapshot_sha256=_parameter_hash(),
        calibration_parameters=ALLOWED_CALIBRATION_PARAMETERS,
    )
    manifest.validate()
    manifest.assert_parameter_fit_allowed(["wall_heat_fraction", "radiator_ua_nominal_w_per_k"])
    with pytest.raises(PermissionError, match="undeclared"):
        manifest.assert_parameter_fit_allowed(["ram_capture_coefficient"])


def test_calibration_manifest_rejects_unapproved_parameter():
    manifest = ValidationRunManifest(
        run_id="CAL-01",
        dataset_id="ARGONNE-D3-CAL",
        role=ValidationRole.CALIBRATION,
        evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
        dataset_fingerprint=_fingerprint(),
        parameter_snapshot_sha256=_parameter_hash(),
        calibration_parameters=("wall_heat_fraction", "ram_capture_coefficient"),
    )
    with pytest.raises(ValueError, match="unapproved"):
        manifest.validate()


def test_manifest_rejects_role_evidence_mismatch():
    manifest = ValidationRunManifest(
        run_id="VAL-01",
        dataset_id="ARGONNE-D3-HOLDOUT",
        role=ValidationRole.HOLDOUT,
        evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
        dataset_fingerprint=_fingerprint(),
        parameter_snapshot_sha256=_parameter_hash(),
    )
    with pytest.raises(ValueError, match="requires evidence grade"):
        manifest.validate()


def test_argonne_mapping_requires_reviewed_source_names_and_units():
    mapping = ArgonneSignalMap(
        dataset_id="ARGONNE-D3-TEST",
        source_name="Argonne D3",
        file_format="csv",
        columns={
            "time_s": "REPLACE_WITH_D3_TIME_COLUMN",
            "engine_coolant_temp_c": "ECT",
            "engine_speed_rpm": "RPM",
            "vehicle_speed_m_s": "Speed",
            "ambient_temp_c": "Ambient",
        },
        units={
            "time_s": "s",
            "engine_coolant_temp_c": "C",
            "engine_speed_rpm": "rpm",
            "vehicle_speed_m_s": "m/s",
            "ambient_temp_c": "C",
        },
    )
    with pytest.raises(ValueError, match="unresolved"):
        mapping.validate()


def test_argonne_explicit_mapping_normalizes_units_and_records_hashes(tmp_path: Path):
    source = tmp_path / "d3.csv"
    source.write_text(
        "TimeMs,ECT_F,RPM,SpeedMph,AmbientF,Fuel_g_s\n"
        "1000,194,900,0,68,1.0\n"
        "1100,195.8,1000,10,69.8,1.2\n",
        encoding="utf-8",
    )
    mapping = ArgonneSignalMap(
        dataset_id="ARGONNE-D3-TEST",
        source_name="Argonne D3 test fixture",
        file_format="csv",
        columns={
            "time_s": "TimeMs",
            "engine_coolant_temp_c": "ECT_F",
            "engine_speed_rpm": "RPM",
            "vehicle_speed_m_s": "SpeedMph",
            "ambient_temp_c": "AmbientF",
            "fuel_rate_kg_s": "Fuel_g_s",
        },
        units={
            "time_s": "ms",
            "engine_coolant_temp_c": "F",
            "engine_speed_rpm": "rpm",
            "vehicle_speed_m_s": "mph",
            "ambient_temp_c": "F",
            "fuel_rate_kg_s": "g/s",
        },
    )

    dataset = ArgonneD3Adapter().load(source, mapping)
    assert dataset.time_s.tolist() == pytest.approx([0.0, 0.1])
    assert dataset.measured_coolant_temp_c.tolist() == pytest.approx([90.0, 91.0])
    assert dataset.vehicle_speed_m_s[-1] == pytest.approx(4.4704)
    assert dataset.ambient_temp_c.tolist() == pytest.approx([20.0, 21.0])
    assert dataset.fuel_rate_kg_s.tolist() == pytest.approx([0.001, 0.0012])
    assert len(dataset.metadata["source_sha256"]) == 64
    assert len(dataset.metadata["signal_map_sha256"]) == 64
    assert dataset.metadata["mapping_policy"] == "explicit_no_schema_guessing"
