from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from vtms_v1.config import ModelParameters

from .manifest import (
    ALLOWED_CALIBRATION_PARAMETERS,
    EvidenceGrade,
    ValidationRole,
    ValidationRunManifest,
    sha256_mapping,
)
from .runner import run_controlled_comparison
from .synthetic import (
    SyntheticCase,
    _default_calibration_case,
    _default_holdout_case,
    generate_synthetic_dataset,
)


@dataclass(frozen=True)
class ParameterSensitivity:
    name: str
    perturbation_fraction: float
    rms_log_sensitivity_c: float
    peak_abs_log_sensitivity_c: float

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "perturbation_fraction": self.perturbation_fraction,
            "rms_log_sensitivity_c": self.rms_log_sensitivity_c,
            "peak_abs_log_sensitivity_c": self.peak_abs_log_sensitivity_c,
        }


@dataclass(frozen=True)
class IdentifiabilityDiagnostic:
    parameter_names: tuple[str, ...]
    sensitivities: tuple[ParameterSensitivity, ...]
    correlation_matrix: np.ndarray
    singular_values: np.ndarray
    normalized_jacobian_condition_number: float
    max_abs_parameter_correlation: float
    warning: bool
    note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "parameter_names": list(self.parameter_names),
            "sensitivities": [item.as_dict() for item in self.sensitivities],
            "correlation_matrix": self.correlation_matrix.tolist(),
            "singular_values": self.singular_values.tolist(),
            "normalized_jacobian_condition_number": self.normalized_jacobian_condition_number,
            "max_abs_parameter_correlation": self.max_abs_parameter_correlation,
            "warning": self.warning,
            "note": self.note,
        }


@dataclass(frozen=True)
class WarmupStageSensitivity:
    name: str
    rms_fractional_sensitivity_c: float
    peak_abs_fractional_sensitivity_c: float
    relative_rms_to_strongest: float

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "rms_fractional_sensitivity_c": self.rms_fractional_sensitivity_c,
            "peak_abs_fractional_sensitivity_c": self.peak_abs_fractional_sensitivity_c,
            "relative_rms_to_strongest": self.relative_rms_to_strongest,
        }


@dataclass(frozen=True)
class WarmupStageIdentifiabilityDiagnostic:
    dataset_ids: tuple[str, ...]
    parameter_names: tuple[str, ...]
    perturbation_fraction: float
    sample_count: int
    sensitivities: tuple[WarmupStageSensitivity, ...]
    pairwise_cosine_matrix: np.ndarray
    singular_values: np.ndarray
    normalized_singular_values: np.ndarray
    numerical_rank: int
    normalized_jacobian_condition_number: float
    weakest_parameter: str
    weakest_relative_rms: float
    strongest_abs_pairwise_cosine: float
    weak_parameter_names: tuple[str, ...]
    four_parameter_cal_01_authorized: bool
    note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_ids": list(self.dataset_ids),
            "parameter_names": list(self.parameter_names),
            "perturbation_fraction": self.perturbation_fraction,
            "sample_count": self.sample_count,
            "sensitivities": [item.as_dict() for item in self.sensitivities],
            "pairwise_cosine_matrix": self.pairwise_cosine_matrix.tolist(),
            "singular_values": self.singular_values.tolist(),
            "normalized_singular_values": self.normalized_singular_values.tolist(),
            "numerical_rank": self.numerical_rank,
            "normalized_jacobian_condition_number": self.normalized_jacobian_condition_number,
            "weakest_parameter": self.weakest_parameter,
            "weakest_relative_rms": self.weakest_relative_rms,
            "strongest_abs_pairwise_cosine": self.strongest_abs_pairwise_cosine,
            "weak_parameter_names": list(self.weak_parameter_names),
            "four_parameter_cal_01_authorized": self.four_parameter_cal_01_authorized,
            "note": self.note,
        }


def synthetic_identifiability_case() -> SyntheticCase:
    """Excite warm-up, thermostat/radiator, speed, and fuel-rate regimes without physical data."""

    return SyntheticCase(
        case_id="SYN-IDENT-01",
        duration_s=600.0,
        sample_interval_s=5.0,
        initial_engine_temp_c=30.0,
        initial_coolant_temp_c=28.0,
        segment_edges_s=(0.0, 90.0, 180.0, 300.0, 420.0, 510.0, 600.0),
        ambient_temp_c=(22.0, 24.0, 25.0, 23.0, 27.0, 24.0),
        engine_speed_rpm=(950.0, 1800.0, 2800.0, 1400.0, 3300.0, 2100.0),
        vehicle_speed_m_s=(0.0, 10.0, 25.0, 4.0, 30.0, 15.0),
        fuel_energy_rate_w=(36000.0, 52000.0, 70000.0, 44000.0, 76000.0, 50000.0),
    )


def _prediction(dataset, fingerprint, parameters: ModelParameters, initial_engine_temp_c: float) -> np.ndarray:
    manifest = ValidationRunManifest(
        run_id="SYN-IDENT-PREFLIGHT",
        dataset_id=dataset.dataset_id,
        role=ValidationRole.CALIBRATION,
        evidence_grade=EvidenceGrade.CONTROLLED_CALIBRATION,
        dataset_fingerprint=fingerprint,
        parameter_snapshot_sha256=sha256_mapping(parameters.snapshot()),
        calibration_parameters=tuple(ALLOWED_CALIBRATION_PARAMETERS),
        notes="Synthetic pre-Argonne sensitivity/identifiability diagnostic only; not physical evidence.",
    )
    comparison = run_controlled_comparison(
        dataset,
        manifest,
        parameters=parameters,
        initial_engine_temp_c=initial_engine_temp_c,
    )
    return np.asarray(comparison.predicted_coolant_temp_c, dtype=float)


def evaluate_synthetic_identifiability(*, parameters: ModelParameters | None = None, perturbation_fraction: float = 0.05) -> IdentifiabilityDiagnostic:
    """Evaluate broad local coolant-trace sensitivity before any physical residual is opened."""
    if not 0.001 <= perturbation_fraction <= 0.20:
        raise ValueError("perturbation_fraction must be in [0.001, 0.20]")
    baseline = parameters or ModelParameters()
    baseline.validate()
    case = synthetic_identifiability_case()
    dataset, fingerprint = generate_synthetic_dataset(case, baseline)
    columns: list[np.ndarray] = []
    sensitivities: list[ParameterSensitivity] = []
    for name in ALLOWED_CALIBRATION_PARAMETERS:
        theta = float(getattr(baseline, name))
        lower_value = theta * (1.0 - perturbation_fraction)
        upper_value = theta * (1.0 + perturbation_fraction)
        lower = replace(baseline, **{name: lower_value})
        upper = replace(baseline, **{name: upper_value})
        lower.validate(); upper.validate()
        y_minus = _prediction(dataset, fingerprint, lower, case.initial_engine_temp_c)
        y_plus = _prediction(dataset, fingerprint, upper, case.initial_engine_temp_c)
        delta_log = np.log(upper_value) - np.log(lower_value)
        column = (y_plus - y_minus) / delta_log
        columns.append(column)
        sensitivities.append(ParameterSensitivity(name, perturbation_fraction, float(np.sqrt(np.mean(column**2))), float(np.max(np.abs(column)))))
    jacobian = np.column_stack(columns)
    norms = np.linalg.norm(jacobian, axis=0)
    normalized = np.zeros_like(jacobian)
    active = norms > 1.0e-12
    normalized[:, active] = jacobian[:, active] / norms[active]
    correlation = normalized.T @ normalized
    np.fill_diagonal(correlation, 1.0)
    singular_values = np.linalg.svd(normalized, compute_uv=False)
    smallest = float(singular_values[-1]) if singular_values.size else 0.0
    condition_number = float(singular_values[0] / smallest) if smallest > 1.0e-12 else float("inf")
    off_diagonal = np.abs(correlation - np.eye(correlation.shape[0]))
    max_correlation = float(np.max(off_diagonal)) if off_diagonal.size else 0.0
    warning = bool(condition_number > 100.0 or max_correlation > 0.95 or np.any(~active))
    note = (
        "WARNING: the four-parameter coolant-only fit shows strong local collinearity or weak excitation. Treat individual fitted values as non-unique unless additional observables or constraints resolve it."
        if warning else
        "No severe local collinearity was detected in this broad synthetic excitation case, but this does not prove structural or physical identifiability on Argonne data."
    )
    return IdentifiabilityDiagnostic(tuple(ALLOWED_CALIBRATION_PARAMETERS), tuple(sensitivities), correlation, singular_values, condition_number, max_correlation, warning, note)


def evaluate_warmup_stage_identifiability(*, parameters: ModelParameters | None = None, perturbation_fraction: float = 0.01, weak_relative_rms_threshold: float = 0.02) -> WarmupStageIdentifiabilityDiagnostic:
    """Test whether existing warm-up-style profiles support one four-parameter CAL-01 fit.

    Physical datasets cannot be supplied. The function constructs deterministic synthetic
    traces internally, so it cannot inspect an Argonne residual. The relative-RMS threshold
    is a VTMS engineering heuristic, not a formal statistical or validation criterion.
    """
    if not 0.001 <= perturbation_fraction <= 0.20:
        raise ValueError("perturbation_fraction must be in [0.001, 0.20]")
    if not 0.0 < weak_relative_rms_threshold < 1.0:
        raise ValueError("weak_relative_rms_threshold must be between 0 and 1")
    baseline = parameters or ModelParameters()
    baseline.validate()
    cases = (_default_calibration_case(), _default_holdout_case())
    generated = [generate_synthetic_dataset(case, baseline) for case in cases]
    columns: list[np.ndarray] = []
    for name in ALLOWED_CALIBRATION_PARAMETERS:
        theta = float(getattr(baseline, name))
        lower = replace(baseline, **{name: theta * (1.0 - perturbation_fraction)})
        upper = replace(baseline, **{name: theta * (1.0 + perturbation_fraction)})
        lower.validate(); upper.validate()
        blocks: list[np.ndarray] = []
        for case, (dataset, fingerprint) in zip(cases, generated, strict=True):
            y_minus = _prediction(dataset, fingerprint, lower, case.initial_engine_temp_c)
            y_plus = _prediction(dataset, fingerprint, upper, case.initial_engine_temp_c)
            blocks.append((y_plus - y_minus) / (2.0 * perturbation_fraction))
        columns.append(np.concatenate(blocks))
    jacobian = np.column_stack(columns)
    rms_values = np.asarray([np.sqrt(np.mean(column**2)) for column in columns], dtype=float)
    strongest_rms = float(np.max(rms_values))
    relative_rms = rms_values / strongest_rms if strongest_rms > 0.0 else np.zeros_like(rms_values)
    sensitivities = tuple(
        WarmupStageSensitivity(name, float(rms), float(np.max(np.abs(column))), float(relative))
        for name, column, rms, relative in zip(ALLOWED_CALIBRATION_PARAMETERS, columns, rms_values, relative_rms, strict=True)
    )
    norms = np.linalg.norm(jacobian, axis=0)
    normalized = np.zeros_like(jacobian)
    active = norms > 1.0e-12
    normalized[:, active] = jacobian[:, active] / norms[active]
    pairwise_cosine = normalized.T @ normalized
    np.fill_diagonal(pairwise_cosine, 1.0)
    singular_values = np.linalg.svd(normalized, compute_uv=False)
    largest = float(singular_values[0]) if singular_values.size else 0.0
    smallest = float(singular_values[-1]) if singular_values.size else 0.0
    normalized_singular_values = singular_values / largest if largest > 0.0 else np.zeros_like(singular_values)
    condition_number = float(largest / smallest) if smallest > 1.0e-12 else float("inf")
    numerical_rank = int(np.linalg.matrix_rank(normalized))
    off_diagonal = np.abs(pairwise_cosine - np.eye(pairwise_cosine.shape[0]))
    strongest_pairwise_cosine = float(np.max(off_diagonal)) if off_diagonal.size else 0.0
    weak_names = tuple(name for name, relative in zip(ALLOWED_CALIBRATION_PARAMETERS, relative_rms, strict=True) if float(relative) < weak_relative_rms_threshold)
    weakest_index = int(np.argmin(relative_rms))
    weakest_parameter = ALLOWED_CALIBRATION_PARAMETERS[weakest_index]
    weakest_relative = float(relative_rms[weakest_index])
    authorized = not weak_names
    note = (
        "Warm-up-stage practical-identifiability concern: at least one governed parameter is weakly excited relative to the strongest coolant-temperature sensitivity. Do not place all four parameters in one CAL-01 optimizer stage."
        if weak_names else
        "No parameter falls below the warm-up-stage relative-sensitivity heuristic. This still does not establish physical identifiability on Argonne data."
    )
    return WarmupStageIdentifiabilityDiagnostic(
        tuple(case.case_id for case in cases), tuple(ALLOWED_CALIBRATION_PARAMETERS), perturbation_fraction,
        int(jacobian.shape[0]), sensitivities, pairwise_cosine, singular_values, normalized_singular_values,
        numerical_rank, condition_number, weakest_parameter, weakest_relative, strongest_pairwise_cosine,
        weak_names, authorized, note,
    )
