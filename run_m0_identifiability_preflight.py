from __future__ import annotations

import json

from vtms_v2.m0.config import M0Parameters
from vtms_v2.m0.identifiability import (
    evaluate_m0_identifiability,
    evaluate_m0_staged_identifiability,
)


if __name__ == "__main__":
    parameters = M0Parameters()
    diagnostics = evaluate_m0_staged_identifiability(parameters=parameters)
    diagnostics["hydraulic_open_shape"] = evaluate_m0_identifiability(
        parameters=parameters,
        parameter_names=("f_open", "gamma"),
    )
    payload = {
        "status": "VTMS_V2_M0_SYNTHETIC_PREFIT_IDENTIFIABILITY",
        "physical_data_used": False,
        "physical_calibration_authorized": False,
        "parameter_snapshot": parameters.snapshot(),
        "diagnostics": {
            name: diagnostic.as_dict()
            for name, diagnostic in diagnostics.items()
        },
        "disclaimer": (
            "This preflight uses deterministic synthetic scenarios only. It may "
            "authorize a mathematically distinguishable parameter subset for a "
            "future preregistered physical stage, but it is not calibration or "
            "physical validation and it does not inspect reserved blind evidence."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
