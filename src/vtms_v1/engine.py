from __future__ import annotations

import math

import numpy as np

from .config import ModelParameters
from .utils import clip


REFERENCE_TORQUE_CURVE = np.array(
    [
        [700.0, 0.45],
        [800.0, 0.55],
        [1500.0, 0.85],
        [2500.0, 1.00],
        [3500.0, 0.98],
        [4500.0, 0.92],
        [5500.0, 0.83],
        [6500.0, 0.68],
    ],
    dtype=float,
)


class ReferenceEngineModel:
    def __init__(self, parameters: ModelParameters) -> None:
        self.parameters = parameters

    def torque_shape(self, rpm: float) -> float:
        if rpm == 0.0:
            return 0.0
        if not 700.0 <= rpm <= 6500.0:
            raise ValueError("rpm outside VTMS-V1 reference torque-curve domain")
        return float(np.interp(rpm, REFERENCE_TORQUE_CURVE[:, 0], REFERENCE_TORQUE_CURVE[:, 1]))

    def brake_efficiency(self, load: float) -> float:
        if not 0.0 <= load <= 1.0:
            raise ValueError("load must be in [0, 1]")
        return clip(0.18 + 0.16 * load, 0.18, 0.34)

    def brake_power_w(self, rpm: float, load: float) -> float:
        if rpm == 0.0:
            return 0.0
        if not 0.0 <= load <= 1.0:
            raise ValueError("load must be in [0, 1]")
        omega_rad_s = 2.0 * math.pi * rpm / 60.0
        torque_nm = self.parameters.peak_torque_nm * self.torque_shape(rpm) * load
        return torque_nm * omega_rad_s

    def engine_heat_w(self, rpm: float, load: float, override_w: float | None = None) -> float:
        if override_w is not None:
            return float(override_w)
        if rpm == 0.0:
            return 0.0
        brake_power = self.brake_power_w(rpm, load)
        eta_b = self.brake_efficiency(load)
        fuel_power = brake_power / eta_b
        return self.parameters.wall_heat_fraction * fuel_power
