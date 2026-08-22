from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import numpy as np

from vtms_v2.m0.identifiability import synthetic_m0_cases

from .config import M2Parameters
from .simulation import M2SimulationRunner

M2_CANDIDATES = (
    "head_thermal_capacitance_fraction",
    "head_heat_fraction",
    "head_block_ua_w_per_k",
    "hot_coolant_capacitance_fraction",
    "engine_thermal_capacitance_j_per_k",
    "engine_coolant_ua_w_per_k",
)


@dataclass(frozen=True)
class M2ParameterSensitivity:
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
class M2IdentifiabilityDiagnostic:
    case_ids: tuple[str, ...]
    parameter_names: tuple[str, ...]
    perturbation_fraction: float
    sample_count: int
    sensitivities: tuple[M2ParameterSensitivity, ...]
    pairwise_cosine_matrix: np.ndarray
    singular_values: np.ndarray
    normalized_singular_values: np.ndarray
    numerical_rank: int
    normalized_jacobian_condition_number: float
    strongest_abs_pairwise_cosine: float
    weak_parameter_names: tuple[str, ...]
    simultaneous_fit_authorized: bool
    note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "case_ids": list(self.case_ids),
            "parameter_names": list(self.parameter_names),
            "perturbation_fraction": self.perturbation_fraction,
            "sample_count": self.sample_count,
            "sensitivities": [item.as_dict() for item in self.sensitivities],
            "pairwise_cosine_matrix": self.pairwise_cosine_matrix.tolist(),
            "singular_values": self.singular_values.tolist(),
            "normalized_singular_values": self.normalized_singular_values.tolist(),
            "numerical_rank": self.numerical_rank,
            "normalized_jacobian_condition_number": self.normalized_jacobian_condition_number,
            "strongest_abs_pairwise_cosine": self.strongest_abs_pairwise_cosine,
            "weak_parameter_names": list(self.weak_parameter_names),
            "simultaneous_fit_authorized": self.simultaneous_fit_authorized,
            "note": self.note,
        }


def _prediction(case, parameters: M2Parameters) -> np.ndarray:
    result = M2SimulationRunner(parameters).run(
        case.scenario,
        airflow_boundary=case.airflow_boundary,
    )
    return np.asarray(
        [point.ect_predicted_c for point in result.time_series],
        dtype=float,
    )


def _perturbed_values(
    parameters: M2Parameters,
    name: str,
    perturbation_fraction: float,
) -> tuple[float, float]:
    theta = float(getattr(parameters, name))
    if theta == 0.0:
        return theta - perturbation_fraction, theta + perturbation_fraction
    return (
        theta * (1.0 - perturbation_fraction),
        theta * (1.0 + perturbation_fraction),
    )


def evaluate_m2_identifiability(
    *,
    parameters: M2Parameters | None = None,
    parameter_names: Iterable[str] = M2_CANDIDATES,
    perturbation_fraction: float = 0.01,
    weak_relative_rms_threshold: float = 0.02,
    correlation_threshold: float = 0.95,
    condition_number_threshold: float = 100.0,
) -> M2IdentifiabilityDiagnostic:
    """Local practical-identifiability preflight using synthetic excitation only."""

    if not 0.001 <= perturbation_fraction <= 0.10:
        raise ValueError("perturbation_fraction must be in [0.001, 0.10]")
    if not 0.0 < weak_relative_rms_threshold < 1.0:
        raise ValueError("weak_relative_rms_threshold must be between 0 and 1")
    if not 0.0 < correlation_threshold < 1.0:
        raise ValueError("correlation_threshold must be between 0 and 1")
    if condition_number_threshold <= 1.0:
        raise ValueError("condition_number_threshold must exceed 1")

    baseline = parameters or M2Parameters()
    baseline.validate()
    names = tuple(parameter_names)
    if not names:
        raise ValueError("at least one parameter name is required")
    unknown = [name for name in names if name not in M2_CANDIDATES]
    if unknown:
        raise ValueError(f"unsupported M2 identifiability parameters: {unknown}")

    cases = synthetic_m0_cases()
    columns: list[np.ndarray] = []
    for name in names:
        low_value, high_value = _perturbed_values(
            baseline,
            name,
            perturbation_fraction,
        )
        low = replace(baseline, **{name: low_value})
        high = replace(baseline, **{name: high_value})
        low.validate()
        high.validate()
        blocks: list[np.ndarray] = []
        for case in cases:
            y_low = _prediction(case, low)
            y_high = _prediction(case, high)
            blocks.append(
                (y_high - y_low) / (2.0 * perturbation_fraction)
            )
        columns.append(np.concatenate(blocks))

    jacobian = np.column_stack(columns)
    rms_values = np.asarray(
        [np.sqrt(np.mean(column**2)) for column in columns],
        dtype=float,
    )
    strongest_rms = float(np.max(rms_values))
    relative_rms = (
        rms_values / strongest_rms
        if strongest_rms > 0.0
        else np.zeros_like(rms_values)
    )

    sensitivities = tuple(
        M2ParameterSensitivity(
            name=name,
            rms_fractional_sensitivity_c=float(rms),
            peak_abs_fractional_sensitivity_c=float(np.max(np.abs(column))),
            relative_rms_to_strongest=float(relative),
        )
        for name, column, rms, relative in zip(
            names,
            columns,
            rms_values,
            relative_rms,
            strict=True,
        )
    )

    norms = np.linalg.norm(jacobian, axis=0)
    active = norms > 1.0e-12
    normalized = np.zeros_like(jacobian)
    normalized[:, active] = jacobian[:, active] / norms[active]
    pairwise = normalized.T @ normalized
    np.fill_diagonal(pairwise, 1.0)

    singular_values = np.linalg.svd(normalized, compute_uv=False)
    largest = float(singular_values[0]) if singular_values.size else 0.0
    smallest = float(singular_values[-1]) if singular_values.size else 0.0
    normalized_singular_values = (
        singular_values / largest
        if largest > 0.0
        else np.zeros_like(singular_values)
    )
    condition_number = (
        float(largest / smallest)
        if smallest > 1.0e-12
        else float("inf")
    )
    numerical_rank = int(np.linalg.matrix_rank(normalized))

    off_diagonal = np.abs(pairwise - np.eye(pairwise.shape[0]))
    strongest_pairwise = (
        float(np.max(off_diagonal)) if off_diagonal.size else 0.0
    )
    weak_names = tuple(
        name
        for name, relative in zip(names, relative_rms, strict=True)
        if float(relative) < weak_relative_rms_threshold
    )

    authorized = bool(
        not weak_names
        and np.all(active)
        and strongest_pairwise <= correlation_threshold
        and condition_number <= condition_number_threshold
        and numerical_rank == len(names)
    )
    note = (
        "Synthetic M2 subset is locally distinguishable under the frozen "
        "excitation. This is mathematical preflight only and does not authorize "
        "physical calibration."
        if authorized
        else
        "Synthetic M2 identifiability warning. Reduce the physical fitting "
        "stage or independently constrain weak/correlated parameters."
    )

    return M2IdentifiabilityDiagnostic(
        case_ids=tuple(case.case_id for case in cases),
        parameter_names=names,
        perturbation_fraction=perturbation_fraction,
        sample_count=int(jacobian.shape[0]),
        sensitivities=sensitivities,
        pairwise_cosine_matrix=pairwise,
        singular_values=singular_values,
        normalized_singular_values=normalized_singular_values,
        numerical_rank=numerical_rank,
        normalized_jacobian_condition_number=condition_number,
        strongest_abs_pairwise_cosine=strongest_pairwise,
        weak_parameter_names=weak_names,
        simultaneous_fit_authorized=authorized,
        note=note,
    )


def evaluate_m2_staged_identifiability(
    *,
    parameters: M2Parameters | None = None,
) -> dict[str, M2IdentifiabilityDiagnostic]:
    baseline = parameters or M2Parameters()
    return {
        "new_topology": evaluate_m2_identifiability(
            parameters=baseline,
            parameter_names=(
                "head_thermal_capacitance_fraction",
                "head_heat_fraction",
                "head_block_ua_w_per_k",
            ),
        ),
        "topology_plus_total_storage": evaluate_m2_identifiability(
            parameters=baseline,
            parameter_names=(
                "head_thermal_capacitance_fraction",
                "head_heat_fraction",
                "head_block_ua_w_per_k",
                "engine_thermal_capacitance_j_per_k",
            ),
        ),
        "topology_plus_engine_coupling": evaluate_m2_identifiability(
            parameters=baseline,
            parameter_names=(
                "head_thermal_capacitance_fraction",
                "head_heat_fraction",
                "head_block_ua_w_per_k",
                "engine_coolant_ua_w_per_k",
            ),
        ),
        "m2_core": evaluate_m2_identifiability(
            parameters=baseline,
        ),
    }
