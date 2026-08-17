from __future__ import annotations

import json

from vtms_validation.identifiability import evaluate_synthetic_identifiability
from vtms_validation.physical_bounds import (
    argonne_physical_bound_rationales,
    argonne_preregistered_bounds,
)


if __name__ == "__main__":
    diagnostic = evaluate_synthetic_identifiability()
    payload = {
        "status": "pre_argonne_residual_preregistration",
        "physical_bounds": argonne_preregistered_bounds().as_dict(),
        "bound_rationales": [item.__dict__ for item in argonne_physical_bound_rationales()],
        "synthetic_identifiability": diagnostic.as_dict(),
        "disclaimer": (
            "No Argonne model residuals are used by this preflight. The sensitivity case is synthetic, "
            "and the identifiability result is a local numerical diagnostic rather than physical validation."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
