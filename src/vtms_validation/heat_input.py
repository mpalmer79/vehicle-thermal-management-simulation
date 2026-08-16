from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MafStoichiometricHeatEstimator:
    """Secondary-evidence heat-input estimator for KIT plausibility work.

    This is intentionally not a measured fuel-rate channel. It assumes the
    measured MAF represents combustion air, gasoline is near stoichiometric,
    and a fixed lower heating value applies. It is inappropriate for formal
    calibration without additional evidence about lambda/enrichment.
    """

    stoich_air_fuel_mass_ratio: float = 14.7
    gasoline_lhv_j_per_kg: float = 43.7e6
    wall_heat_fraction: float = 0.28

    def fuel_rate_kg_s(self, maf_g_s: np.ndarray | float) -> np.ndarray | float:
        return np.asarray(maf_g_s) / 1000.0 / self.stoich_air_fuel_mass_ratio

    def engine_heat_w(self, maf_g_s: np.ndarray | float) -> np.ndarray | float:
        fuel = self.fuel_rate_kg_s(maf_g_s)
        return fuel * self.gasoline_lhv_j_per_kg * self.wall_heat_fraction

    def metadata(self) -> dict[str, object]:
        return {
            "method": "MAF_STOICHIOMETRIC_HEAT_ESTIMATE",
            "evidence_level": "secondary_plausibility_only",
            "stoich_air_fuel_mass_ratio": self.stoich_air_fuel_mass_ratio,
            "gasoline_lhv_j_per_kg": self.gasoline_lhv_j_per_kg,
            "wall_heat_fraction": self.wall_heat_fraction,
            "fuel_rate_status": "derived_not_measured",
            "limitations": [
                "assumes near-stoichiometric gasoline combustion",
                "does not observe commanded equivalence ratio or enrichment",
                "does not account for EGR or unmeasured air-path effects",
                "must not be reported as measured fuel consumption",
            ],
        }
