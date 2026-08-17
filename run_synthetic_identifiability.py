from __future__ import annotations

import json

from vtms_v1.config import ModelParameters
from vtms_validation.identifiability import analyze_synthetic_identifiability
from vtms_validation.synthetic import (
    _default_calibration_case,
    _default_holdout_case,
    generate_synthetic_dataset,
)


def main() -> None:
    parameters = ModelParameters()
    calibration, _ = generate_synthetic_dataset(_default_calibration_case(), parameters)
    holdout, _ = generate_synthetic_dataset(_default_holdout_case(), parameters)

    payload = {
        "purpose": (
            "Pre-Argonne local practical-identifiability diagnostic using synthetic operating profiles only. "
            "No Argonne model residual is loaded or evaluated."
        ),
        "calibration_profile": analyze_synthetic_identifiability(
            calibration,
            parameters=parameters,
        ).as_dict(),
        "holdout_profile": analyze_synthetic_identifiability(
            holdout,
            parameters=parameters,
        ).as_dict(),
        "combined_profiles": analyze_synthetic_identifiability(
            (calibration, holdout),
            parameters=parameters,
        ).as_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
