from dataclasses import replace

import numpy as np
import pytest

from vtms_v1.scenario import Scenario
from vtms_v2.m0.airflow import (
    AirflowBoundary,
    AirflowBoundaryClass,
    M0AirflowModel,
)
from vtms_v2.m0.config import M0Parameters
from vtms_v2.m0.hydraulics import M0HydraulicSplit
from vtms_v2.m0.identifiability import evaluate_m0_identifiability
from vtms_v2.m0.simulation import M0SimulationRunner
from vtms_v2.m0.thermostat import M0ThermostatModel


def test_m0_defaults_follow_frozen_governance() -> None:
    parameters = M0Parameters()
    parameters.validate()
    assert parameters.thermostat_open_c == pytest.approx(87.8)
    assert 97.0 <= parameters.thermostat_full_c <= 102.0
    assert 0.0 <= parameters.f_closed <= 0.05
    assert 0.85 <= parameters.f_open <= 1.0
    assert 0.50 <= parameters.gamma <= 2.0


def test_m0_rejects_thermostat_full_open_outside_frozen_envelope() -> None:
    with pytest.raises(ValueError, match="97..102"):
        replace(M0Parameters(), thermostat_full_c=105.0).validate()


def test_m0_thermostat_is_static_and_physically_anchored() -> None:
    parameters = M0Parameters(thermostat_full_c=100.0)
    thermostat = M0ThermostatModel(parameters)
    assert thermostat.opening(87.8) == pytest.approx(0.0)
    assert thermostat.opening(100.0) == pytest.approx(1.0)
    assert thermostat.opening((87.8 + 100.0) / 2.0) == pytest.approx(0.5)


def test_m0_hydraulic_split_conserves_mass_and_is_not_valve_identity() -> None:
    parameters = M0Parameters(f_closed=0.02, f_open=0.95, gamma=2.0)
    hydraulics = M0HydraulicSplit(parameters)
    position = 0.5
    fraction = hydraulics.radiator_fraction(position)
    assert fraction != pytest.approx(position)
    radiator, bypass = hydraulics.split_flow(1.2, position)
    assert radiator + bypass == pytest.approx(1.2)
    assert radiator >= 0.0
    assert bypass >= 0.0


def test_constant_external_fan_boundary_does_not_use_vehicle_speed() -> None:
    parameters = M0Parameters()
    airflow = M0AirflowModel(parameters)
    boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN,
        external_fan_vol_flow_m3_s=2.5,
    )
    slow = airflow.mass_flow_kg_s(
        boundary=boundary,
        time_s=0.0,
        vehicle_speed_m_s=0.0,
        ambient_temp_c=22.0,
        internal_fan_fraction=0.0,
    )
    fast = airflow.mass_flow_kg_s(
        boundary=boundary,
        time_s=0.0,
        vehicle_speed_m_s=35.0,
        ambient_temp_c=22.0,
        internal_fan_fraction=0.0,
    )
    assert fast == pytest.approx(slow)


def test_unknown_airflow_requires_explicit_uncertainty_surrogate() -> None:
    boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.UNKNOWN,
    )
    with pytest.raises(ValueError, match="uncertainty surrogate"):
        boundary.validate()


def test_measured_core_airflow_is_authoritative() -> None:
    parameters = M0Parameters()
    airflow = M0AirflowModel(parameters)
    boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.MEASURED_CORE_AIRFLOW,
        measured_core_air_mass_flow_kg_s=1.25,
    )
    actual = airflow.mass_flow_kg_s(
        boundary=boundary,
        time_s=0.0,
        vehicle_speed_m_s=30.0,
        ambient_temp_c=20.0,
        internal_fan_fraction=1.0,
    )
    assert actual == pytest.approx(1.25)


def test_m0_zero_input_equilibrium_and_energy_balance() -> None:
    scenario = Scenario(
        scenario_id="SYN-M0-EQUILIBRIUM",
        name="M0 zero input equilibrium",
        duration_s=60.0,
        ambient_temp_c=25.0,
        engine_speed_rpm=1000.0,
        effective_load=0.0,
        vehicle_speed_m_s=20.0,
        initial_engine_temp_c=25.0,
        initial_coolant_temp_c=25.0,
        engine_heat_override_w=0.0,
        output_interval_s=5.0,
    )
    boundary = AirflowBoundary(
        boundary_class=AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY,
        documented_core_vol_flow_m3_s=0.0,
    )
    result = M0SimulationRunner().run(
        scenario,
        airflow_boundary=boundary,
    )
    assert result.model_metadata["model_id"] == "VTMS-V2-M0"
    assert result.final_point().engine_structure_temp_c == pytest.approx(25.0)
    assert result.final_point().coolant_temp_c == pytest.approx(25.0)
    assert result.energy_balance.normalized_residual < 1.0e-12


def test_m0_identifiability_preflight_is_synthetic_and_well_formed() -> None:
    diagnostic = evaluate_m0_identifiability(
        parameter_names=("radiator_ua_nominal_w_per_k", "gamma"),
    )
    assert diagnostic.case_ids == (
        "SYN-M0-WARMUP",
        "SYN-M0-CONSTANT-FAN",
        "SYN-M0-SPEED-MATCHED",
    )
    assert diagnostic.sample_count > 100
    assert diagnostic.pairwise_cosine_matrix.shape == (2, 2)
    assert np.all(np.isfinite(diagnostic.pairwise_cosine_matrix))
    assert diagnostic.numerical_rank in {1, 2}
