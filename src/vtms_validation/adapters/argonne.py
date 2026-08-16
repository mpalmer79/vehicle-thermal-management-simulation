from __future__ import annotations

from pathlib import Path

from ..dataset import ValidationDataset


class ArgonneD3Adapter:
    """Contract placeholder until Argonne D3 raw files and channel dictionary arrive."""

    REQUIRED_LOGICAL_CHANNELS = (
        "time_s",
        "engine_coolant_temp_c",
        "engine_speed_rpm",
        "vehicle_speed_m_s",
        "ambient_temp_c",
    )

    PREFERRED_HEAT_CHANNELS = (
        "fuel_rate_kg_s",
        "fuel_energy_rate_w",
        "engine_torque_nm",
    )

    def load(self, path: str | Path) -> ValidationDataset:
        raise NotImplementedError(
            "Argonne D3 channel names/units are intentionally not guessed. "
            "Implement this mapping only after the D3 signal dictionary is received."
        )
