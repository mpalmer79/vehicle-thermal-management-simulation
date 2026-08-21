from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from vtms_validation.residual_diagnostics import analyze_residuals


def _read_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        columns: dict[str, list[float]] = {name: [] for name in reader.fieldnames}
        for row in reader:
            for name in reader.fieldnames:
                value = row.get(name)
                if value is None or value == "":
                    raise ValueError(f"missing value in column {name!r}")
                columns[name].append(float(value))
    return {name: np.asarray(values, dtype=float) for name, values in columns.items()}


def _optional(columns: dict[str, np.ndarray], name: str) -> np.ndarray | None:
    return columns.get(name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze an already-reconstructed VTMS-V1 comparison trace without "
            "fitting or modifying model parameters."
        )
    )
    parser.add_argument("comparison_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()

    columns = _read_csv(args.comparison_csv)
    required = {"measured_coolant_temp_c", "predicted_coolant_temp_c"}
    missing = sorted(required - columns.keys())
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    report = analyze_residuals(
        measured_coolant_temp_c=columns["measured_coolant_temp_c"],
        predicted_coolant_temp_c=columns["predicted_coolant_temp_c"],
        engine_speed_rpm=_optional(columns, "engine_speed_rpm"),
        vehicle_speed_m_s=_optional(columns, "vehicle_speed_m_s"),
        fuel_energy_rate_w=_optional(columns, "fuel_energy_rate_w"),
        engine_load_fraction=_optional(columns, "engine_load_fraction"),
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
