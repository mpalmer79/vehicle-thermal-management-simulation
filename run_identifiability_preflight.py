from __future__ import annotations

import json

from vtms_validation.identifiability import (
    evaluate_synthetic_identifiability,
    evaluate_warmup_stage_identifiability,
)
from vtms_validation.physical_bounds import (
    argonne_cal_01_bounds,
    argonne_cal_rad_01_bounds,
    argonne_physical_bound_rationales,
    argonne_preregistered_bounds,
)


if __name__ == "__main__":
    broad_diagnostic = evaluate_synthetic_identifiability()
    warmup_diagnostic = evaluate_warmup_stage_identifiability()
    payload = {
        "status": "pre_argonne_residual_preregistration",
        "physical_bounds": argonne_preregistered_bounds().as_dict(),
        "staged_bounds": {
            "CAL-01": argonne_cal_01_bounds().as_dict(),
            "CAL-RAD-01": argonne_cal_rad_01_bounds().as_dict(),
        },
        "bound_rationales": [item.__dict__ for item in argonne_physical_bound_rationales()],
        "broad_synthetic_identifiability": broad_diagnostic.as_dict(),
        "warmup_stage_identifiability": warmup_diagnostic.as_dict(),
        "disclaimer": (
            "No Argonne model residuals are used by this preflight. Both sensitivity diagnostics are synthetic. "
            "The broad diagnostic asks whether the model can create distinct parameter signatures under a deliberately "
            "rich excitation. The warm-up diagnostic asks whether the existing warm-up-style profiles materially excite "
            "all four parameters in one CAL-01 stage. Neither result is physical validation."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
