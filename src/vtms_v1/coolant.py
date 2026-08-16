from __future__ import annotations

from dataclasses import dataclass

from .config import ModelParameters


@dataclass(frozen=True)
class CoolantProperties:
    specific_heat_j_per_kg_k: float
    density_kg_per_m3: float

    @classmethod
    def from_parameters(cls, parameters: ModelParameters) -> "CoolantProperties":
        return cls(
            specific_heat_j_per_kg_k=parameters.coolant_cp_j_per_kg_k,
            density_kg_per_m3=parameters.coolant_density_kg_per_m3,
        )
