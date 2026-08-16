from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json

import numpy as np

from vtms_v1.config import ModelParameters
from vtms_v1.scenario import Scenario
from vtms_v1.simulation import SimulationRunner

from .acceptance import AcceptanceEvaluation, evaluate_acceptance
from .calibration import (
    BoundedCalibrationResult,
    CalibrationBounds,
    ParameterBound,
    run_bounded_calibration,
)
from .dataset import ValidationDataset
from .manifest import (
    ALLOWED_CALIBRATION_PARAMETERS,
    DatasetFingerprint,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from .runner import ComparisonResult, run_controlled_comparison


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    duration_s: float
    sample_interval_s: float
    initial_engine_temp_c: float
    initial_coolant_temp_c: float
    ambient_temp_c: tuple[float, ...]
    engine_speed_rpm: tuple[float, ...]
    vehicle_speed_m_s: tuple[float, ...]
    fuel_energy_rate_w: tuple[float, ...]
    segment_edges_s: tuple[float, ...]
    measurement_noise_amplitude_c: float = 0.0

    def validate(self) -> None:
        if self.duration_s <= 0 or self.sample_interval_s <= 0:
            raise ValueError("synthetic case duration and sample interval must be positive")
        if len(self.segment_edges_s) < 2:
            raise ValueError("synthetic case requires at least one segment")
        if self.segment_edges_s[0] != 0.0 or self.segment_edges_s[-1] != self.duration_s:
            raise ValueError("synthetic segment edges must span exactly 0..duration_s")
        if any(b <= a for a, b in zip(self.segment_edges_s, self.segment_edges_s[1:])):
            raise ValueError("synthetic segment edges must be strictly increasing")
        expected = len(self.segment_edges_s) - 1
        for name, values in {
            "ambient_temp_c": self.ambient_temp_c,
            "engine_speed_rpm": self.engine_speed_rpm,
            "vehicle_speed_m_s": self.vehicle_speed_m_s,
            "fuel_energy_rate_w": self.fuel_energy_rate_w,
        }.items():
            if len(values) != expected:
                raise ValueError(f"{name} must contain one value per synthetic segment")
        if self.measurement_noise_amplitude_c < 0:
            raise ValueError("synthetic measurement noise amplitude must be nonnegative")


@dataclass(frozen=True)
class SyntheticCalibrationHarnessResult:
    calibration: BoundedCalibrationResult
    holdout_comparison: ComparisonResult
    holdout_acceptance: AcceptanceEvaluation
    truth_parameters: ModelParameters
    synthetic_bounds: CalibrationBounds
    disclaimer: str

    def as_dict(self) -> dict[str, object]:
        return {
            "disclaimer": self.disclaimer,
            "truth_parameters": self.truth_parameters.snapshot(),
            "synthetic_bounds": self.synthetic_bounds.as_dict(),
            "calibration": self.calibration.as_dict(),
            "holdout_metrics": self.holdout_comparison.metrics.as_dict(),
            "holdout_acceptance": self.holdout_acceptance.as_dict(),
        }


def _segment_profile(case: SyntheticCase, values: tuple[float, ...], time_s: np.ndarray) -> np.ndarray:
    edges = np.asarray(case.segment_edges_s, dtype=float)
    segment_index = np.searchsorted(edges[1:], time_s, side="right")
    segment_index = np.minimum(segment_index, len(values) - 1)
    return np.asarray(values, dtype=float)[segment_index]


def _synthetic_fingerprint(case: SyntheticCase) -> DatasetFingerprint:
    payload = json.dumps(asdict(case), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return DatasetFingerprint(
        file_name=f"{case.case_id}.synthetic-recipe.json",
        sha256_hex=sha256(payload).hexdigest(),
        size_bytes=len(payload),
    )


def generate_synthetic_dataset(
    case: SyntheticCase,
    truth_parameters: ModelParameters,
) -> tuple[ValidationDataset, DatasetFingerprint]:
    """Generate deterministic non-physical data for software-pipeline verification only."""

    case.validate()
    truth_parameters.validate()
    time_s = np.arange(0.0, case.duration_s + 0.5 * case.sample_interval_s, case.sample_interval_s)
    time_s[-1] = case.duration_s
    ambient = _segment_profile(case, case.ambient_temp_c, time_s)
    rpm = _segment_profile(case, case.engine_speed_rpm, time_s)
    speed = _segment_profile(case, case.vehicle_speed_m_s, time_s)
    fuel_energy = _segment_profile(case, case.fuel_energy_rate_w, time_s)

    def profile(values: np.ndarray):
        return lambda t: float(np.interp(t, time_s, values))

    q_engine = fuel_energy * truth_parameters.wall_heat_fraction
    scenario = Scenario(
        scenario_id=f"SYN-TRUTH-{case.case_id}",
        name="Synthetic truth generator, not physical evidence",
        duration_s=case.duration_s,
        ambient_temp_c=profile(ambient),
        engine_speed_rpm=profile(rpm),
        effective_load=0.0,
        vehicle_speed_m_s=profile(speed),
        initial_engine_temp_c=case.initial_engine_temp_c,
        initial_coolant_temp_c=case.initial_coolant_temp_c,
        engine_heat_override_w=profile(q_engine),
        output_interval_s=1.0,
    )
    truth_result = SimulationRunner(parameters=truth_parameters).run(scenario)
    sim_t = np.asarray([point.time_s for point in truth_result.time_series], dtype=float)
    sim_c = np.asarray([point.coolant_temp_c for point in truth_result.time_series], dtype=float)
    measured = np.interp(time_s, sim_t, sim_c)
    if case.measurement_noise_amplitude_c:
        measured = measured + case.measurement_noise_amplitude_c * np.sin(0.071 * time_s)

    fingerprint = _synthetic_fingerprint(case)
    dataset = ValidationDataset(
        dataset_id=case.case_id,
        source_name="VTMS deterministic synthetic calibration harness",
        time_s=time_s,
        measured_coolant_temp_c=measured,
        engine_speed_rpm=rpm,
        vehicle_speed_m_s=speed,
        ambient_temp_c=ambient,
        fuel_energy_rate_w=fuel_energy,
        metadata={
            "source_sha256": fingerprint.sha256_hex,
            "synthetic": True,
            "physical_validation_evidence": False,
            "initial_engine_temp_c": case.initial_engine_temp_c,
            "generator_model_id": "VTMS-V1",
        },
    )
    dataset.validate()
    return dataset, fingerprint


def synthetic_demo_bounds() -> CalibrationBounds:
    """Test-only bounds for the synthetic harness, never Argonne calibration bounds."""

    return CalibrationBounds(
        parameters=(
            ParameterBound("wall_heat_fraction", 0.18, 0.42),
            ParameterBound("engine_thermal_capacitance_j_per_k", 30000.0, 90000.0),
            ParameterBound("engine_coolant_ua_w_per_k", 500.0, 1600.0),
            ParameterBound("radiator_ua_nominal_w_per_k", 600.0, 1800.0),
        )
    )


def _default_calibration_case() -> SyntheticCase:
    return SyntheticCase(
        case_id="SYN-CAL-01",
        duration_s=240.0,
        sample_interval_s=4.0,
        initial_engine_temp_c=82.0,
        initial_coolant_temp_c=48.0,
        segment_edges_s=(0.0, 55.0, 115.0, 175.0, 240.0),
        ambient_temp_c=(30.0, 32.0, 29.0, 34.0),
        engine_speed_rpm=(1100.0, 2200.0, 3100.0, 1500.0),
        vehicle_speed_m_s=(0.0, 12.0, 25.0, 4.0),
        fuel_energy_rate_w=(52000.0, 68000.0, 43000.0, 58000.0),
    )


def _default_holdout_case() -> SyntheticCase:
    return SyntheticCase(
        case_id="SYN-HOLD-01",
        duration_s=210.0,
        sample_interval_s=4.0,
        initial_engine_temp_c=76.0,
        initial_coolant_temp_c=44.0,
        segment_edges_s=(0.0, 45.0, 105.0, 155.0, 210.0),
        ambient_temp_c=(20.0, 24.0, 27.0, 22.0),
        engine_speed_rpm=(1800.0, 2800.0, 1400.0, 3400.0),
        vehicle_speed_m_s=(18.0, 28.0, 6.0, 30.0),
        fuel_energy_rate_w=(61000.0, 47000.0, 65000.0, 50000.0),
    )


def run_synthetic_bounded_calibration_harness(
    *,
    initial_parameters: ModelParameters | None = None,
    truth_parameters: ModelParameters | None = None,
    bounds: CalibrationBounds | None = None,
    max_nfev: int = 80,
) -> SyntheticCalibrationHarnessResult:
    """Exercise calibration, freeze, holdout, and acceptance without physical data.

    Synthetic success proves software plumbing only. It is not verification that
    the model topology is physically adequate and it is never validation evidence.
    """

    initial = initial_parameters or ModelParameters()
    truth = truth_parameters or replace(
        ModelParameters(),
        wall_heat_fraction=0.315,
        engine_thermal_capacitance_j_per_k=57500.0,
        engine_coolant_ua_w_per_k=860.0,
        radiator_ua_nominal_w_per_k=1280.0,
    )
    calibration_bounds = bounds or synthetic_demo_bounds()

    calibration_case = _default_calibration_case()
    calibration_dataset, calibration_fingerprint = generate_synthetic_dataset(
        calibration_case, truth
    )
    calibration_manifest = ValidationRunManifest(
        run_id="SYN-CAL-01",
        dataset_id=calibration_dataset.dataset_id,
        role=ValidationRole.CALIBRATION,
        evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
        dataset_fingerprint=calibration_fingerprint,
        parameter_snapshot_sha256=sha256_mapping(initial.snapshot()),
        calibration_parameters=tuple(ALLOWED_CALIBRATION_PARAMETERS),
        notes="Synthetic software-pipeline exercise only; not physical evidence and not approved calibration bounds.",
    )
    calibration = run_bounded_calibration(
        calibration_dataset,
        calibration_manifest,
        initial_parameters=initial,
        bounds=calibration_bounds,
        initial_engine_temp_c=calibration_case.initial_engine_temp_c,
        max_nfev=max_nfev,
    )

    holdout_case = _default_holdout_case()
    holdout_dataset, holdout_fingerprint = generate_synthetic_dataset(holdout_case, truth)
    holdout_manifest = ValidationRunManifest(
        run_id="SYN-HOLD-01",
        dataset_id=holdout_dataset.dataset_id,
        role=ValidationRole.HOLDOUT,
        evidence_grade=EvidenceGrade.INDEPENDENT_HOLDOUT,
        dataset_fingerprint=holdout_fingerprint,
        parameter_snapshot_sha256=calibration.calibrated_parameter_snapshot_sha256,
        notes="Synthetic untouched holdout for pipeline verification only; never physical validation evidence.",
    )
    holdout_comparison = run_controlled_comparison(
        holdout_dataset,
        holdout_manifest,
        parameters=calibration.calibrated_model_parameters,
        initial_engine_temp_c=holdout_case.initial_engine_temp_c,
    )
    holdout_acceptance = evaluate_acceptance(holdout_comparison, holdout_manifest)

    return SyntheticCalibrationHarnessResult(
        calibration=calibration,
        holdout_comparison=holdout_comparison,
        holdout_acceptance=holdout_acceptance,
        truth_parameters=truth,
        synthetic_bounds=calibration_bounds,
        disclaimer=(
            "Synthetic harness output verifies calibration/acceptance software only. "
            "It is not physical validation, does not justify VTMS-V1 model adequacy, "
            "and its test-only parameter bounds must not be reused for Argonne fitting."
        ),
    )
