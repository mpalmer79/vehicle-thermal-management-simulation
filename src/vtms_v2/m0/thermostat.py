from __future__ import annotations

from vtms_v1.types import ThermostatMode
from vtms_v1.utils import clip, validate_health

from .config import M0Parameters


class M0ThermostatModel:
    """Static M0 thermostat law. No lag or hysteresis state is permitted in M0."""

    def __init__(self, parameters: M0Parameters) -> None:
        self.parameters = parameters

    def raw_opening(self, coolant_temp_c: float) -> float:
        span = self.parameters.thermostat_full_c - self.parameters.thermostat_open_c
        return clip(
            (coolant_temp_c - self.parameters.thermostat_open_c) / span,
            0.0,
            1.0,
        )

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
