from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ThermostatMode(str, Enum):
    NORMAL = "normal"
    STUCK_CLOSED = "stuck_closed"
    STUCK_OPEN = "stuck_open"


@dataclass(frozen=True)
class FaultState:
    fan_failed: bool = False
    thermostat_mode: ThermostatMode = ThermostatMode.NORMAL
    thermostat_health: float = 1.0
    pump_health: float = 1.0
    radiator_health: float = 1.0
    airflow_health: float = 1.0


@dataclass(frozen=True)
class RadiatorEvaluation:
    heat_w: float
    outlet_temp_c: float | None
    effectiveness: float
    ntu: float
    capacity_ratio: float | None
    coolant_capacity_rate_w_per_k: float
    air_capacity_rate_w_per_k: float
    flow_active: bool


@dataclass(frozen=True)
class TimeSeriesPoint:
    time_s: float
    engine_structure_temp_c: float
    coolant_temp_c: float
    radiator_outlet_temp_c: float | None
    engine_heat_w: float
    engine_to_coolant_w: float
    engine_to_ambient_w: float
    radiator_heat_w: float
    pump_flow_kg_s: float
    radiator_flow_kg_s: float
    bypass_flow_kg_s: float
    air_flow_kg_s: float
    thermostat_fraction: float
    fan_fraction: float
    radiator_effectiveness: float
    radiator_ntu: float


@dataclass(frozen=True)
class EnergyBalance:
    input_energy_j: float
    rejected_energy_j: float
    stored_energy_change_j: float
    residual_j: float
    normalized_residual: float


@dataclass(frozen=True)
class SolverDiagnostics:
    success: bool
    status: int
    message: str
    function_evaluations: int
    jacobian_evaluations: int
    lu_decompositions: int


@dataclass(frozen=True)
class SimulationResult:
    model_metadata: dict[str, Any]
    scenario_metadata: dict[str, Any]
    parameter_snapshot: dict[str, Any]
    provenance_snapshot: dict[str, str]
    time_series: list[TimeSeriesPoint]
    events: list[dict[str, Any]]
    energy_balance: EnergyBalance
    warnings: list[str]
    solver_diagnostics: SolverDiagnostics

    def final_point(self) -> TimeSeriesPoint:
        return self.time_series[-1]
