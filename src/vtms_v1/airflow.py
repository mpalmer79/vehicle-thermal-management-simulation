from __future__ import annotations

import math

from .config import ModelParameters
from .constants import ABSOLUTE_ZERO_C
from .utils import validate_health


class AirflowModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    def air_density_kg_m3(self, ambient_temp_c: float) -> float:
        if ambient_temp_c <= ABSOLUTE_ZERO_C:
            raise ValueError("ambient temperature must be above absolute zero")
        absolute_temp_k = ambient_temp_c + 273.15
        return self.parameters.atmospheric_pressure_pa / (
            self.parameters.air_gas_constant_j_per_kg_k * absolute_temp_k
        )

    def ram_vol_flow_m3_s(self, vehicle_speed_m_s: float) -> float:
        if vehicle_speed_m_s < 0:
            raise ValueError("vehicle_speed_m_s must be >= 0")
        return (
            self.parameters.ram_capture_coefficient
            * self.parameters.radiator_face_area_m2
            * vehicle_speed_m_s
        )

    def fan_vol_flow_m3_s(self, fan_fraction: float) -> float:
        if not 0.0 <= fan_fraction <= 1.0:
            raise ValueError("fan_fraction must be in [0, 1]")
        return fan_fraction * self.parameters.fan_max_vol_flow_m3_s

    def mass_flow_kg_s(
        self,
        vehicle_speed_m_s: float,
        ambient_temp_c: float,
        fan_fraction: float,
        health: float = 1.0,
    ) -> float:
        validate_health("airflow_health", health)
        ram = self.ram_vol_flow_m3_s(vehicle_speed_m_s)
        fan = self.fan_vol_flow_m3_s(fan_fraction)
        vol_flow = health * math.sqrt(ram * ram + fan * fan)
        return self.air_density_kg_m3(ambient_temp_c) * vol_flow
