import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from vtms_v1.verification import run_verification_suite

report = run_verification_suite()
out = Path("verification_report.json")
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({
    "verification_status": report["verification_status"],
    "check_count": len(report["checks"]),
    "report": str(out),
}, indent=2))
