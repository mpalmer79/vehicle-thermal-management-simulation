from __future__ import annotations

import numpy as np
import pytest

from vtms_v1.scenario import OperatingPoint, Scenario
from vtms_v1.types import FaultState
from vtms_v2.m0.airflow import AirflowBoundary, AirflowBoundaryClass
from vtms_v2.m1 import M1Parameters, M1SimulationRunner
from vtms_v2.m2 import M2Parameters, M2SimulationRunner, M2ThermalModel


def _boundary() -> AirflowBoundary:
    return AirflowBoundary(
        boundary_class=AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY,
        documented_core_vol_flow_m3_s=0.60,
        source_note="synthetic M2 verification boundary",
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
        scenario_id="SYN-M2-VERIFY",
        name="Synthetic M2 verification",
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


def test_m2_engine_capacitance_and_conductance_partitions_preserve_totals() -> None:
    p = M2Parameters(head_thermal_capacitance_fraction=0.35)
    assert p.head_thermal_capacitance_j_per_k + p.block_thermal_capacitance_j_per_k == pytest.approx(
        p.engine_thermal_capacitance_j_per_k
    )
    assert p.head_coolant_ua_w_per_k + p.block_coolant_ua_w_per_k == pytest.approx(
        p.engine_coolant_ua_w_per_k
    )
    assert p.head_ambient_ua_w_per_k + p.block_ambient_ua_w_per_k == pytest.approx(
        p.engine_ambient_ua_w_per_k
    )


def test_m2_rejects_out_of_bound_topology_parameters() -> None:
    with pytest.raises(ValueError):
        M2Parameters(head_thermal_capacitance_fraction=0.10).validate()
    with pytest.raises(ValueError):
        M2Parameters(head_heat_fraction=0.99).validate()
    with pytest.raises(ValueError):
        M2Parameters(head_block_ua_w_per_k=50.0).validate()


def test_m2_continuous_energy_identity_and_mass_balance() -> None:
    p = M2Parameters()
    model = M2ThermalModel(p)
    c = model.evaluate_components(
        115.0,
        100.0,
        95.0,
        80.0,
        _op(),
        FaultState(),
        _boundary(),
        time_s=10.0,
    )
    d_head, d_block, d_hot, d_cold = model.rhs(
        115.0,
        100.0,
        95.0,
        80.0,
        _op(),
        FaultState(),
        _boundary(),
        time_s=10.0,
    )

    assert c.pump_flow_kg_s == pytest.approx(
        c.radiator_flow_kg_s + c.bypass_flow_kg_s,
        abs=1e-12,
    )
    assert c.head_heat_w + c.block_heat_w == pytest.approx(c.engine_heat_w)
    stored_rate = (
        p.head_thermal_capacitance_j_per_k * d_head
        + p.block_thermal_capacitance_j_per_k * d_block
        + p.hot_coolant_capacitance_j_per_k * d_hot
        + p.cold_coolant_capacitance_j_per_k * d_cold
    )
    external_rate = c.engine_heat_w - c.engine_to_ambient_w - c.radiator.heat_w
    assert stored_rate == pytest.approx(external_rate, rel=1e-12, abs=1e-8)


def test_m2_internal_head_block_exchange_is_conservative() -> None:
    p = M2Parameters()
    model = M2ThermalModel(p)
    c = model.evaluate_components(
        120.0,
        90.0,
        90.0,
        80.0,
        _op(),
        FaultState(),
        _boundary(),
        time_s=0.0,
    )
    assert c.head_block_w == pytest.approx(
        p.head_block_ua_w_per_k * 30.0
    )
    # Q_hb is removed from the head and added to the block in rhs.
    assert c.head_block_w > 0.0


def test_m2_exact_nested_collapse_matches_m1_ect() -> None:
    fraction = 0.55
    m2_parameters = M2Parameters(
        head_thermal_capacitance_fraction=fraction,
        head_heat_fraction=fraction,
        head_block_ua_w_per_k=800.0,
    )
    m1_parameters = M1Parameters()

    scenario = _scenario()
    m1 = M1SimulationRunner(m1_parameters).run(
        scenario,
        airflow_boundary=_boundary(),
        max_step_s=0.05,
        rtol=1e-9,
        atol=1e-11,
    )
    m2 = M2SimulationRunner(m2_parameters).run(
        scenario,
        airflow_boundary=_boundary(),
        max_step_s=0.05,
        rtol=1e-9,
        atol=1e-11,
    )

    m1_ect = np.array([point.ect_predicted_c for point in m1.time_series])
    m2_ect = np.array([point.ect_predicted_c for point in m2.time_series])
    m2_head = np.array([point.head_temp_c for point in m2.time_series])
    m2_block = np.array([point.block_temp_c for point in m2.time_series])

    assert np.max(np.abs(m2_head - m2_block)) < 1e-8
    assert np.max(np.abs(m2_ect - m1_ect)) < 1e-6


def test_m2_simulation_observes_hot_side_as_ect_and_is_deterministic() -> None:
    runner = M2SimulationRunner()
    first = runner.run(_scenario(), airflow_boundary=_boundary(), max_step_s=0.25)
    second = runner.run(_scenario(), airflow_boundary=_boundary(), max_step_s=0.25)

    first_hot = np.array([point.hot_coolant_temp_c for point in first.time_series])
    second_hot = np.array([point.hot_coolant_temp_c for point in second.time_series])
    first_ect = np.array([point.ect_predicted_c for point in first.time_series])
    assert np.allclose(first_hot, first_ect, rtol=0.0, atol=0.0)
    assert np.allclose(first_hot, second_hot, rtol=0.0, atol=1e-12)
    assert first.model_metadata["model_id"] == "VTMS-V2-M2"


def test_m2_integrated_energy_balance_is_small() -> None:
    result = M2SimulationRunner().run(
        _scenario(),
        airflow_boundary=_boundary(),
        max_step_s=0.10,
    )
    assert result.energy_balance.normalized_residual < 5e-4


def test_m2_explicit_hidden_initial_states_are_preserved() -> None:
    result = M2SimulationRunner().run(
        _scenario(),
        airflow_boundary=_boundary(),
        initial_head_temp_c=105.0,
        initial_block_temp_c=95.0,
        initial_cold_temp_c=70.0,
        max_step_s=0.25,
    )
    first = result.time_series[0]
    assert first.head_temp_c == pytest.approx(105.0)
    assert first.block_temp_c == pytest.approx(95.0)
    assert first.hot_coolant_temp_c == pytest.approx(80.0)
    assert first.cold_coolant_temp_c == pytest.approx(70.0)
    init = result.scenario_metadata["m2_initialization"]
    assert init["head_defaulted_to_scenario_engine"] is False
    assert init["block_defaulted_to_head"] is False
    assert init["cold_defaulted_to_hot"] is False
