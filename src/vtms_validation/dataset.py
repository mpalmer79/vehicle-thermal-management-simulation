from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ValidationDataset:
    dataset_id: str
    source_name: str
    time_s: np.ndarray
    measured_coolant_temp_c: np.ndarray
    engine_speed_rpm: np.ndarray
    vehicle_speed_m_s: np.ndarray
    ambient_temp_c: np.ndarray
    mass_air_flow_g_s: np.ndarray | None = None
    fuel_rate_kg_s: np.ndarray | None = None
    fuel_energy_rate_w: np.ndarray | None = None
    engine_torque_nm: np.ndarray | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        arrays = {
            "time_s": self.time_s,
            "measured_coolant_temp_c": self.measured_coolant_temp_c,
            "engine_speed_rpm": self.engine_speed_rpm,
            "vehicle_speed_m_s": self.vehicle_speed_m_s,
            "ambient_temp_c": self.ambient_temp_c,
        }
        n = len(self.time_s)
        if n < 2:
            raise ValueError("validation dataset requires at least two samples")
        for name, values in arrays.items():
            if len(values) != n:
                raise ValueError(f"{name} length does not match time_s")
            if not np.all(np.isfinite(values)):
                raise ValueError(f"{name} contains non-finite values")
        if np.any(np.diff(self.time_s) <= 0):
            raise ValueError("time_s must be strictly increasing")
        if self.time_s[0] != 0.0:
            raise ValueError("time_s must start at zero")
        if np.any(self.vehicle_speed_m_s < 0):
            raise ValueError("vehicle speed must be nonnegative")
        if np.any(self.engine_speed_rpm < 0):
            raise ValueError("measured engine speed must be nonnegative")

        nonnegative_optional = {
            "mass_air_flow_g_s": self.mass_air_flow_g_s,
            "fuel_rate_kg_s": self.fuel_rate_kg_s,
            "fuel_energy_rate_w": self.fuel_energy_rate_w,
        }
        for optional_name, optional_values in nonnegative_optional.items():
            if optional_values is not None:
                if len(optional_values) != n:
                    raise ValueError(f"{optional_name} length does not match time_s")
                if not np.all(np.isfinite(optional_values)):
                    raise ValueError(f"{optional_name} contains non-finite values")
                if np.any(optional_values < 0):
                    raise ValueError(f"{optional_name} must be nonnegative")

        if self.engine_torque_nm is not None:
            if len(self.engine_torque_nm) != n:
                raise ValueError("engine_torque_nm length does not match time_s")
            if not np.all(np.isfinite(self.engine_torque_nm)):
                raise ValueError("engine_torque_nm contains non-finite values")

    @property
    def duration_s(self) -> float:
        return float(self.time_s[-1])

    def interp(self, values: np.ndarray, time_s: float) -> float:
        return float(np.interp(time_s, self.time_s, values))
