from __future__ import annotations

import json

from vtms_validation.synthetic import run_synthetic_bounded_calibration_harness


def main() -> None:
    result = run_synthetic_bounded_calibration_harness()
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
