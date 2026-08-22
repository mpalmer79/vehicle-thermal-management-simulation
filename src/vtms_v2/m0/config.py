from __future__ import annotations

from dataclasses import asdict, dataclass

from vtms_v1.config import ModelParameters as V1ModelParameters


@dataclass(frozen=True)
class M0ModelMetadata:
    model_id: str = "VTMS-V2-M0"
    model_version: str = "0.1.0"
    equation_set: str = "EM-V2-M0"
    classification: str = "corrected-control two-state falsification baseline"
    validation_status: str = "synthetic_verification_only_no_physical_calibration"
    digital_twin_status: str = "not_a_digital_twin"

    def snapshot(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class M0Parameters(V1ModelParameters):
    thermostat_open_c: float = 87.8
    thermostat_full_c: float = 99.5

    f_closed: float = 0.02
    f_open: float = 0.95
    gamma: float = 1.0

    eta_pack: float = 0.40
    external_fan_capacity_m3_s: float = 2.50
    ags_static_restriction_factor: float = 1.0

    def validate(self) -> None:
        super().validate()
        if not 97.0 <= self.thermostat_full_c <= 102.0:
            raise ValueError(
                "M0 thermostat_full_c must remain inside the frozen 97..102 C uncertainty envelope"
            )
        if not 0.0 <= self.f_closed <= 0.05:
            raise ValueError("f_closed must be in [0.00, 0.05]")
        if not 0.85 <= self.f_open <= 1.0:
            raise ValueError("f_open must be in [0.85, 1.00]")
        if self.f_open < self.f_closed:
            raise ValueError("f_open must be >= f_closed")
        if not 0.50 <= self.gamma <= 2.0:
            raise ValueError("gamma must be in [0.50, 2.00]")
        if not 0.0 < self.eta_pack <= 1.0:
            raise ValueError("eta_pack must be in (0, 1]")
        if self.external_fan_capacity_m3_s <= 0.0:
            raise ValueError("external_fan_capacity_m3_s must be > 0")
        if not 0.0 < self.ags_static_restriction_factor <= 1.0:
            raise ValueError("ags_static_restriction_factor must be in (0, 1]")

    @staticmethod
    def provenance() -> dict[str, str]:
        provenance = V1ModelParameters.provenance()
        provenance.update(
            {
                "thermostat_open_c": "SOURCED/FORD-MOTORCRAFT-190F-APPLICATION",
                "thermostat_full_c": "ENGINEERING_UNCERTAINTY/FROZEN_97_102_C",
                "f_closed": "ENGINEERING_BOUNDED/M0-H1-FREEZE",
                "f_open": "ENGINEERING_BOUNDED/M0-H1-FREEZE",
                "gamma": "ENGINEERING_BOUNDED/M0-H1-FREEZE",
                "eta_pack": "ENGINEERING_BOUNDED/PRE-FIT-IDENTIFIABILITY",
                "external_fan_capacity_m3_s": "ARGONNE_PROTOCOL_CAPACITY_NOT_CORE_FLOW",
                "ags_static_restriction_factor": "UNCERTAINTY_CASE/AGS_STATUS_UNRESOLVED",
            }
        )
        return provenance
