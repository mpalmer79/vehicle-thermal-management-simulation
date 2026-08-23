from __future__ import annotations

from dataclasses import replace
import math

import numpy as np

from vtms_v1.constants import FLOW_EPS
from vtms_v1.radiator import RadiatorModel
from vtms_v1.scenario import Scenario
from vtms_v1.types import FaultState, RadiatorEvaluation
from vtms_v1.utils import validate_health

from .m0.airflow import AirflowBoundary, AirflowBoundaryClass
from .m0.config import M0Parameters
from .m0.simulation import M0SimulationRunner


RAD_S0_PARAMETER_NAMES = (
    "radiator_ua_nominal_w_per_k",
    "n_air",
    "eta_pack",
    "f_open",
    "gamma",
)


class RadUAAirflowRadiatorModel(RadiatorModel):
    """RAD-UA-A candidate used only for governed V2 development tests.

    The candidate changes only the effective radiator conductance law. The
    effectiveness-NTU heat-exchanger formulation and zero-flow behavior remain
    inherited from VTMS-V1.
    """

    def __init__(
        self,
        parameters: M0Parameters,
        *,
        n_air: float,
        air_mass_flow_reference_kg_s: float = 1.8,
    ) -> None:
        super().__init__(parameters)
        if not 0.0 <= n_air <= 1.0:
            raise ValueError("n_air must be in [0, 1]")
        if air_mass_flow_reference_kg_s <= 0.0:
            raise ValueError("air_mass_flow_reference_kg_s must be > 0")
        self.n_air = float(n_air)
        self.air_mass_flow_reference_kg_s = float(air_mass_flow_reference_kg_s)

    def ua_effective_w_per_k(self, air_flow_kg_s: float, health: float = 1.0) -> float:
        validate_health("radiator_health", health)
        if air_flow_kg_s < 0.0:
            raise ValueError("air_flow_kg_s must be >= 0")
        if air_flow_kg_s <= FLOW_EPS:
            return 0.0
        ratio = air_flow_kg_s / self.air_mass_flow_reference_kg_s
        return (
            health
            * self.parameters.radiator_ua_nominal_w_per_k
            * ratio ** self.n_air
        )

    def evaluate(
        self,
        coolant_inlet_temp_c: float,
        ambient_temp_c: float,
        radiator_coolant_flow_kg_s: float,
        air_flow_kg_s: float,
        health: float = 1.0,
    ) -> RadiatorEvaluation:
        validate_health("radiator_health", health)
        if radiator_coolant_flow_kg_s < 0.0 or air_flow_kg_s < 0.0:
            raise ValueError("radiator and air mass flows must be >= 0")

        c_cool = radiator_coolant_flow_kg_s * self.parameters.coolant_cp_j_per_kg_k
        c_air = air_flow_kg_s * self.parameters.air_cp_j_per_kg_k
        if c_cool <= FLOW_EPS or c_air <= FLOW_EPS:
            return RadiatorEvaluation(
                heat_w=0.0,
                outlet_temp_c=None,
                effectiveness=0.0,
                ntu=0.0,
                capacity_ratio=None,
                coolant_capacity_rate_w_per_k=c_cool,
                air_capacity_rate_w_per_k=c_air,
                flow_active=False,
            )

        c_min = min(c_cool, c_air)
        c_max = max(c_cool, c_air)
        c_r = c_min / c_max
        ua_eff = self.ua_effective_w_per_k(air_flow_kg_s, health)
        ntu = ua_eff / c_min
        effectiveness = self.crossflow_both_unmixed_effectiveness(ntu, c_r)
        heat_w = effectiveness * c_min * (coolant_inlet_temp_c - ambient_temp_c)
        outlet_temp_c = coolant_inlet_temp_c - heat_w / c_cool
        return RadiatorEvaluation(
            heat_w=heat_w,
            outlet_temp_c=outlet_temp_c,
            effectiveness=effectiveness,
            ntu=ntu,
            capacity_ratio=c_r,
            coolant_capacity_rate_w_per_k=c_cool,
            air_capacity_rate_w_per_k=c_air,
            flow_active=True,
        )


class RadS0SimulationRunner(M0SimulationRunner):
    def __init__(
        self,
        parameters: M0Parameters | None = None,
        *,
        n_air: float = 0.5,
        air_mass_flow_reference_kg_s: float = 1.8,
    ) -> None:
        super().__init__(parameters=parameters)
        self.n_air = float(n_air)
        self.air_mass_flow_reference_kg_s = float(air_mass_flow_reference_kg_s)
        self.thermal_model.radiator = RadUAAirflowRadiatorModel(
            self.parameters,
            n_air=self.n_air,
            air_mass_flow_reference_kg_s=self.air_mass_flow_reference_kg_s,
        )


def _piecewise(edges_s: tuple[float, ...], values: tuple[float, ...]):
    if len(edges_s) != len(values) + 1:
        raise ValueError("piecewise profile requires one more edge than values")

    def profile(time_s: float) -> float:
        index = int(np.searchsorted(np.asarray(edges_s[1:]), time_s, side="right"))
        return float(values[min(index, len(values) - 1)])

    return profile


def rad_s0_synthetic_scenario() -> tuple[Scenario, AirflowBoundary]:
    edges = (0.0, 150.0, 300.0, 450.0, 600.0, 750.0, 900.0)
    rpm = (1200.0, 2200.0, 3200.0, 1600.0, 2800.0, 1100.0)
    heat = (30000.0, 55000.0, 80000.0, 42000.0, 70000.0, 26000.0)
    external_air = (0.5, 1.5, 2.5, 0.8, 2.0, 1.0)
    scenario = Scenario(
        scenario_id="SYN-RAD-S0",
        name="RAD-S0 synthetic variable-UA identifiability excitation",
        duration_s=900.0,
        ambient_temp_c=24.0,
        engine_speed_rpm=_piecewise(edges, rpm),
        effective_load=0.0,
        vehicle_speed_m_s=0.0,
        initial_engine_temp_c=72.0,
        initial_coolant_temp_c=70.0,
        engine_heat_override_w=_piecewise(edges, heat),
        faults=FaultState(fan_failed=True),
        output_interval_s=5.0,
    )
    airflow = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN,
        external_fan_vol_flow_m3_s=_piecewise(edges, external_air),
        hood_position="synthetic_not_physical",
        source_note="RAD-S0 synthetic excitation only; no physical airflow evidence used.",
    )
    return scenario, airflow


def _reference_parameters() -> M0Parameters:
    return M0Parameters(
        thermostat_open_c=87.8,
        thermostat_full_c=99.5,
        f_closed=0.02,
        f_open=0.925,
        gamma=1.0,
        eta_pack=0.6,
        external_fan_capacity_m3_s=2.5,
        ags_static_restriction_factor=1.0,
        radiator_ua_nominal_w_per_k=1100.0,
    )


def _run_trace(
    parameters: M0Parameters,
    n_air: float,
    *,
    tight: bool = False,
):
    scenario, airflow = rad_s0_synthetic_scenario()
    runner = RadS0SimulationRunner(parameters, n_air=n_air)
    result = runner.run(
        scenario,
        airflow_boundary=airflow,
        rtol=1.0e-8 if tight else None,
        atol=1.0e-10 if tight else None,
        max_step_s=0.25 if tight else None,
    )
    trace = np.asarray([p.coolant_temp_c for p in result.time_series], dtype=float)
    return result, trace


def _component_verification(parameters: M0Parameters) -> dict[str, object]:
    variable = RadUAAirflowRadiatorModel(parameters, n_air=0.5)
    constant = RadiatorModel(parameters)

    zero_air = variable.evaluate(100.0, 25.0, 0.5, 0.0)
    zero_coolant = variable.evaluate(100.0, 25.0, 0.0, 1.8)
    zero_flow_pass = (
        zero_air.heat_w == 0.0
        and zero_air.outlet_temp_c is None
        and zero_coolant.heat_w == 0.0
        and zero_coolant.outlet_temp_c is None
    )

    ref_variable = variable.evaluate(100.0, 25.0, 0.5, 1.8)
    ref_constant = constant.evaluate(100.0, 25.0, 0.5, 1.8)
    reference_flow_error_w = abs(ref_variable.heat_w - ref_constant.heat_w)
    reference_flow_pass = reference_flow_error_w <= 1.0e-10

    collapse = RadUAAirflowRadiatorModel(parameters, n_air=0.0)
    collapse_errors = []
    for air_flow in (0.1, 0.3, 0.8, 1.8, 3.0):
        candidate = collapse.evaluate(100.0, 25.0, 0.5, air_flow)
        baseline = constant.evaluate(100.0, 25.0, 0.5, air_flow)
        collapse_errors.append(abs(candidate.heat_w - baseline.heat_w))
    collapse_max_error_w = float(max(collapse_errors))
    collapse_pass = collapse_max_error_w <= 1.0e-10

    heat_values = []
    effectiveness_values = []
    for air_flow in np.geomspace(0.05, 5.0, 40):
        evaluation = variable.evaluate(100.0, 25.0, 0.5, float(air_flow))
        heat_values.append(evaluation.heat_w)
        effectiveness_values.append(evaluation.effectiveness)
    monotonic_pass = bool(np.all(np.diff(np.asarray(heat_values)) >= -1.0e-9))
    effectiveness_pass = bool(
        np.all((np.asarray(effectiveness_values) >= 0.0) & (np.asarray(effectiveness_values) <= 1.0))
    )

    return {
        "zero_flow_pass": zero_flow_pass,
        "reference_flow_pass": reference_flow_pass,
        "reference_flow_heat_error_w": reference_flow_error_w,
        "n_air_zero_constant_ua_collapse_pass": collapse_pass,
        "n_air_zero_max_heat_error_w": collapse_max_error_w,
        "monotonic_heat_rejection_with_airflow_pass": monotonic_pass,
        "effectiveness_bounds_pass": effectiveness_pass,
    }


def evaluate_rad_s0(*, perturbation_fraction: float = 0.01) -> dict[str, object]:
    if not 0.001 <= perturbation_fraction <= 0.05:
        raise ValueError("perturbation_fraction must be in [0.001, 0.05]")

    baseline_parameters = _reference_parameters()
    baseline_parameters.validate()
    baseline_n = 0.5
    component = _component_verification(baseline_parameters)

    baseline_result, baseline_trace = _run_trace(baseline_parameters, baseline_n)
    repeat_result, repeat_trace = _run_trace(baseline_parameters, baseline_n)
    _, tight_trace = _run_trace(baseline_parameters, baseline_n, tight=True)

    deterministic_max_error_c = float(np.max(np.abs(baseline_trace - repeat_trace)))
    solver_delta = baseline_trace - tight_trace
    solver_noise_rms_c = float(np.sqrt(np.mean(solver_delta * solver_delta)))
    solver_noise_peak_c = float(np.max(np.abs(solver_delta)))
    energy_residual = float(baseline_result.energy_balance.normalized_residual)

    columns: list[np.ndarray] = []
    rms_sensitivities: list[float] = []
    peak_sensitivities: list[float] = []

    for name in RAD_S0_PARAMETER_NAMES:
        if name == "n_air":
            lower_n = baseline_n * (1.0 - perturbation_fraction)
            upper_n = baseline_n * (1.0 + perturbation_fraction)
            _, lower_trace = _run_trace(baseline_parameters, lower_n)
            _, upper_trace = _run_trace(baseline_parameters, upper_n)
        else:
            theta = float(getattr(baseline_parameters, name))
            lower_parameters = replace(
                baseline_parameters,
                **{name: theta * (1.0 - perturbation_fraction)},
            )
            upper_parameters = replace(
                baseline_parameters,
                **{name: theta * (1.0 + perturbation_fraction)},
            )
            lower_parameters.validate()
            upper_parameters.validate()
            _, lower_trace = _run_trace(lower_parameters, baseline_n)
            _, upper_trace = _run_trace(upper_parameters, baseline_n)
        column = (upper_trace - lower_trace) / (2.0 * perturbation_fraction)
        columns.append(column)
        rms_sensitivities.append(float(np.sqrt(np.mean(column * column))))
        peak_sensitivities.append(float(np.max(np.abs(column))))

    jacobian = np.column_stack(columns)
    norms = np.linalg.norm(jacobian, axis=0)
    active = norms > 1.0e-12
    normalized = np.zeros_like(jacobian)
    normalized[:, active] = jacobian[:, active] / norms[active]
    cosine = normalized.T @ normalized
    np.fill_diagonal(cosine, 1.0)
    singular_values = np.linalg.svd(normalized, compute_uv=False)
    smallest = float(singular_values[-1]) if singular_values.size else 0.0
    condition_number = (
        float(singular_values[0] / smallest)
        if smallest > 1.0e-12
        else float("inf")
    )

    strongest_rms = max(rms_sensitivities)
    relative_rms = [value / strongest_rms if strongest_rms > 0.0 else 0.0 for value in rms_sensitivities]
    n_index = RAD_S0_PARAMETER_NAMES.index("n_air")
    n_pairwise = [
        abs(float(cosine[n_index, index]))
        for index in range(len(RAD_S0_PARAMETER_NAMES))
        if index != n_index
    ]
    max_n_pairwise = max(n_pairwise)

    discrete: list[dict[str, object]] = []
    traces: dict[float, np.ndarray] = {}
    for n_air in (0.4, 0.5, 0.6):
        _, trace = _run_trace(baseline_parameters, n_air)
        traces[n_air] = trace
    rms_floor = max(0.02, 20.0 * solver_noise_rms_c)
    peak_floor = max(0.05, 20.0 * solver_noise_peak_c)
    for lower_n, upper_n in ((0.4, 0.5), (0.5, 0.6)):
        delta = traces[upper_n] - traces[lower_n]
        rms_delta = float(np.sqrt(np.mean(delta * delta)))
        peak_delta = float(np.max(np.abs(delta)))
        discrete.append(
            {
                "pair": [lower_n, upper_n],
                "rms_trace_separation_c": rms_delta,
                "peak_trace_separation_c": peak_delta,
                "rms_required_c": rms_floor,
                "peak_required_c": peak_floor,
                "pass": bool(rms_delta > rms_floor and peak_delta > peak_floor),
            }
        )

    identifiability_pass = bool(
        np.all(active)
        and condition_number <= 100.0
        and max_n_pairwise < 0.95
        and relative_rms[n_index] >= 0.02
        and all(item["pass"] for item in discrete)
    )
    verification_pass = bool(
        all(
            component[key]
            for key in (
                "zero_flow_pass",
                "reference_flow_pass",
                "n_air_zero_constant_ua_collapse_pass",
                "monotonic_heat_rejection_with_airflow_pass",
                "effectiveness_bounds_pass",
            )
        )
        and energy_residual <= 0.001
        and deterministic_max_error_c <= 1.0e-12
    )

    sensitivities = []
    for name, rms, peak, relative in zip(
        RAD_S0_PARAMETER_NAMES,
        rms_sensitivities,
        peak_sensitivities,
        relative_rms,
        strict=True,
    ):
        sensitivities.append(
            {
                "name": name,
                "rms_fractional_sensitivity_c": rms,
                "peak_abs_fractional_sensitivity_c": peak,
                "relative_rms_to_strongest": relative,
            }
        )

    return {
        "gate": "VTMS-V2-RAD-S0",
        "evidence_class": "synthetic_only_not_physical_evidence",
        "candidate": {
            "model": "RAD-UA-A",
            "baseline_n_air": baseline_n,
            "authorized_physical_exponents": [0.4, 0.5, 0.6],
            "ua_ref_w_per_k": baseline_parameters.radiator_ua_nominal_w_per_k,
            "air_mass_flow_reference_kg_s": 1.8,
        },
        "verification": {
            **component,
            "normalized_energy_residual": energy_residual,
            "deterministic_repeat_max_error_c": deterministic_max_error_c,
            "tight_vs_default_solver_noise_rms_c": solver_noise_rms_c,
            "tight_vs_default_solver_noise_peak_c": solver_noise_peak_c,
            "status": "PASS" if verification_pass else "FAIL",
        },
        "identifiability": {
            "parameter_names": list(RAD_S0_PARAMETER_NAMES),
            "perturbation_fraction": perturbation_fraction,
            "sensitivities": sensitivities,
            "pairwise_cosine_matrix": cosine.tolist(),
            "singular_values": singular_values.tolist(),
            "normalized_jacobian_condition_number": condition_number,
            "max_abs_pairwise_cosine_involving_n_air": max_n_pairwise,
            "n_air_relative_rms_to_strongest": relative_rms[n_index],
            "all_columns_active": bool(np.all(active)),
            "discrete_candidate_separation": discrete,
            "status": "PASS" if identifiability_pass else "FAIL",
        },
        "overall_status": "PASS" if verification_pass and identifiability_pass else "FAIL",
        "interpretation": (
            "RAD-UA-A passes the preregistered synthetic numerical and practical-identifiability gate. This authorizes only a separately frozen consumed-development feasibility test; it is not physical validation or Ford-specific exponent identification."
            if verification_pass and identifiability_pass
            else "RAD-UA-A fails at least one preregistered RAD-S0 requirement. Physical RAD-UA-A execution is blocked unless a new intervention is preregistered without using physical residuals to move the failed threshold."
        ),
    }
