from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import (
    COOLANT_PROPERTY_SET,
    EQUATION_SET,
    MODEL_ID,
    MODEL_VERSION,
    PARAMETER_SET,
    REFERENCE_VEHICLE,
    VALIDATION_STATUS,
)


@dataclass(frozen=True)
class ModelMetadata:
    model_id: str = MODEL_ID
    model_version: str = MODEL_VERSION
    equation_set: str = EQUATION_SET
    reference_vehicle: str = REFERENCE_VEHICLE
    coolant_property_set: str = COOLANT_PROPERTY_SET
    parameter_set: str = PARAMETER_SET
    validation_status: str = VALIDATION_STATUS
    classification: str = "physics-based lumped-parameter transient thermal simulation"
    digital_twin_status: str = "not_a_digital_twin_in_v1"

    def snapshot(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ModelParameters:
    # P-001 through P-026 from Engineering Model Specification 1.0.0.
    coolant_cp_j_per_kg_k: float = 3690.0
    coolant_density_kg_per_m3: float = 1020.0
    coolant_volume_m3: float = 0.0065
    engine_thermal_capacitance_j_per_k: float = 50000.0
    engine_coolant_ua_w_per_k: float = 1000.0
    engine_ambient_ua_w_per_k: float = 12.0
    wall_heat_fraction: float = 0.28
    peak_torque_nm: float = 250.0
    thermostat_open_c: float = 88.0
    thermostat_full_c: float = 98.0
    fan_start_c: float = 96.0
    fan_full_c: float = 104.0
    radiator_ua_nominal_w_per_k: float = 1100.0
    radiator_face_area_m2: float = 0.45
    ram_capture_coefficient: float = 0.33
    fan_max_vol_flow_m3_s: float = 1.15
    air_cp_j_per_kg_k: float = 1006.0
    atmospheric_pressure_pa: float = 101325.0
    air_gas_constant_j_per_kg_k: float = 287.05
    pump_base_flow_kg_s: float = 0.18
    pump_slope_kg_s_per_rpm: float = 2.20e-4
    pump_max_flow_kg_s: float = 1.40
    solver_rtol: float = 1.0e-6
    solver_atol: float = 1.0e-8
    solver_max_step_s: float = 1.0

    @property
    def coolant_mass_kg(self) -> float:
        return self.coolant_density_kg_per_m3 * self.coolant_volume_m3

    @property
    def coolant_thermal_capacitance_j_per_k(self) -> float:
        return self.coolant_mass_kg * self.coolant_cp_j_per_kg_k

    def snapshot(self) -> dict[str, float]:
        data = asdict(self)
        data["coolant_mass_kg"] = self.coolant_mass_kg
        data["coolant_thermal_capacitance_j_per_k"] = self.coolant_thermal_capacitance_j_per_k
        return data

    @staticmethod
    def provenance() -> dict[str, str]:
        return {
            "coolant_cp_j_per_kg_k": "SOURCED/DERIVED",
            "coolant_density_kg_per_m3": "SOURCED/ROUNDED",
            "coolant_volume_m3": "ASSUMED",
            "engine_thermal_capacitance_j_per_k": "CALIBRATED",
            "engine_coolant_ua_w_per_k": "CALIBRATED",
            "engine_ambient_ua_w_per_k": "CALIBRATED",
            "wall_heat_fraction": "CALIBRATED",
            "peak_torque_nm": "ASSUMED",
            "thermostat_open_c": "ASSUMED",
            "thermostat_full_c": "ASSUMED",
            "fan_start_c": "ASSUMED",
            "fan_full_c": "ASSUMED",
            "radiator_ua_nominal_w_per_k": "CALIBRATED",
            "radiator_face_area_m2": "ASSUMED",
            "ram_capture_coefficient": "CALIBRATED",
            "fan_max_vol_flow_m3_s": "ASSUMED",
            "air_cp_j_per_kg_k": "STANDARD",
            "atmospheric_pressure_pa": "STANDARD",
            "air_gas_constant_j_per_kg_k": "STANDARD",
            "pump_base_flow_kg_s": "ASSUMED",
            "pump_slope_kg_s_per_rpm": "ASSUMED",
            "pump_max_flow_kg_s": "ASSUMED",
            "solver_rtol": "SPECIFICATION",
            "solver_atol": "SPECIFICATION",
            "solver_max_step_s": "SPECIFICATION",
            "coolant_mass_kg": "DERIVED",
            "coolant_thermal_capacitance_j_per_k": "DERIVED",
        }

    def validate(self) -> None:
        positive = {
            "coolant_cp_j_per_kg_k": self.coolant_cp_j_per_kg_k,
            "coolant_density_kg_per_m3": self.coolant_density_kg_per_m3,
            "coolant_volume_m3": self.coolant_volume_m3,
            "engine_thermal_capacitance_j_per_k": self.engine_thermal_capacitance_j_per_k,
            "engine_coolant_ua_w_per_k": self.engine_coolant_ua_w_per_k,
            "radiator_ua_nominal_w_per_k": self.radiator_ua_nominal_w_per_k,
            "radiator_face_area_m2": self.radiator_face_area_m2,
            "fan_max_vol_flow_m3_s": self.fan_max_vol_flow_m3_s,
            "air_cp_j_per_kg_k": self.air_cp_j_per_kg_k,
            "atmospheric_pressure_pa": self.atmospheric_pressure_pa,
            "air_gas_constant_j_per_kg_k": self.air_gas_constant_j_per_kg_k,
            "solver_rtol": self.solver_rtol,
            "solver_atol": self.solver_atol,
            "solver_max_step_s": self.solver_max_step_s,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be > 0, got {value}")
        if self.engine_ambient_ua_w_per_k < 0:
            raise ValueError("engine_ambient_ua_w_per_k must be >= 0")
        if not 0.0 <= self.wall_heat_fraction <= 1.0:
            raise ValueError("wall_heat_fraction must be in [0, 1]")
        if self.thermostat_full_c <= self.thermostat_open_c:
            raise ValueError("thermostat_full_c must exceed thermostat_open_c")
        if self.fan_full_c <= self.fan_start_c:
            raise ValueError("fan_full_c must exceed fan_start_c")
        if not 0.0 <= self.ram_capture_coefficient:
            raise ValueError("ram_capture_coefficient must be >= 0")
