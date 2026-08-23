from __future__ import annotations

from dataclasses import dataclass

from vtms_v1.engine import ReferenceEngineModel
from vtms_v1.fan import FanController
from vtms_v1.pump import PumpModel
from vtms_v1.radiator import RadiatorModel
from vtms_v1.scenario import OperatingPoint
from vtms_v1.types import FaultState, RadiatorEvaluation

from .airflow import AirflowBoundary, M0AirflowModel
from .config import M0Parameters
from .hydraulics import M0HydraulicSplit
from .thermostat import M0ThermostatModel


@dataclass(frozen=True)
class M0ComponentEvaluation:
    engine_heat_w: float
    engine_to_coolant_w: float
    engine_to_ambient_w: float
    radiator: RadiatorEvaluation
    pump_flow_kg_s: float
    radiator_flow_kg_s: float
    bypass_flow_kg_s: float
    radiator_flow_fraction: float
    air_flow_kg_s: float
    thermostat_fraction: float
    fan_fraction: float


class M0ThermalModel:
    def __init__(self, parameters: M0Parameters) -> None:
        self.parameters = parameters
        self.engine = ReferenceEngineModel(parameters)
        self.pump = PumpModel(parameters)
        self.thermostat = M0ThermostatModel(parameters)
        self.hydraulics = M0HydraulicSplit(parameters)
        self.fan = FanController(parameters)
        self.airflow = M0AirflowModel(parameters)
        self.radiator = RadiatorModel(parameters)

    def evaluate_components(
        self,
        engine_temp_c: float,
        coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> M0ComponentEvaluation:
        q_engine = self.engine.engine_heat_w(
            op.engine_speed_rpm,
            op.effective_load,
            op.engine_heat_override_w,
        )
        q_ec = self.parameters.engine_coolant_ua_w_per_k * (
            engine_temp_c - coolant_temp_c
        )
        q_ea = self.parameters.engine_ambient_ua_w_per_k * (
            engine_temp_c - op.ambient_temp_c
        )

        pump_flow = self.pump.mass_flow_kg_s(
            op.engine_speed_rpm,
            faults.pump_health,
        )
        thermostat_fraction = self.thermostat.opening(
            coolant_temp_c,
            mode=faults.thermostat_mode,
            health=faults.thermostat_health,
        )
        radiator_fraction = self.hydraulics.radiator_fraction(
            thermostat_fraction
        )
        radiator_flow, bypass_flow = self.hydraulics.split_flow(
            pump_flow,
            thermostat_fraction,
        )

        fan_fraction = self.fan.command(coolant_temp_c, faults.fan_failed)
        air_flow = self.airflow.mass_flow_kg_s(
            boundary=airflow_boundary,
            time_s=time_s,
            vehicle_speed_m_s=op.vehicle_speed_m_s,
            ambient_temp_c=op.ambient_temp_c,
            internal_fan_fraction=fan_fraction,
            health=faults.airflow_health,
        )
        radiator = self.radiator.evaluate(
            coolant_temp_c,
            op.ambient_temp_c,
            radiator_flow,
            air_flow,
            faults.radiator_health,
        )

        return M0ComponentEvaluation(
            engine_heat_w=q_engine,
            engine_to_coolant_w=q_ec,
            engine_to_ambient_w=q_ea,
            radiator=radiator,
            pump_flow_kg_s=pump_flow,
            radiator_flow_kg_s=radiator_flow,
            bypass_flow_kg_s=bypass_flow,
            radiator_flow_fraction=radiator_fraction,
            air_flow_kg_s=air_flow,
            thermostat_fraction=thermostat_fraction,
            fan_fraction=fan_fraction,
        )

    def rhs(
        self,
        engine_temp_c: float,
        coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> tuple[float, float]:
        c = self.evaluate_components(
            engine_temp_c,
            coolant_temp_c,
            op,
            faults,
            airflow_boundary,
            time_s=time_s,
        )
        d_engine = (
            c.engine_heat_w
            - c.engine_to_coolant_w
            - c.engine_to_ambient_w
        ) / self.parameters.engine_thermal_capacitance_j_per_k
        d_coolant = (
            c.engine_to_coolant_w - c.radiator.heat_w
        ) / self.parameters.coolant_thermal_capacitance_j_per_k
        return d_engine, d_coolant
