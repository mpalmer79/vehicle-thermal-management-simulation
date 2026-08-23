import json

from vtms_v2.rad_s0 import evaluate_rad_s0


report = evaluate_rad_s0()
print(json.dumps(report, indent=2, sort_keys=True))

verification = report["verification"]
identifiability = report["identifiability"]

if verification["status"] != "PASS":
    raise SystemExit("RAD-S0 numerical verification no longer matches the frozen PASS result")
if identifiability["status"] != "FAIL" or report["overall_status"] != "FAIL":
    raise SystemExit("RAD-S0 identifiability no longer matches the frozen governed FAIL result")
if identifiability["normalized_jacobian_condition_number"] <= 100.0:
    raise SystemExit("RAD-S0 frozen condition-number failure unexpectedly disappeared")
if identifiability["max_abs_pairwise_cosine_involving_n_air"] < 0.95:
    raise SystemExit("RAD-S0 frozen n_air collinearity failure unexpectedly disappeared")
