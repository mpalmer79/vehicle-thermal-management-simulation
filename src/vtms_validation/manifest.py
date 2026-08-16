from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from vtms_v1.constants import EQUATION_SET, MODEL_ID, MODEL_VERSION, PARAMETER_SET


class ValidationRole(StrEnum):
    PLAUSIBILITY = "plausibility"
    CALIBRATION = "calibration"
    HOLDOUT = "holdout"
    CHALLENGE = "challenge"


class EvidenceGrade(StrEnum):
    SECONDARY_PLAUSIBILITY = "secondary_plausibility"
    CONTROLLED_CALIBRATION = "controlled_calibration"
    INDEPENDENT_HOLDOUT = "independent_holdout"
    CHALLENGE_ONLY = "challenge_only"


ROLE_EVIDENCE_GRADE: dict[ValidationRole, EvidenceGrade] = {
    ValidationRole.PLAUSIBILITY: EvidenceGrade.SECONDARY_PLAUSIBILITY,
    ValidationRole.CALIBRATION: EvidenceGrade.CONTROLLED_CALIBRATION,
    ValidationRole.HOLDOUT: EvidenceGrade.INDEPENDENT_HOLDOUT,
    ValidationRole.CHALLENGE: EvidenceGrade.CHALLENGE_ONLY,
}

# Frozen from the VTMS physical-validation protocol. Adding another fitted
# parameter requires an explicit protocol/model-governance change.
ALLOWED_CALIBRATION_PARAMETERS = (
    "wall_heat_fraction",
    "engine_thermal_capacitance_j_per_k",
    "engine_coolant_ua_w_per_k",
    "radiator_ua_nominal_w_per_k",
)


@dataclass(frozen=True)
class AcceptanceCriteria:
    """Project acceptance thresholds, not an SAE or Argonne standard."""

    rmse_c_max: float = 5.0
    mae_c_max: float = 4.0
    abs_bias_c_max: float = 3.0
    p90_abs_error_c_max: float = 7.0
    threshold_arrival_error_s_max: float = 60.0
    threshold_arrival_error_fraction_max: float = 0.10


@dataclass(frozen=True)
class DatasetFingerprint:
    file_name: str
    sha256_hex: str
    size_bytes: int

    @classmethod
    def from_path(cls, path: str | Path) -> "DatasetFingerprint":
        source = Path(path)
        digest = sha256()
        size_bytes = 0
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size_bytes += len(chunk)
        return cls(file_name=source.name, sha256_hex=digest.hexdigest(), size_bytes=size_bytes)

    def validate(self) -> None:
        if not self.file_name.strip():
            raise ValueError("dataset fingerprint requires a file name")
        if self.size_bytes < 0:
            raise ValueError("dataset fingerprint size_bytes must be nonnegative")
        if len(self.sha256_hex) != 64 or any(char not in "0123456789abcdef" for char in self.sha256_hex.lower()):
            raise ValueError("dataset fingerprint sha256_hex must be a 64-character hexadecimal SHA-256")


@dataclass(frozen=True)
class ValidationRunManifest:
    run_id: str
    dataset_id: str
    role: ValidationRole
    evidence_grade: EvidenceGrade
    dataset_fingerprint: DatasetFingerprint
    parameter_snapshot_sha256: str
    model_id: str = MODEL_ID
    model_version: str = MODEL_VERSION
    equation_set: str = EQUATION_SET
    parameter_set: str = PARAMETER_SET
    calibration_parameters: tuple[str, ...] = ()
    acceptance_criteria: AcceptanceCriteria = field(default_factory=AcceptanceCriteria)
    physical_evidence: bool = False
    notes: str = ""

    def validate(self) -> None:
        if not self.run_id.strip():
            raise ValueError("validation manifest requires run_id")
        if not self.dataset_id.strip():
            raise ValueError("validation manifest requires dataset_id")
        self.dataset_fingerprint.validate()
        expected_grade = ROLE_EVIDENCE_GRADE[self.role]
        if self.evidence_grade != expected_grade:
            raise ValueError(
                f"role {self.role.value!r} requires evidence grade {expected_grade.value!r}, "
                f"got {self.evidence_grade.value!r}"
            )
        if len(self.parameter_snapshot_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.parameter_snapshot_sha256.lower()
        ):
            raise ValueError("parameter_snapshot_sha256 must be a 64-character hexadecimal SHA-256")

        unknown = sorted(set(self.calibration_parameters) - set(ALLOWED_CALIBRATION_PARAMETERS))
        if unknown:
            raise ValueError(f"calibration manifest contains unapproved fitted parameters: {unknown}")
        if self.role is not ValidationRole.CALIBRATION and self.calibration_parameters:
            raise ValueError(f"{self.role.value} runs cannot declare calibration parameters")
        if self.role is ValidationRole.CALIBRATION and not self.calibration_parameters:
            raise ValueError("calibration runs must declare the preregistered fitted-parameter subset")

    @property
    def permits_parameter_fitting(self) -> bool:
        return self.role is ValidationRole.CALIBRATION

    def assert_parameter_fit_allowed(self, parameter_names: tuple[str, ...] | list[str]) -> None:
        self.validate()
        if not self.permits_parameter_fitting:
            raise PermissionError(f"parameter fitting is prohibited for {self.role.value} runs")
        requested = set(parameter_names)
        declared = set(self.calibration_parameters)
        if not requested <= declared:
            undeclared = sorted(requested - declared)
            raise PermissionError(f"parameter fitting requested undeclared parameters: {undeclared}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["role"] = self.role.value
        payload["evidence_grade"] = self.evidence_grade.value
        return payload


def sha256_mapping(mapping: Mapping[str, Any]) -> str:
    """Hash a mapping using stable JSON serialization for provenance records."""

    serialized = json.dumps(mapping, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(serialized.encode("utf-8")).hexdigest()
