from __future__ import annotations

from dataclasses import dataclass

from vtms_v1.engine import ReferenceEngineModel
from vtms_v1.fan import FanController
from vtms_v1.pump import PumpModel
from vtms_v1.radiator import RadiatorModel
from vtms_v1.scenario import OperatingPoint
from vtms_v1.types import FaultState, RadiatorEvaluation
from vtms_v2.m0.airflow import AirflowBoundary, M0AirflowModel
from vtms_v2.m0.hydraulics import M0HydraulicSplit
from vtms_v2.m0.thermostat import M0ThermostatModel

from .config import M1Parameters


@dataclass(frozen=True)
class M1ComponentEvaluation:
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
    hot_advective_w: float
    radiator_return_mixing_w: float
    bypass_return_mixing_w: float


class M1ThermalModel:
    def __init__(self, parameters: M1Parameters) -> None:
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
        hot_coolant_temp_c: float,
        cold_coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> M1ComponentEvaluation:
        p = self.parameters
        q_engine = self.engine.engine_heat_w(
            op.engine_speed_rpm,
            op.effective_load,
            op.engine_heat_override_w,
        )
        q_ec = p.engine_coolant_ua_w_per_k * (
            engine_temp_c - hot_coolant_temp_c
        )
        q_ea = p.engine_ambient_ua_w_per_k * (
            engine_temp_c - op.ambient_temp_c
        )

        pump_flow = self.pump.mass_flow_kg_s(
            op.engine_speed_rpm,
            faults.pump_health,
        )
        thermostat_fraction = self.thermostat.opening(
            hot_coolant_temp_c,
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

        fan_fraction = self.fan.command(
            hot_coolant_temp_c,
            faults.fan_failed,
        )
        air_flow = self.airflow.mass_flow_kg_s(
            boundary=airflow_boundary,
            time_s=time_s,
            vehicle_speed_m_s=op.vehicle_speed_m_s,
            ambient_temp_c=op.ambient_temp_c,
            internal_fan_fraction=fan_fraction,
            health=faults.airflow_health,
        )
        radiator = self.radiator.evaluate(
            hot_coolant_temp_c,
            op.ambient_temp_c,
            radiator_flow,
            air_flow,
            faults.radiator_health,
        )

        cp = p.coolant_cp_j_per_kg_k
        hot_advective = pump_flow * cp * (
            cold_coolant_temp_c - hot_coolant_temp_c
        )
        radiator_outlet = (
            hot_coolant_temp_c
            if radiator.outlet_temp_c is None
            else radiator.outlet_temp_c
        )
        radiator_return_mixing = radiator_flow * cp * (
            radiator_outlet - cold_coolant_temp_c
        )
        bypass_return_mixing = bypass_flow * cp * (
            hot_coolant_temp_c - cold_coolant_temp_c
        )

        return M1ComponentEvaluation(
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
            hot_advective_w=hot_advective,
            radiator_return_mixing_w=radiator_return_mixing,
            bypass_return_mixing_w=bypass_return_mixing,
        )

    def rhs(
        self,
        engine_temp_c: float,
        hot_coolant_temp_c: float,
        cold_coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> tuple[float, float, float]:
        c = self.evaluate_components(
            engine_temp_c,
            hot_coolant_temp_c,
            cold_coolant_temp_c,
            op,
            faults,
            airflow_boundary,
            time_s=time_s,
        )
        p = self.parameters
        d_engine = (
            c.engine_heat_w
            - c.engine_to_coolant_w
            - c.engine_to_ambient_w
        ) / p.engine_thermal_capacitance_j_per_k
        d_hot = (
            c.engine_to_coolant_w + c.hot_advective_w
        ) / p.hot_coolant_capacitance_j_per_k
        d_cold = (
            c.radiator_return_mixing_w + c.bypass_return_mixing_w
        ) / p.cold_coolant_capacitance_j_per_k
        return d_engine, d_hot, d_cold
