from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vtms_v1.types import EnergyBalance, SolverDiagnostics


@dataclass(frozen=True)
class M1TimeSeriesPoint:
    time_s: float
    engine_structure_temp_c: float
    hot_coolant_temp_c: float
    cold_coolant_temp_c: float
    ect_predicted_c: float
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
class M1SimulationResult:
    model_metadata: dict[str, Any]
    scenario_metadata: dict[str, Any]
    parameter_snapshot: dict[str, Any]
    provenance_snapshot: dict[str, str]
    time_series: list[M1TimeSeriesPoint]
    events: list[dict[str, Any]]
    energy_balance: EnergyBalance
    warnings: list[str]
    solver_diagnostics: SolverDiagnostics

    def final_point(self) -> M1TimeSeriesPoint:
        return self.time_series[-1]
