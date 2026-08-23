from __future__ import annotations

import json

from vtms_v2.m2.config import M2Parameters
from vtms_v2.m2.identifiability import evaluate_m2_staged_identifiability


if __name__ == "__main__":
    parameters = M2Parameters()
    diagnostics = evaluate_m2_staged_identifiability(parameters=parameters)
    payload = {
        "status": "VTMS_V2_M2_SYNTHETIC_PREFIT_IDENTIFIABILITY",
        "physical_data_used": False,
        "reserved_blind_evidence_used": False,
        "physical_calibration_authorized": False,
        "parameter_snapshot": parameters.snapshot(),
        "diagnostics": {
            name: diagnostic.as_dict()
            for name, diagnostic in diagnostics.items()
        },
        "disclaimer": (
            "This preflight uses deterministic synthetic scenarios only. It tests "
            "whether the M2 dual-engine-storage topology creates distinguishable "
            "ECT signatures relative to retained engine and coolant parameters. "
            "It is not calibration, physical validation, or authorization to "
            "inspect reserved blind evidence."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
