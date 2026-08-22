from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Callable

from vtms_v1.constants import ABSOLUTE_ZERO_C
from vtms_v1.utils import validate_health

from .config import M0Parameters

FloatProfile = float | Callable[[float], float]


class AirflowBoundaryClass(str, Enum):
    CONSTANT_SPEED_EXTERNAL_FAN = "CONSTANT_SPEED_EXTERNAL_FAN"
    SPEED_MATCHED_EXTERNAL_FAN = "SPEED_MATCHED_EXTERNAL_FAN"
    MEASURED_CORE_AIRFLOW = "MEASURED_CORE_AIRFLOW"
    OTHER_DOCUMENTED_BOUNDARY = "OTHER_DOCUMENTED_BOUNDARY"
    UNKNOWN = "UNKNOWN"


def _value(profile: FloatProfile, time_s: float) -> float:
    return float(profile(time_s) if callable(profile) else profile)


@dataclass(frozen=True)
class AirflowBoundary:
    boundary_class: AirflowBoundaryClass
    external_fan_vol_flow_m3_s: FloatProfile | None = None
    measured_core_air_mass_flow_kg_s: FloatProfile | None = None
    documented_core_vol_flow_m3_s: FloatProfile | None = None
    unknown_surrogate_core_vol_flow_m3_s: FloatProfile | None = None
    speed_match_gain: float = 1.0
    ags_restriction_factor: FloatProfile = 1.0
    hood_position: str | None = None
    source_note: str = ""

    def validate(self) -> None:
        if self.speed_match_gain < 0.0:
            raise ValueError("speed_match_gain must be >= 0")
        restriction = _value(self.ags_restriction_factor, 0.0)
        if not 0.0 < restriction <= 1.0:
            raise ValueError("ags_restriction_factor must be in (0, 1]")
        if self.boundary_class is AirflowBoundaryClass.MEASURED_CORE_AIRFLOW:
            if self.measured_core_air_mass_flow_kg_s is None:
                raise ValueError(
                    "MEASURED_CORE_AIRFLOW requires measured_core_air_mass_flow_kg_s"
                )
        if self.boundary_class is AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY:
            if self.documented_core_vol_flow_m3_s is None:
                raise ValueError(
                    "OTHER_DOCUMENTED_BOUNDARY requires documented_core_vol_flow_m3_s"
                )
        if self.boundary_class is AirflowBoundaryClass.UNKNOWN:
            if self.unknown_surrogate_core_vol_flow_m3_s is None:
                raise ValueError(
                    "UNKNOWN airflow may be simulated only with an explicit uncertainty surrogate"
                )

    def metadata(self) -> dict[str, object]:
        def printable(value: object) -> object:
            return "profile" if callable(value) else value

        return {
            "boundary_class": self.boundary_class.value,
            "external_fan_vol_flow_m3_s": printable(
                self.external_fan_vol_flow_m3_s
            ),
            "measured_core_air_mass_flow_kg_s": printable(
                self.measured_core_air_mass_flow_kg_s
            ),
            "documented_core_vol_flow_m3_s": printable(
                self.documented_core_vol_flow_m3_s
            ),
            "unknown_surrogate_core_vol_flow_m3_s": printable(
                self.unknown_surrogate_core_vol_flow_m3_s
            ),
            "speed_match_gain": self.speed_match_gain,
            "ags_restriction_factor": printable(self.ags_restriction_factor),
            "hood_position": self.hood_position,
            "source_note": self.source_note,
        }


class M0AirflowModel:
    def __init__(self, parameters: M0Parameters) -> None:
        self.parameters = parameters

    def air_density_kg_m3(self, ambient_temp_c: float) -> float:
        if ambient_temp_c <= ABSOLUTE_ZERO_C:
            raise ValueError("ambient temperature must be above absolute zero")
        absolute_temp_k = ambient_temp_c + 273.15
        return self.parameters.atmospheric_pressure_pa / (
            self.parameters.air_gas_constant_j_per_kg_k * absolute_temp_k
        )

    def internal_fan_vol_flow_m3_s(self, fan_fraction: float) -> float:
        if not 0.0 <= fan_fraction <= 1.0:
            raise ValueError("fan_fraction must be in [0, 1]")
        return fan_fraction * self.parameters.fan_max_vol_flow_m3_s

    def mass_flow_kg_s(
        self,
        *,
        boundary: AirflowBoundary,
        time_s: float,
        vehicle_speed_m_s: float,
        ambient_temp_c: float,
        internal_fan_fraction: float,
        health: float = 1.0,
    ) -> float:
        boundary.validate()
        validate_health("airflow_health", health)
        if vehicle_speed_m_s < 0.0:
            raise ValueError("vehicle_speed_m_s must be >= 0")

        density = self.air_density_kg_m3(ambient_temp_c)
        restriction = _value(boundary.ags_restriction_factor, time_s)
        if not 0.0 < restriction <= 1.0:
            raise ValueError(
                "time-varying ags_restriction_factor must be in (0, 1]"
            )

        if boundary.boundary_class is AirflowBoundaryClass.MEASURED_CORE_AIRFLOW:
            assert boundary.measured_core_air_mass_flow_kg_s is not None
            measured = _value(boundary.measured_core_air_mass_flow_kg_s, time_s)
            if measured < 0.0:
                raise ValueError("measured core air mass flow must be >= 0")
            return health * restriction * measured

        if boundary.boundary_class is AirflowBoundaryClass.CONSTANT_SPEED_EXTERNAL_FAN:
            external = (
                self.parameters.external_fan_capacity_m3_s
                if boundary.external_fan_vol_flow_m3_s is None
                else _value(boundary.external_fan_vol_flow_m3_s, time_s)
            )
            if external < 0.0:
                raise ValueError("external fan volume flow must be >= 0")
            base_core_vol = self.parameters.eta_pack * external
        elif boundary.boundary_class is AirflowBoundaryClass.SPEED_MATCHED_EXTERNAL_FAN:
            base_core_vol = (
                self.parameters.eta_pack
                * boundary.speed_match_gain
                * self.parameters.radiator_face_area_m2
                * vehicle_speed_m_s
            )
        elif boundary.boundary_class is AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY:
            assert boundary.documented_core_vol_flow_m3_s is not None
            base_core_vol = _value(boundary.documented_core_vol_flow_m3_s, time_s)
        else:
            assert boundary.unknown_surrogate_core_vol_flow_m3_s is not None
            base_core_vol = _value(
                boundary.unknown_surrogate_core_vol_flow_m3_s,
                time_s,
            )

        if base_core_vol < 0.0:
            raise ValueError("core volume flow must be >= 0")

        base_core_vol *= restriction * self.parameters.ags_static_restriction_factor
        internal_fan = self.internal_fan_vol_flow_m3_s(internal_fan_fraction)
        total_vol = math.sqrt(
            base_core_vol * base_core_vol + internal_fan * internal_fan
        )
        return health * density * total_vol
