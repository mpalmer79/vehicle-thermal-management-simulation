from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from vtms_v1.constants import ABSOLUTE_ZERO_C
from vtms_v1.scenario import Scenario
from vtms_v1.types import FaultState, ThermostatMode


class FaultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fan_failed: bool = False
    thermostat_mode: ThermostatMode = ThermostatMode.NORMAL
    thermostat_health: float = Field(default=1.0, ge=0.0, le=1.0)
    pump_health: float = Field(default=1.0, ge=0.0, le=1.0)
    radiator_health: float = Field(default=1.0, ge=0.0, le=1.0)
    airflow_health: float = Field(default=1.0, ge=0.0, le=1.0)

    def to_core(self) -> FaultState:
        return FaultState(
            fan_failed=self.fan_failed,
            thermostat_mode=self.thermostat_mode,
            thermostat_health=self.thermostat_health,
            pump_health=self.pump_health,
            radiator_health=self.radiator_health,
            airflow_health=self.airflow_health,
        )


class SimulationRequest(BaseModel):
    """Public UI-facing request translated into the frozen core Scenario contract."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str = Field(default="CUSTOM", min_length=1, max_length=64)
    name: str = Field(default="Custom simulation", min_length=1, max_length=120)
    duration_s: float = Field(gt=0.0, le=7200.0)
    ambient_temp_c: float = Field(gt=ABSOLUTE_ZERO_C)
    engine_speed_rpm: float = Field(ge=0.0, le=6500.0)
    effective_load_percent: float = Field(ge=0.0, le=100.0)
    vehicle_speed_kmh: float = Field(ge=0.0)
    initial_engine_temp_c: float = Field(gt=ABSOLUTE_ZERO_C)
    initial_coolant_temp_c: float = Field(gt=ABSOLUTE_ZERO_C)
    engine_heat_override_w: float | None = Field(default=None, ge=0.0)
    output_interval_s: float = Field(default=1.0, ge=1.0, le=10.0)
    faults: FaultRequest = Field(default_factory=FaultRequest)

    @field_validator("engine_speed_rpm")
    @classmethod
    def validate_reference_engine_speed(cls, value: float) -> float:
        if value != 0.0 and value < 700.0:
            raise ValueError("engine_speed_rpm must be 0 or within 700..6500 rpm")
        return value

    def to_core(self) -> Scenario:
        return Scenario(
            scenario_id=self.scenario_id,
            name=self.name,
            duration_s=self.duration_s,
            ambient_temp_c=self.ambient_temp_c,
            engine_speed_rpm=self.engine_speed_rpm,
            effective_load=self.effective_load_percent / 100.0,
            vehicle_speed_m_s=self.vehicle_speed_kmh / 3.6,
            initial_engine_temp_c=self.initial_engine_temp_c,
            initial_coolant_temp_c=self.initial_coolant_temp_c,
            engine_heat_override_w=self.engine_heat_override_w,
            faults=self.faults.to_core(),
            output_interval_s=self.output_interval_s,
        )


class SimulationResponse(BaseModel):
    run_id: str
    classification: Literal["computed_simulation"] = "computed_simulation"
    result: dict[str, Any]
