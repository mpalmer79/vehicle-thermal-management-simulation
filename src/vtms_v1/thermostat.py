from __future__ import annotations

from .config import ModelParameters
from .types import ThermostatMode
from .utils import clip, validate_health


class ThermostatModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    def raw_opening(self, coolant_temp_c: float) -> float:
        span = self.parameters.thermostat_full_c - self.parameters.thermostat_open_c
        return clip((coolant_temp_c - self.parameters.thermostat_open_c) / span, 0.0, 1.0)

    def opening(
        self,
        coolant_temp_c: float,
        mode: ThermostatMode = ThermostatMode.NORMAL,
        health: float = 1.0,
    ) -> float:
        validate_health("thermostat_health", health)
        if mode is ThermostatMode.STUCK_CLOSED:
            return 0.0
        if mode is ThermostatMode.STUCK_OPEN:
            return 1.0
        return clip(self.raw_opening(coolant_temp_c) * health, 0.0, 1.0)

    @staticmethod
    def split_flow(total_flow_kg_s: float, opening: float) -> tuple[float, float]:
        if total_flow_kg_s < 0:
            raise ValueError("total_flow_kg_s must be >= 0")
        if not 0.0 <= opening <= 1.0:
            raise ValueError("opening must be in [0, 1]")
        radiator_flow = opening * total_flow_kg_s
        bypass_flow = (1.0 - opening) * total_flow_kg_s
        return radiator_flow, bypass_flow
