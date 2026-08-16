from __future__ import annotations

from dataclasses import dataclass

from .airflow import AirflowModel
from .config import ModelParameters
from .engine import ReferenceEngineModel
from .fan import FanController
from .pump import PumpModel
from .radiator import RadiatorModel
from .scenario import OperatingPoint
from .thermostat import ThermostatModel
from .types import FaultState, RadiatorEvaluation


@dataclass(frozen=True)
class ComponentEvaluation:
    engine_heat_w: float
    engine_to_coolant_w: float
    engine_to_ambient_w: float
    radiator: RadiatorEvaluation
    pump_flow_kg_s: float
    radiator_flow_kg_s: float
    bypass_flow_kg_s: float
    air_flow_kg_s: float
    thermostat_fraction: float
    fan_fraction: float


class ThermalModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters
        self.engine = ReferenceEngineModel(parameters)
        self.pump = PumpModel(parameters)
        self.thermostat = ThermostatModel(parameters)
        self.fan = FanController(parameters)
        self.airflow = AirflowModel(parameters)
        self.radiator = RadiatorModel(parameters)

    def evaluate_components(
        self,
        engine_temp_c: float,
        coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
    ) -> ComponentEvaluation:
        q_engine = self.engine.engine_heat_w(
            op.engine_speed_rpm,
            op.effective_load,
            op.engine_heat_override_w,
        )
        q_ec = self.parameters.engine_coolant_ua_w_per_k * (engine_temp_c - coolant_temp_c)
        q_ea = self.parameters.engine_ambient_ua_w_per_k * (engine_temp_c - op.ambient_temp_c)

        pump_flow = self.pump.mass_flow_kg_s(op.engine_speed_rpm, faults.pump_health)
        alpha = self.thermostat.opening(
            coolant_temp_c,
            mode=faults.thermostat_mode,
            health=faults.thermostat_health,
        )
        radiator_flow, bypass_flow = self.thermostat.split_flow(pump_flow, alpha)

        fan_fraction = self.fan.command(coolant_temp_c, faults.fan_failed)
        air_flow = self.airflow.mass_flow_kg_s(
            op.vehicle_speed_m_s,
            op.ambient_temp_c,
            fan_fraction,
            faults.airflow_health,
        )
        radiator = self.radiator.evaluate(
            coolant_temp_c,
            op.ambient_temp_c,
            radiator_flow,
            air_flow,
            faults.radiator_health,
        )
        return ComponentEvaluation(
            engine_heat_w=q_engine,
            engine_to_coolant_w=q_ec,
            engine_to_ambient_w=q_ea,
            radiator=radiator,
            pump_flow_kg_s=pump_flow,
            radiator_flow_kg_s=radiator_flow,
            bypass_flow_kg_s=bypass_flow,
            air_flow_kg_s=air_flow,
            thermostat_fraction=alpha,
            fan_fraction=fan_fraction,
        )

    def rhs(
        self,
        engine_temp_c: float,
        coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
    ) -> tuple[float, float]:
        c = self.evaluate_components(engine_temp_c, coolant_temp_c, op, faults)
        d_engine = (
            c.engine_heat_w - c.engine_to_coolant_w - c.engine_to_ambient_w
        ) / self.parameters.engine_thermal_capacitance_j_per_k
        d_coolant = (
            c.engine_to_coolant_w - c.radiator.heat_w
        ) / self.parameters.coolant_thermal_capacitance_j_per_k
        return d_engine, d_coolant
