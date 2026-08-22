from __future__ import annotations

from vtms_v1.utils import clip

from .config import M0Parameters


class M0HydraulicSplit:
    """Bounded static radiator/bypass split frozen for M0 falsification."""

    def __init__(self, parameters: M0Parameters) -> None:
        self.parameters = parameters

    def radiator_fraction(self, thermostat_position: float) -> float:
        if not 0.0 <= thermostat_position <= 1.0:
            raise ValueError("thermostat_position must be in [0, 1]")
        z = clip(thermostat_position, 0.0, 1.0)
        shaped = z ** self.parameters.gamma
        return self.parameters.f_closed + (
            self.parameters.f_open - self.parameters.f_closed
        ) * shaped

    def split_flow(
        self,
        total_flow_kg_s: float,
        thermostat_position: float,
    ) -> tuple[float, float]:
        if total_flow_kg_s < 0.0:
            raise ValueError("total_flow_kg_s must be >= 0")
        fraction = self.radiator_fraction(thermostat_position)
        radiator = fraction * total_flow_kg_s
        bypass = total_flow_kg_s - radiator
        return radiator, bypass
