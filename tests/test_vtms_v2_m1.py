from __future__ import annotations

import numpy as np
import pytest

from vtms_v1.scenario import OperatingPoint, Scenario
from vtms_v1.types import FaultState, ThermostatMode
from vtms_v2.m0.airflow import AirflowBoundary, AirflowBoundaryClass
from vtms_v2.m1 import M1Parameters, M1SimulationRunner, M1ThermalModel


def _boundary() -> AirflowBoundary:
    return AirflowBoundary(
        boundary_class=AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY,
        documented_core_vol_flow_m3_s=0.60,
        source_note="synthetic M1 verification boundary",
    )


def _op() -> OperatingPoint:
    return OperatingPoint(
        ambient_temp_c=25.0,
        engine_speed_rpm=2000.0,
        effective_load=0.5,
        vehicle_speed_m_s=10.0,
        engine_heat_override_w=30000.0,
    )


def _scenario() -> Scenario:
    return Scenario(
        scenario_id="SYN-M1-VERIFY",
        name="Synthetic M1 verification",
        duration_s=120.0,
        ambient_temp_c=25.0,
        engine_speed_rpm=2000.0,
        effective_load=0.5,
        vehicle_speed_m_s=10.0,
        initial_engine_temp_c=90.0,
        initial_coolant_temp_c=80.0,
        engine_heat_override_w=30000.0,
        output_interval_s=0.5,
    )


def test_m1_coolant_capacitance_partition_preserves_total() -> None:
    p = M1Parameters(hot_coolant_capacitance_fraction=0.35)
    assert p.hot_coolant_capacitance_j_per_k > 0.0
    assert p.cold_coolant_capacitance_j_per_k > 0.0
    assert p.hot_coolant_capacitance_j_per_k + p.cold_coolant_capacitance_j_per_k == pytest.approx(
        p.coolant_thermal_capacitance_j_per_k
    )


def test_m1_rejects_degenerate_capacitance_partition() -> None:
    with pytest.raises(ValueError):
        M1Parameters(hot_coolant_capacitance_fraction=0.0).validate()
    with pytest.raises(ValueError):
        M1Parameters(hot_coolant_capacitance_fraction=1.0).validate()


def test_m1_continuous_energy_identity_and_mass_balance() -> None:
    p = M1Parameters()
    model = M1ThermalModel(p)
    c = model.evaluate_components(105.0, 95.0, 80.0, _op(), FaultState(), _boundary(), time_s=10.0)
    d_engine, d_hot, d_cold = model.rhs(105.0, 95.0, 80.0, _op(), FaultState(), _boundary(), time_s=10.0)

    assert c.pump_flow_kg_s == pytest.approx(c.radiator_flow_kg_s + c.bypass_flow_kg_s, abs=1e-12)
    stored_rate = (
        p.engine_thermal_capacitance_j_per_k * d_engine
        + p.hot_coolant_capacitance_j_per_k * d_hot
        + p.cold_coolant_capacitance_j_per_k * d_cold
    )
    external_rate = c.engine_heat_w - c.engine_to_ambient_w - c.radiator.heat_w
    assert stored_rate == pytest.approx(external_rate, rel=1e-12, abs=1e-8)


def test_m1_closed_radiator_limit_has_no_radiator_heat() -> None:
    p = M1Parameters(f_closed=0.0)
    model = M1ThermalModel(p)
    faults = FaultState(thermostat_mode=ThermostatMode.STUCK_CLOSED)
    c = model.evaluate_components(105.0, 95.0, 80.0, _op(), faults, _boundary(), time_s=0.0)
    assert c.radiator_flow_kg_s == pytest.approx(0.0)
    assert c.bypass_flow_kg_s == pytest.approx(c.pump_flow_kg_s)
    assert c.radiator.heat_w == pytest.approx(0.0)


def test_m1_full_radiator_limit_preserves_flow() -> None:
    p = M1Parameters(f_open=1.0)
    model = M1ThermalModel(p)
    faults = FaultState(thermostat_mode=ThermostatMode.STUCK_OPEN)
    c = model.evaluate_components(105.0, 95.0, 80.0, _op(), faults, _boundary(), time_s=0.0)
    assert c.radiator_flow_kg_s == pytest.approx(c.pump_flow_kg_s)
    assert c.bypass_flow_kg_s == pytest.approx(0.0, abs=1e-12)


def test_m1_simulation_observes_hot_side_as_ect_and_is_deterministic() -> None:
    runner = M1SimulationRunner()
    first = runner.run(_scenario(), airflow_boundary=_boundary(), max_step_s=0.25)
    second = runner.run(_scenario(), airflow_boundary=_boundary(), max_step_s=0.25)

    first_hot = np.array([point.hot_coolant_temp_c for point in first.time_series])
    second_hot = np.array([point.hot_coolant_temp_c for point in second.time_series])
    first_ect = np.array([point.ect_predicted_c for point in first.time_series])
    assert np.allclose(first_hot, first_ect, rtol=0.0, atol=0.0)
    assert np.allclose(first_hot, second_hot, rtol=0.0, atol=1e-12)
    assert first.model_metadata["model_id"] == "VTMS-V2-M1"
    assert first.scenario_metadata["m1_initialization"]["cold_initial_defaulted_to_hot"] is True


def test_m1_integrated_energy_balance_is_small() -> None:
    result = M1SimulationRunner().run(_scenario(), airflow_boundary=_boundary(), max_step_s=0.10)
    assert result.energy_balance.normalized_residual < 5e-4


def test_m1_explicit_cold_initial_state_is_preserved() -> None:
    result = M1SimulationRunner().run(
        _scenario(),
        airflow_boundary=_boundary(),
        initial_cold_temp_c=70.0,
        max_step_s=0.25,
    )
    assert result.time_series[0].hot_coolant_temp_c == pytest.approx(80.0)
    assert result.time_series[0].cold_coolant_temp_c == pytest.approx(70.0)
    assert result.scenario_metadata["m1_initialization"]["cold_initial_defaulted_to_hot"] is False
