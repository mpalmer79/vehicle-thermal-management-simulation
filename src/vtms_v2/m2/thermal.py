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

from .config import M2Parameters


@dataclass(frozen=True)
class M2ComponentEvaluation:
    engine_heat_w: float
    head_heat_w: float
    block_heat_w: float
    head_to_coolant_w: float
    block_to_coolant_w: float
    head_block_w: float
    head_to_ambient_w: float
    block_to_ambient_w: float
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


class M2ThermalModel:
    def __init__(self, parameters: M2Parameters) -> None:
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
        head_temp_c: float,
        block_temp_c: float,
        hot_coolant_temp_c: float,
        cold_coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> M2ComponentEvaluation:
        p = self.parameters
        q_engine = self.engine.engine_heat_w(
            op.engine_speed_rpm,
            op.effective_load,
            op.engine_heat_override_w,
        )
        q_head = p.head_heat_fraction * q_engine
        q_block = (1.0 - p.head_heat_fraction) * q_engine

        q_hc = p.head_coolant_ua_w_per_k * (
            head_temp_c - hot_coolant_temp_c
        )
        q_bc = p.block_coolant_ua_w_per_k * (
            block_temp_c - hot_coolant_temp_c
        )
        q_hb = p.head_block_ua_w_per_k * (head_temp_c - block_temp_c)
        q_ha = p.head_ambient_ua_w_per_k * (
            head_temp_c - op.ambient_temp_c
        )
        q_ba = p.block_ambient_ua_w_per_k * (
            block_temp_c - op.ambient_temp_c
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

        return M2ComponentEvaluation(
            engine_heat_w=q_engine,
            head_heat_w=q_head,
            block_heat_w=q_block,
            head_to_coolant_w=q_hc,
            block_to_coolant_w=q_bc,
            head_block_w=q_hb,
            head_to_ambient_w=q_ha,
            block_to_ambient_w=q_ba,
            engine_to_coolant_w=q_hc + q_bc,
            engine_to_ambient_w=q_ha + q_ba,
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
        head_temp_c: float,
        block_temp_c: float,
        hot_coolant_temp_c: float,
        cold_coolant_temp_c: float,
        op: OperatingPoint,
        faults: FaultState,
        airflow_boundary: AirflowBoundary,
        *,
        time_s: float,
    ) -> tuple[float, float, float, float]:
        c = self.evaluate_components(
            head_temp_c,
            block_temp_c,
            hot_coolant_temp_c,
            cold_coolant_temp_c,
            op,
            faults,
            airflow_boundary,
            time_s=time_s,
        )
        p = self.parameters
        d_head = (
            c.head_heat_w
            - c.head_to_coolant_w
            - c.head_block_w
            - c.head_to_ambient_w
        ) / p.head_thermal_capacitance_j_per_k
        d_block = (
            c.block_heat_w
            + c.head_block_w
            - c.block_to_coolant_w
            - c.block_to_ambient_w
        ) / p.block_thermal_capacitance_j_per_k
        d_hot = (
            c.engine_to_coolant_w + c.hot_advective_w
        ) / p.hot_coolant_capacitance_j_per_k
        d_cold = (
            c.radiator_return_mixing_w + c.bypass_return_mixing_w
        ) / p.cold_coolant_capacitance_j_per_k
        return d_head, d_block, d_hot, d_cold
