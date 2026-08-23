from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from scipy.integrate import solve_ivp

from vtms_v1.constants import ABSOLUTE_ZERO_C, FLOW_EPS
from vtms_validation.dataset import ValidationDataset
from vtms_validation.metrics import calculate_metrics

from .simulation import M2SimulationRunner
from .stage_b import (
    FUEL_LHV_J_PER_KG,
    StageBCase,
    StageBRunResult,
    _project_engine_speed,
    evaluate_stage_b_acceptance,
    run_stage_b_case_reference,
)

try:
    from numba import njit
except ImportError:  # pragma: no cover - optional acceleration dependency
    njit = None


def _rhs_impl(
    time_s: float,
    state: np.ndarray,
    source_time_s: np.ndarray,
    engine_speed_rpm: np.ndarray,
    ambient_temp_c: np.ndarray,
    engine_heat_w: np.ndarray,
    head_thermal_capacitance_fraction: float,
    head_heat_fraction: float,
    head_block_ua_w_per_k: float,
    hot_coolant_capacitance_fraction: float,
    engine_thermal_capacitance_j_per_k: float,
    engine_coolant_ua_w_per_k: float,
    thermostat_open_c: float,
    thermostat_full_c: float,
    f_closed: float,
    f_open: float,
    gamma: float,
    eta_pack: float,
    radiator_ua_w_per_k: float,
    coolant_thermal_capacitance_j_per_k: float,
    coolant_cp_j_per_kg_k: float,
    engine_ambient_ua_w_per_k: float,
    pump_base_flow_kg_s: float,
    pump_slope_kg_s_per_rpm: float,
    pump_max_flow_kg_s: float,
    fan_start_c: float,
    fan_full_c: float,
    fan_max_vol_flow_m3_s: float,
    air_cp_j_per_kg_k: float,
    atmospheric_pressure_pa: float,
    air_gas_constant_j_per_kg_k: float,
    external_fan_capacity_m3_s: float,
    ags_static_restriction_factor: float,
    flow_eps: float,
) -> np.ndarray:
    head_temp_c = state[0]
    block_temp_c = state[1]
    hot_temp_c = state[2]
    cold_temp_c = state[3]

    rpm = np.interp(time_s, source_time_s, engine_speed_rpm)
    ambient = np.interp(time_s, source_time_s, ambient_temp_c)
    q_engine = np.interp(time_s, source_time_s, engine_heat_w)

    c_head = (
        head_thermal_capacitance_fraction * engine_thermal_capacitance_j_per_k
    )
    c_block = (
        (1.0 - head_thermal_capacitance_fraction)
        * engine_thermal_capacitance_j_per_k
    )
    c_hot = (
        hot_coolant_capacitance_fraction
        * coolant_thermal_capacitance_j_per_k
    )
    c_cold = (
        (1.0 - hot_coolant_capacitance_fraction)
        * coolant_thermal_capacitance_j_per_k
    )

    ua_head_cool = (
        head_thermal_capacitance_fraction * engine_coolant_ua_w_per_k
    )
    ua_block_cool = (
        (1.0 - head_thermal_capacitance_fraction)
        * engine_coolant_ua_w_per_k
    )
    ua_head_ambient = (
        head_thermal_capacitance_fraction * engine_ambient_ua_w_per_k
    )
    ua_block_ambient = (
        (1.0 - head_thermal_capacitance_fraction)
        * engine_ambient_ua_w_per_k
    )

    q_head = head_heat_fraction * q_engine
    q_block = (1.0 - head_heat_fraction) * q_engine
    q_head_cool = ua_head_cool * (head_temp_c - hot_temp_c)
    q_block_cool = ua_block_cool * (block_temp_c - hot_temp_c)
    q_head_block = head_block_ua_w_per_k * (head_temp_c - block_temp_c)
    q_head_ambient = ua_head_ambient * (head_temp_c - ambient)
    q_block_ambient = ua_block_ambient * (block_temp_c - ambient)

    if rpm == 0.0:
        pump_flow = 0.0
    else:
        nominal_pump = pump_base_flow_kg_s + pump_slope_kg_s_per_rpm * max(
            rpm - 800.0,
            0.0,
        )
        pump_flow = min(max(nominal_pump, 0.0), pump_max_flow_kg_s)

    thermostat_fraction = min(
        max(
            (hot_temp_c - thermostat_open_c)
            / (thermostat_full_c - thermostat_open_c),
            0.0,
        ),
        1.0,
    )
    radiator_fraction = f_closed + (
        f_open - f_closed
    ) * thermostat_fraction**gamma
    radiator_flow = radiator_fraction * pump_flow
    bypass_flow = pump_flow - radiator_flow

    fan_fraction = min(
        max(
            (hot_temp_c - fan_start_c) / (fan_full_c - fan_start_c),
            0.0,
        ),
        1.0,
    )
    air_density = atmospheric_pressure_pa / (
        air_gas_constant_j_per_kg_k * (ambient + 273.15)
    )
    external_core_vol_flow = (
        eta_pack
        * external_fan_capacity_m3_s
        * ags_static_restriction_factor
    )
    internal_fan_vol_flow = fan_fraction * fan_max_vol_flow_m3_s
    total_core_vol_flow = math.sqrt(
        external_core_vol_flow * external_core_vol_flow
        + internal_fan_vol_flow * internal_fan_vol_flow
    )
    air_flow = air_density * total_core_vol_flow

    c_cool_rate = radiator_flow * coolant_cp_j_per_kg_k
    c_air_rate = air_flow * air_cp_j_per_kg_k
    if c_cool_rate <= flow_eps or c_air_rate <= flow_eps:
        radiator_outlet_c = hot_temp_c
    else:
        c_min = min(c_cool_rate, c_air_rate)
        c_max = max(c_cool_rate, c_air_rate)
        capacity_ratio = c_min / c_max
        ntu = radiator_ua_w_per_k / c_min
        if ntu == 0.0:
            effectiveness = 0.0
        elif capacity_ratio <= flow_eps:
            effectiveness = min(max(1.0 - math.exp(-ntu), 0.0), 1.0)
        else:
            exponent = (ntu**0.22 / capacity_ratio) * (
                math.exp(-capacity_ratio * ntu**0.78) - 1.0
            )
            effectiveness = min(
                max(1.0 - math.exp(exponent), 0.0),
                1.0,
            )
        radiator_heat_w = (
            effectiveness * c_min * (hot_temp_c - ambient)
        )
        radiator_outlet_c = hot_temp_c - radiator_heat_w / c_cool_rate

    hot_advective_w = (
        pump_flow
        * coolant_cp_j_per_kg_k
        * (cold_temp_c - hot_temp_c)
    )
    radiator_return_w = (
        radiator_flow
        * coolant_cp_j_per_kg_k
        * (radiator_outlet_c - cold_temp_c)
    )
    bypass_return_w = (
        bypass_flow
        * coolant_cp_j_per_kg_k
        * (hot_temp_c - cold_temp_c)
    )

    result = np.empty(4, dtype=np.float64)
    result[0] = (
        q_head - q_head_cool - q_head_block - q_head_ambient
    ) / c_head
    result[1] = (
        q_block + q_head_block - q_block_cool - q_block_ambient
    ) / c_block
    result[2] = (
        q_head_cool + q_block_cool + hot_advective_w
    ) / c_hot
    result[3] = (
        radiator_return_w + bypass_return_w
    ) / c_cold
    return result


_rhs_numba = None if njit is None else njit(cache=True)(_rhs_impl)


def numba_available() -> bool:
    return _rhs_numba is not None


def _require_numba() -> None:
    if _rhs_numba is None:
        raise RuntimeError(
            "M2 Stage B acceleration requires the optional 'accelerate' dependency"
        )


def _fuel_energy_rate_w(dataset: ValidationDataset) -> np.ndarray:
    if dataset.fuel_energy_rate_w is not None:
        return np.asarray(dataset.fuel_energy_rate_w, dtype=float)
    if dataset.fuel_rate_kg_s is not None:
        return np.asarray(dataset.fuel_rate_kg_s, dtype=float) * FUEL_LHV_J_PER_KG
    raise ValueError("M2 Stage B requires direct fuel-rate or fuel-energy evidence")


def run_stage_b_case_accelerated(
    dataset: ValidationDataset,
    case: StageBCase,
    *,
    initial_head_offset_c: float = 0.0,
    initial_block_offset_c: float = 0.0,
    initial_cold_offset_c: float = 0.0,
) -> StageBRunResult:
    """Run one Stage B case with a compiled RHS and independent SciPy RK45.

    Compilation accelerates only RHS arithmetic. SciPy ``solve_ivp`` remains the
    integrator and every configuration receives its own adaptive RK45 controller.
    Equations, source interpolation order, output grid, and acceptance calculations
    are intentionally identical to ``run_stage_b_case_reference``.
    """

    _require_numba()
    dataset.validate()
    if float(np.min(dataset.ambient_temp_c)) <= ABSOLUTE_ZERO_C:
        raise ValueError("ambient temperature must be above absolute zero")

    parameters = case.parameters()
    parameters.validate()
    reference_rpm = _project_engine_speed(dataset.engine_speed_rpm)
    engine_heat_w = _fuel_energy_rate_w(dataset) * case.wall_heat_fraction
    initial_ect = float(dataset.measured_coolant_temp_c[0])
    output_times = M2SimulationRunner._output_times(dataset.duration_s, 1.0)

    assert _rhs_numba is not None

    def rhs(time_s: float, state: np.ndarray) -> np.ndarray:
        return _rhs_numba(
            time_s,
            state,
            dataset.time_s,
            reference_rpm,
            dataset.ambient_temp_c,
            engine_heat_w,
            case.head_thermal_capacitance_fraction,
            case.head_heat_fraction,
            case.head_block_ua_w_per_k,
            case.hot_coolant_capacitance_fraction,
            case.engine_thermal_capacitance_j_per_k,
            case.engine_coolant_ua_w_per_k,
            parameters.thermostat_open_c,
            case.thermostat_full_c,
            parameters.f_closed,
            case.f_open,
            case.gamma,
            case.eta_pack,
            case.radiator_ua_nominal_w_per_k,
            parameters.coolant_thermal_capacitance_j_per_k,
            parameters.coolant_cp_j_per_kg_k,
            parameters.engine_ambient_ua_w_per_k,
            parameters.pump_base_flow_kg_s,
            parameters.pump_slope_kg_s_per_rpm,
            parameters.pump_max_flow_kg_s,
            parameters.fan_start_c,
            parameters.fan_full_c,
            parameters.fan_max_vol_flow_m3_s,
            parameters.air_cp_j_per_kg_k,
            parameters.atmospheric_pressure_pa,
            parameters.air_gas_constant_j_per_kg_k,
            parameters.external_fan_capacity_m3_s,
            parameters.ags_static_restriction_factor,
            FLOW_EPS,
        )

    solution = solve_ivp(
        rhs,
        (0.0, dataset.duration_s),
        np.asarray(
            [
                initial_ect + initial_head_offset_c,
                initial_ect + initial_block_offset_c,
                initial_ect,
                initial_ect + initial_cold_offset_c,
            ],
            dtype=float,
        ),
        method="RK45",
        rtol=1.0e-6,
        atol=1.0e-8,
        max_step=1.0,
        t_eval=output_times,
    )
    if not solution.success:
        raise RuntimeError(f"accelerated M2 Stage B solve failed: {solution.message}")

    predicted = np.interp(dataset.time_s, solution.t, solution.y[2])
    measured = np.asarray(dataset.measured_coolant_temp_c, dtype=float)
    metrics = calculate_metrics(dataset.time_s, measured, predicted)
    acceptance = evaluate_stage_b_acceptance(
        dataset.time_s,
        measured,
        predicted,
        metrics,
    )
    return StageBRunResult(
        case=case,
        metrics=metrics,
        acceptance=acceptance,
        predicted_c=predicted,
    )


@dataclass(frozen=True)
class StageBAccelerationEquivalence:
    global_index: int
    initial_head_offset_c: float
    initial_block_offset_c: float
    initial_cold_offset_c: float
    max_abs_trace_error_c: float
    rms_trace_error_c: float
    reference_pass: bool
    accelerated_pass: bool
    equivalent: bool

    def to_dict(self) -> dict[str, int | float | bool]:
        return asdict(self)


def compare_stage_b_acceleration(
    dataset: ValidationDataset,
    case: StageBCase,
    *,
    initial_head_offset_c: float = 0.0,
    initial_block_offset_c: float = 0.0,
    initial_cold_offset_c: float = 0.0,
    trace_atol_c: float = 1.0e-9,
) -> StageBAccelerationEquivalence:
    if trace_atol_c <= 0.0:
        raise ValueError("trace_atol_c must be > 0")

    keyword_args = {
        "initial_head_offset_c": initial_head_offset_c,
        "initial_block_offset_c": initial_block_offset_c,
        "initial_cold_offset_c": initial_cold_offset_c,
    }
    reference = run_stage_b_case_reference(dataset, case, **keyword_args)
    accelerated = run_stage_b_case_accelerated(dataset, case, **keyword_args)
    delta = accelerated.predicted_c - reference.predicted_c
    max_abs = float(np.max(np.abs(delta)))
    rms = float(np.sqrt(np.mean(delta**2)))
    pass_match = reference.acceptance.passed == accelerated.acceptance.passed
    equivalent = bool(max_abs <= trace_atol_c and pass_match)
    return StageBAccelerationEquivalence(
        global_index=case.global_index,
        initial_head_offset_c=initial_head_offset_c,
        initial_block_offset_c=initial_block_offset_c,
        initial_cold_offset_c=initial_cold_offset_c,
        max_abs_trace_error_c=max_abs,
        rms_trace_error_c=rms,
        reference_pass=reference.acceptance.passed,
        accelerated_pass=accelerated.acceptance.passed,
        equivalent=equivalent,
    )
