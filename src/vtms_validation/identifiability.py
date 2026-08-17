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
from .synthetic import SyntheticCase, generate_synthetic_dataset


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


def _prediction(
    dataset,
    fingerprint,
    parameters: ModelParameters,
    initial_engine_temp_c: float,
) -> np.ndarray:
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


def evaluate_synthetic_identifiability(
    *,
    parameters: ModelParameters | None = None,
    perturbation_fraction: float = 0.05,
) -> IdentifiabilityDiagnostic:
    """Evaluate local coolant-trace sensitivity before any physical residual is opened.

    Central multiplicative finite differences approximate dT_c/d(log theta). Columns
    are normalized before SVD/correlation so the diagnostic measures parameter-shape
    collinearity rather than merely differing parameter units. This is a local numerical
    diagnostic, not a proof of structural identifiability.
    """

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
        lower.validate()
        upper.validate()

        y_minus = _prediction(dataset, fingerprint, lower, case.initial_engine_temp_c)
        y_plus = _prediction(dataset, fingerprint, upper, case.initial_engine_temp_c)
        delta_log = np.log(upper_value) - np.log(lower_value)
        column = (y_plus - y_minus) / delta_log
        columns.append(column)
        sensitivities.append(
            ParameterSensitivity(
                name=name,
                perturbation_fraction=perturbation_fraction,
                rms_log_sensitivity_c=float(np.sqrt(np.mean(column**2))),
                peak_abs_log_sensitivity_c=float(np.max(np.abs(column))),
            )
        )

    jacobian = np.column_stack(columns)
    norms = np.linalg.norm(jacobian, axis=0)
    if np.any(norms <= 1.0e-12):
        normalized = np.zeros_like(jacobian)
        for index, norm in enumerate(norms):
            if norm > 1.0e-12:
                normalized[:, index] = jacobian[:, index] / norm
    else:
        normalized = jacobian / norms

    correlation = normalized.T @ normalized
    np.fill_diagonal(correlation, 1.0)
    singular_values = np.linalg.svd(normalized, compute_uv=False)
    smallest = float(singular_values[-1]) if singular_values.size else 0.0
    condition_number = (
        float(singular_values[0] / smallest) if smallest > 1.0e-12 else float("inf")
    )
    off_diagonal = np.abs(correlation - np.eye(correlation.shape[0]))
    max_correlation = float(np.max(off_diagonal)) if off_diagonal.size else 0.0

    warning = bool(condition_number > 100.0 or max_correlation > 0.95 or np.any(norms <= 1.0e-12))
    note = (
        "WARNING: the four-parameter coolant-only fit shows strong local collinearity or weak excitation. "
        "Treat individual fitted values as non-unique unless additional observables or constraints resolve it."
        if warning
        else
        "No severe local collinearity was detected in this synthetic excitation case, but this does not prove "
        "structural or physical identifiability on Argonne data."
    )

    return IdentifiabilityDiagnostic(
        parameter_names=tuple(ALLOWED_CALIBRATION_PARAMETERS),
        sensitivities=tuple(sensitivities),
        correlation_matrix=correlation,
        singular_values=singular_values,
        normalized_jacobian_condition_number=condition_number,
        max_abs_parameter_correlation=max_correlation,
        warning=warning,
        note=note,
    )
