from __future__ import annotations

from .config import ModelParameters
from .utils import clip, validate_health


class PumpModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    def mass_flow_kg_s(self, rpm: float, health: float = 1.0) -> float:
        validate_health("pump_health", health)
        if rpm < 0:
            raise ValueError("rpm must be >= 0")
        if rpm == 0.0:
            return 0.0
        nominal = clip(
            self.parameters.pump_base_flow_kg_s
            + self.parameters.pump_slope_kg_s_per_rpm * max(rpm - 800.0, 0.0),
            0.0,
            self.parameters.pump_max_flow_kg_s,
        )
        return health * nominal
