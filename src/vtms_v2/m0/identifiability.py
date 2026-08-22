from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import numpy as np

from vtms_v1.scenario import Scenario

from .airflow import AirflowBoundary, AirflowBoundaryClass
from .config import M0Parameters
from .simulation import M0SimulationRunner

M0_HEAT_REJECTION_CANDIDATES = (
    "radiator_ua_nominal_w_per_k",
    "eta_pack",
    "f_closed",
    "f_open",
    "gamma",
)


@dataclass(frozen=True)
class M0SyntheticCase:
    case_id: str
    scenario: Scenario
    airflow_boundary: AirflowBoundary


@dataclass(frozen=True)
class M0ParameterSensitivity:
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
class M0IdentifiabilityDiagnostic:
    case_ids: tuple[str, ...]
    parameter_names: tuple[str, ...]
    perturbation_fraction: float
    sample_count: int
    sensitivities: tuple[M0ParameterSensitivity, ...]
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


def _piecewise(edges_s: tuple[float, ...], values: tuple[float, ...]):
    if len(edges_s) != len(values) + 1:
        raise ValueError(
            "piecewise edges must contain exactly one more value than segments"
        )

    def profile(time_s: float) -> float:
        for index, value in enumerate(values):
            if time_s < edges_s[index + 1]:
                return value
        return values[-1]

    return profile


def synthetic_m0_cases() -> tuple[M0SyntheticCase, ...]:
    """Deterministic synthetic excitation only. No Argonne measurements are read."""

    warm_edges = (0.0, 160.0, 320.0, 500.0, 700.0)
    warmup = Scenario(
        scenario_id="SYN-M0-WARMUP",
        name="Synthetic M0 thermostat crossing",
        duration_s=700.0,
        ambient_temp_c=22.0,
        engine_speed_rpm=_piecewise(
            warm_edges,
            (1100.0, 1900.0, 2600.0, 1600.0),
        ),
        effective_load=0.35,
        vehicle_speed_m_s=_piecewise(
            warm_edges,
            (0.0, 8.0, 22.0, 5.0),
        ),
        initial_engine_temp_c=35.0,
        initial_coolant_temp_c=32.0,
        engine_heat_override_w=_piecewise(
            warm_edges,
            (36000.0, 52000.0, 68000.0, 44000.0),
        ),
        output_interval_s=5.0,
    )
    warm_boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY,
        documented_core_vol_flow_m3_s=0.18,
        source_note="synthetic fixed core-flow excitation; no physical evidence",
    )

    fan_edges = (0.0, 180.0, 360.0, 540.0, 720.0)
    constant_fan = Scenario(
        scenario_id="SYN-M0-CONSTANT-FAN",
        name="Synthetic M0 constant external fan hot regulation",
        duration_s=720.0,
        ambient_temp_c=23.0,
        engine_speed_rpm=_piecewise(
            fan_edges,
            (1500.0, 2400.0, 3200.0, 1800.0),
        ),
        effective_load=0.40,
        vehicle_speed_m_s=_piecewise(
            fan_edges,
            (5.0, 25.0, 12.0, 30.0),
        ),
        initial_engine_temp_c=98.0,
        initial_coolant_temp_c=94.0,
        engine_heat_override_w=_piecewise(
            fan_edges,
            (50000.0, 72000.0, 58000.0, 66000.0),
        ),
        output_interval_s=5.0,
    )
    constant_boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN,
        external_fan_vol_flow_m3_s=2.50,
        hood_position="up",
        source_note="synthetic use of frozen external-fan capacity boundary",
    )

    speed_edges = (0.0, 150.0, 300.0, 450.0, 600.0)
    speed_matched = Scenario(
        scenario_id="SYN-M0-SPEED-MATCHED",
        name="Synthetic M0 speed-matched cooling excitation",
        duration_s=600.0,
        ambient_temp_c=25.0,
        engine_speed_rpm=_piecewise(
            speed_edges,
            (1200.0, 2200.0, 3600.0, 2000.0),
        ),
        effective_load=0.45,
        vehicle_speed_m_s=_piecewise(
            speed_edges,
            (3.0, 14.0, 32.0, 8.0),
        ),
        initial_engine_temp_c=90.0,
        initial_coolant_temp_c=86.0,
        engine_heat_override_w=_piecewise(
            speed_edges,
            (42000.0, 62000.0, 80000.0, 48000.0),
        ),
        output_interval_s=5.0,
    )
    speed_boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.SPEED_MATCHED_EXTERNAL_FAN,
        speed_match_gain=1.0,
        source_note="synthetic speed-matched excitation; no physical evidence",
    )

    return (
        M0SyntheticCase("SYN-M0-WARMUP", warmup, warm_boundary),
        M0SyntheticCase("SYN-M0-CONSTANT-FAN", constant_fan, constant_boundary),
        M0SyntheticCase("SYN-M0-SPEED-MATCHED", speed_matched, speed_boundary),
    )


def _prediction(
    case: M0SyntheticCase,
    parameters: M0Parameters,
) -> np.ndarray:
    result = M0SimulationRunner(parameters).run(
        case.scenario,
        airflow_boundary=case.airflow_boundary,
    )
    return np.asarray(
        [point.coolant_temp_c for point in result.time_series],
        dtype=float,
    )


def _perturbed_values(
    parameters: M0Parameters,
    name: str,
    perturbation_fraction: float,
) -> tuple[float, float]:
    theta = float(getattr(parameters, name))
    if theta == 0.0:
        absolute_step = perturbation_fraction
        return theta - absolute_step, theta + absolute_step
    return (
        theta * (1.0 - perturbation_fraction),
        theta * (1.0 + perturbation_fraction),
    )


def evaluate_m0_identifiability(
    *,
    parameters: M0Parameters | None = None,
    parameter_names: Iterable[str] = M0_HEAT_REJECTION_CANDIDATES,
    perturbation_fraction: float = 0.01,
    weak_relative_rms_threshold: float = 0.02,
    correlation_threshold: float = 0.95,
    condition_number_threshold: float = 100.0,
) -> M0IdentifiabilityDiagnostic:
    """Local practical-identifiability preflight using synthetic excitation only."""

    if not 0.001 <= perturbation_fraction <= 0.10:
        raise ValueError("perturbation_fraction must be in [0.001, 0.10]")
    if not 0.0 < weak_relative_rms_threshold < 1.0:
        raise ValueError("weak_relative_rms_threshold must be between 0 and 1")
    if not 0.0 < correlation_threshold < 1.0:
        raise ValueError("correlation_threshold must be between 0 and 1")
    if condition_number_threshold <= 1.0:
        raise ValueError("condition_number_threshold must exceed 1")

    baseline = parameters or M0Parameters()
    baseline.validate()
    names = tuple(parameter_names)
    if not names:
        raise ValueError("at least one parameter name is required")
    unknown = [
        name for name in names if name not in M0_HEAT_REJECTION_CANDIDATES
    ]
    if unknown:
        raise ValueError(
            f"unsupported M0 identifiability parameters: {unknown}"
        )

    cases = synthetic_m0_cases()
    columns: list[np.ndarray] = []

    for name in names:
        lower_value, upper_value = _perturbed_values(
            baseline,
            name,
            perturbation_fraction,
        )
        lower = replace(baseline, **{name: lower_value})
        upper = replace(baseline, **{name: upper_value})
        lower.validate()
        upper.validate()

        blocks: list[np.ndarray] = []
        for case in cases:
            y_minus = _prediction(case, lower)
            y_plus = _prediction(case, upper)
            blocks.append(
                (y_plus - y_minus) / (2.0 * perturbation_fraction)
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
        M0ParameterSensitivity(
            name=name,
            rms_fractional_sensitivity_c=float(rms),
            peak_abs_fractional_sensitivity_c=float(
                np.max(np.abs(column))
            ),
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
        "Synthetic M0 stage is locally distinguishable under the preregistered "
        "excitation. This authorizes only the mathematical subset, not physical "
        "calibration."
        if authorized
        else
        "Synthetic M0 identifiability warning. Do not fit this complete subset "
        "simultaneously to physical data; reduce the stage or independently "
        "constrain correlated/weak parameters."
    )

    return M0IdentifiabilityDiagnostic(
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


def evaluate_m0_staged_identifiability(
    *,
    parameters: M0Parameters | None = None,
) -> dict[str, M0IdentifiabilityDiagnostic]:
    baseline = parameters or M0Parameters()
    return {
        "all_heat_rejection_controls": evaluate_m0_identifiability(
            parameters=baseline,
        ),
        "radiator_air_pair": evaluate_m0_identifiability(
            parameters=baseline,
            parameter_names=(
                "radiator_ua_nominal_w_per_k",
                "eta_pack",
            ),
        ),
        "hydraulic_shape": evaluate_m0_identifiability(
            parameters=baseline,
            parameter_names=("f_closed", "f_open", "gamma"),
        ),
        "radiator_plus_gamma": evaluate_m0_identifiability(
            parameters=baseline,
            parameter_names=(
                "radiator_ua_nominal_w_per_k",
                "gamma",
            ),
        ),
    }
