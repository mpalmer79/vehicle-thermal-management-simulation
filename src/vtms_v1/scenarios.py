from __future__ import annotations

from .scenario import Scenario
from .types import FaultState, ThermostatMode


def canonical_scenarios() -> dict[str, Scenario]:
    base_hot_idle = dict(
        duration_s=1200.0,
        ambient_temp_c=40.0,
        engine_speed_rpm=1000.0,
        effective_load=0.25,
        vehicle_speed_m_s=0.0,
        initial_engine_temp_c=105.0,
        initial_coolant_temp_c=92.0,
    )
    base_high_load = dict(
        duration_s=1200.0,
        ambient_temp_c=35.0,
        engine_speed_rpm=3000.0,
        effective_load=0.55,
        vehicle_speed_m_s=15.0,
        initial_engine_temp_c=105.0,
        initial_coolant_temp_c=92.0,
    )
    return {
        "S-01": Scenario(
            scenario_id="S-01",
            name="Cold start / fast idle",
            duration_s=1200.0,
            ambient_temp_c=20.0,
            engine_speed_rpm=1200.0,
            effective_load=0.25,
            vehicle_speed_m_s=0.0,
            initial_engine_temp_c=20.0,
            initial_coolant_temp_c=20.0,
        ),
        "S-02": Scenario(
            scenario_id="S-02",
            name="Warm highway cruise",
            duration_s=900.0,
            ambient_temp_c=25.0,
            engine_speed_rpm=2500.0,
            effective_load=0.45,
            vehicle_speed_m_s=27.8,
            initial_engine_temp_c=105.0,
            initial_coolant_temp_c=92.0,
        ),
        "S-03": Scenario(scenario_id="S-03", name="Hot ambient idle", **base_hot_idle),
        "S-04": Scenario(scenario_id="S-04", name="Sustained higher load", **base_high_load),
        "S-05": Scenario(
            scenario_id="S-05",
            name="Fan failure at hot idle",
            faults=FaultState(fan_failed=True),
            **base_hot_idle,
        ),
        "S-06": Scenario(
            scenario_id="S-06",
            name="Thermostat stuck closed",
            faults=FaultState(thermostat_mode=ThermostatMode.STUCK_CLOSED),
            **base_hot_idle,
        ),
        "S-07": Scenario(
            scenario_id="S-07",
            name="50% pump degradation",
            faults=FaultState(pump_health=0.50),
            **base_high_load,
        ),
        "S-08": Scenario(
            scenario_id="S-08",
            name="40% radiator UA loss",
            faults=FaultState(radiator_health=0.60),
            **base_high_load,
        ),
        "S-09": Scenario(
            scenario_id="S-09",
            name="50% airflow restriction",
            faults=FaultState(airflow_health=0.50),
            **base_high_load,
        ),
    }
