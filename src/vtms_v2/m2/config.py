from __future__ import annotations

from dataclasses import asdict, dataclass

from vtms_v2.m1.config import M1Parameters


@dataclass(frozen=True)
class M2ModelMetadata:
    model_id: str = "VTMS-V2-M2"
    model_version: str = "0.1.0"
    equation_set: str = "EM-V2-M2"
    classification: str = "four-state dual-engine-storage model-form test"
    validation_status: str = "synthetic_verification_only_no_physical_calibration"
    digital_twin_status: str = "not_a_digital_twin"

    def snapshot(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class M2Parameters(M1Parameters):
    head_thermal_capacitance_fraction: float = 0.35
    head_heat_fraction: float = 0.70
    head_block_ua_w_per_k: float = 800.0

    def validate(self) -> None:
        super().validate()
        if not 0.15 <= self.head_thermal_capacitance_fraction <= 0.60:
            raise ValueError(
                "head_thermal_capacitance_fraction must be in [0.15, 0.60]"
            )
        if not 0.50 <= self.head_heat_fraction <= 0.95:
            raise ValueError("head_heat_fraction must be in [0.50, 0.95]")
        if not 100.0 <= self.head_block_ua_w_per_k <= 3000.0:
            raise ValueError("head_block_ua_w_per_k must be in [100, 3000] W/K")

    @property
    def head_thermal_capacitance_j_per_k(self) -> float:
        return (
            self.head_thermal_capacitance_fraction
            * self.engine_thermal_capacitance_j_per_k
        )

    @property
    def block_thermal_capacitance_j_per_k(self) -> float:
        return (
            (1.0 - self.head_thermal_capacitance_fraction)
            * self.engine_thermal_capacitance_j_per_k
        )

    @property
    def head_coolant_ua_w_per_k(self) -> float:
        return (
            self.head_thermal_capacitance_fraction
            * self.engine_coolant_ua_w_per_k
        )

    @property
    def block_coolant_ua_w_per_k(self) -> float:
        return (
            (1.0 - self.head_thermal_capacitance_fraction)
            * self.engine_coolant_ua_w_per_k
        )

    @property
    def head_ambient_ua_w_per_k(self) -> float:
        return (
            self.head_thermal_capacitance_fraction
            * self.engine_ambient_ua_w_per_k
        )

    @property
    def block_ambient_ua_w_per_k(self) -> float:
        return (
            (1.0 - self.head_thermal_capacitance_fraction)
            * self.engine_ambient_ua_w_per_k
        )

    @staticmethod
    def provenance() -> dict[str, str]:
        provenance = M1Parameters.provenance()
        provenance.update(
            {
                "head_thermal_capacitance_fraction": (
                    "ENGINEERING_TOPOLOGY_ASSUMPTION/M2-FROZEN-BOUND"
                ),
                "head_heat_fraction": (
                    "ENGINEERING_TOPOLOGY_ASSUMPTION/M2-FROZEN-BOUND"
                ),
                "head_block_ua_w_per_k": (
                    "ENGINEERING_TOPOLOGY_ASSUMPTION/M2-FROZEN-BOUND"
                ),
            }
        )
        return provenance
