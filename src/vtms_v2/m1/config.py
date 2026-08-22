from __future__ import annotations

from dataclasses import asdict, dataclass

from vtms_v2.m0.config import M0Parameters


@dataclass(frozen=True)
class M1ModelMetadata:
    model_id: str = "VTMS-V2-M1"
    model_version: str = "0.1.0"
    equation_set: str = "EM-V2-M1"
    classification: str = "three-state hot-cold coolant model-form test"
    validation_status: str = "synthetic_verification_only_no_physical_calibration"
    digital_twin_status: str = "not_a_digital_twin"

    def snapshot(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class M1Parameters(M0Parameters):
    hot_coolant_capacitance_fraction: float = 0.50

    def validate(self) -> None:
        super().validate()
        if not 0.10 <= self.hot_coolant_capacitance_fraction <= 0.90:
            raise ValueError("hot_coolant_capacitance_fraction must be in [0.10, 0.90]")

    @property
    def hot_coolant_capacitance_j_per_k(self) -> float:
        return self.hot_coolant_capacitance_fraction * self.coolant_thermal_capacitance_j_per_k

    @property
    def cold_coolant_capacitance_j_per_k(self) -> float:
        return (1.0 - self.hot_coolant_capacitance_fraction) * self.coolant_thermal_capacitance_j_per_k

    @staticmethod
    def provenance() -> dict[str, str]:
        provenance = M0Parameters.provenance()
        provenance["hot_coolant_capacitance_fraction"] = (
            "ENGINEERING_TOPOLOGY_ASSUMPTION/M1-SYNTHETIC-ONLY"
        )
        return provenance
