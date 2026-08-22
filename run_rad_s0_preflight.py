import json

from vtms_v2.rad_s0 import evaluate_rad_s0


report = evaluate_rad_s0()
print(json.dumps(report, indent=2, sort_keys=True))

if report["overall_status"] != "PASS":
    raise SystemExit(1)
