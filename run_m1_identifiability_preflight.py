from __future__ import annotations

import json

from vtms_v2.m1.config import M1Parameters
from vtms_v2.m1.identifiability import evaluate_m1_staged_identifiability


if __name__ == "__main__":
    parameters = M1Parameters()
    diagnostics = evaluate_m1_staged_identifiability(parameters=parameters)
    payload = {
        "status": "VTMS_V2_M1_SYNTHETIC_PREFIT_IDENTIFIABILITY",
        "physical_data_used": False,
        "physical_calibration_authorized": False,
        "reserved_blind_evidence_used": False,
        "parameter_snapshot": parameters.snapshot(),
        "diagnostics": {
            name: diagnostic.as_dict()
            for name, diagnostic in diagnostics.items()
        },
        "disclaimer": (
            "This preflight uses deterministic synthetic scenarios only. It tests "
            "whether the new M1 coolant-topology parameter has a distinguishable "
            "ECT signature relative to retained parameters. It is not calibration, "
            "physical validation, or authorization to inspect reserved blind evidence."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
