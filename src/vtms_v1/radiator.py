from __future__ import annotations

import math

from .config import ModelParameters
from .constants import FLOW_EPS
from .types import RadiatorEvaluation
from .utils import clip, validate_health


class RadiatorModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    @staticmethod
    def crossflow_both_unmixed_effectiveness(ntu: float, capacity_ratio: float) -> float:
        if ntu < 0.0:
            raise ValueError("NTU must be >= 0")
        if not 0.0 <= capacity_ratio <= 1.0:
            raise ValueError("capacity_ratio must be in [0, 1]")
        if ntu == 0.0:
            return 0.0
        if capacity_ratio <= FLOW_EPS:
            return clip(1.0 - math.exp(-ntu), 0.0, 1.0)
        exponent = (ntu ** 0.22 / capacity_ratio) * (
            math.exp(-capacity_ratio * ntu ** 0.78) - 1.0
        )
        return clip(1.0 - math.exp(exponent), 0.0, 1.0)

    def evaluate(
        self,
        coolant_inlet_temp_c: float,
        ambient_temp_c: float,
        radiator_coolant_flow_kg_s: float,
        air_flow_kg_s: float,
        health: float = 1.0,
    ) -> RadiatorEvaluation:
        validate_health("radiator_health", health)
        if radiator_coolant_flow_kg_s < 0.0 or air_flow_kg_s < 0.0:
            raise ValueError("radiator and air mass flows must be >= 0")

        c_cool = radiator_coolant_flow_kg_s * self.parameters.coolant_cp_j_per_kg_k
        c_air = air_flow_kg_s * self.parameters.air_cp_j_per_kg_k

        if c_cool <= FLOW_EPS or c_air <= FLOW_EPS:
            return RadiatorEvaluation(
                heat_w=0.0,
                outlet_temp_c=None,
                effectiveness=0.0,
                ntu=0.0,
                capacity_ratio=None,
                coolant_capacity_rate_w_per_k=c_cool,
                air_capacity_rate_w_per_k=c_air,
                flow_active=False,
            )

        c_min = min(c_cool, c_air)
        c_max = max(c_cool, c_air)
        c_r = c_min / c_max
        ua_eff = health * self.parameters.radiator_ua_nominal_w_per_k
        ntu = ua_eff / c_min
        effectiveness = self.crossflow_both_unmixed_effectiveness(ntu, c_r)
        heat_w = effectiveness * c_min * (coolant_inlet_temp_c - ambient_temp_c)
        outlet_temp_c = coolant_inlet_temp_c - heat_w / c_cool

        return RadiatorEvaluation(
            heat_w=heat_w,
            outlet_temp_c=outlet_temp_c,
            effectiveness=effectiveness,
            ntu=ntu,
            capacity_ratio=c_r,
            coolant_capacity_rate_w_per_k=c_cool,
            air_capacity_rate_w_per_k=c_air,
            flow_active=True,
        )
