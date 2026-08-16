from __future__ import annotations

from .config import ModelParameters
from .utils import clip


class FanController:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    def command(self, coolant_temp_c: float, failed: bool = False) -> float:
        if failed:
            return 0.0
        span = self.parameters.fan_full_c - self.parameters.fan_start_c
        return clip((coolant_temp_c - self.parameters.fan_start_c) / span, 0.0, 1.0)
