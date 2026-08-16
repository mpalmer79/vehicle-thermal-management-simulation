from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .constants import ABSOLUTE_ZERO_C
from .types import FaultState

FloatProfile = float | Callable[[float], float]
OptionalFloatProfile = float | None | Callable[[float], float | None]


def _value(profile: FloatProfile, time_s: float) -> float:
    return float(profile(time_s) if callable(profile) else profile)


def _optional_value(profile: OptionalFloatProfile, time_s: float) -> float | None:
    raw = profile(time_s) if callable(profile) else profile
    return None if raw is None else float(raw)


@dataclass(frozen=True)
class OperatingPoint:
    ambient_temp_c: float
    engine_speed_rpm: float
    effective_load: float
    vehicle_speed_m_s: float
    engine_heat_override_w: float | None = None


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    duration_s: float
    ambient_temp_c: FloatProfile
    engine_speed_rpm: FloatProfile
    effective_load: FloatProfile
    vehicle_speed_m_s: FloatProfile
    initial_engine_temp_c: float
    initial_coolant_temp_c: float
    engine_heat_override_w: OptionalFloatProfile = None
    faults: FaultState = FaultState()
    output_interval_s: float = 1.0

    def at(self, time_s: float) -> OperatingPoint:
        op = OperatingPoint(
            ambient_temp_c=_value(self.ambient_temp_c, time_s),
            engine_speed_rpm=_value(self.engine_speed_rpm, time_s),
            effective_load=_value(self.effective_load, time_s),
            vehicle_speed_m_s=_value(self.vehicle_speed_m_s, time_s),
            engine_heat_override_w=_optional_value(self.engine_heat_override_w, time_s),
        )
        self._validate_operating_point(op)
        return op

    def validate(self) -> None:
        if self.duration_s <= 0:
            raise ValueError("duration_s must be > 0")
        if self.output_interval_s <= 0:
            raise ValueError("output_interval_s must be > 0")
        if self.initial_engine_temp_c <= ABSOLUTE_ZERO_C:
            raise ValueError("initial_engine_temp_c is below absolute zero")
        if self.initial_coolant_temp_c <= ABSOLUTE_ZERO_C:
            raise ValueError("initial_coolant_temp_c is below absolute zero")
        self._validate_operating_point(self.at(0.0))
        self._validate_operating_point(self.at(self.duration_s))
        for name, value in {
            "thermostat_health": self.faults.thermostat_health,
            "pump_health": self.faults.pump_health,
            "radiator_health": self.faults.radiator_health,
            "airflow_health": self.faults.airflow_health,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")

    @staticmethod
    def _validate_operating_point(op: OperatingPoint) -> None:
        if op.ambient_temp_c <= ABSOLUTE_ZERO_C:
            raise ValueError("ambient_temp_c must be above absolute zero")
        if op.engine_speed_rpm != 0.0 and not 700.0 <= op.engine_speed_rpm <= 6500.0:
            raise ValueError("reference engine speed must be 0 or within 700..6500 rpm")
        if not 0.0 <= op.effective_load <= 1.0:
            raise ValueError("effective_load must be in [0, 1]")
        if op.vehicle_speed_m_s < 0.0:
            raise ValueError("vehicle_speed_m_s must be >= 0")

    def metadata(self) -> dict[str, object]:
        def printable(value: object) -> object:
            return "profile" if callable(value) else value

        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "duration_s": self.duration_s,
            "ambient_temp_c": printable(self.ambient_temp_c),
            "engine_speed_rpm": printable(self.engine_speed_rpm),
            "effective_load": printable(self.effective_load),
            "vehicle_speed_m_s": printable(self.vehicle_speed_m_s),
            "initial_engine_temp_c": self.initial_engine_temp_c,
            "initial_coolant_temp_c": self.initial_coolant_temp_c,
            "engine_heat_override_w": printable(self.engine_heat_override_w),
            "faults": {
                "fan_failed": self.faults.fan_failed,
                "thermostat_mode": self.faults.thermostat_mode.value,
                "thermostat_health": self.faults.thermostat_health,
                "pump_health": self.faults.pump_health,
                "radiator_health": self.faults.radiator_health,
                "airflow_health": self.faults.airflow_health,
            },
        }
