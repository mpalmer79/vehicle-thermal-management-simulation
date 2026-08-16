from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import numpy as np

from ..dataset import ValidationDataset

TIME = "Time"
COOLANT = "Engine Coolant Temperature [°C]"
RPM = "Engine RPM [RPM]"
SPEED = "Vehicle Speed Sensor [km/h]"
AMBIENT = "Ambient Air Temperature [°C]"
MAF = "Air Flow Rate from Mass Flow Sensor [g/s]"


def _parse_clock(value: str) -> float:
    dt = datetime.strptime(value.strip(), "%H:%M:%S.%f")
    return dt.hour * 3600.0 + dt.minute * 60.0 + dt.second + dt.microsecond / 1e6


def load_kit_csv(path: str | Path, *, dataset_id: str | None = None) -> ValidationDataset:
    """Load a KIT OBD-II CSV and synchronize asynchronous PID updates.

    OBD Auto Doctor rows can repeat the most recently observed PID values while
    individual PIDs update on different cycles. The source rows are retained in
    timestamp order, duplicates are collapsed to the last row at a timestamp,
    then values are sampled on the native source timestamps. Missing values are
    forward-filled only after each channel's first observation.
    """
    path = Path(path)
    rows: list[dict[str, str]] = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {TIME, COOLANT, RPM, SPEED, AMBIENT, MAF}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"KIT file is missing required columns: {sorted(missing)}")
        rows.extend(reader)
    if not rows:
        raise ValueError("KIT CSV has no data rows")

    clocks = np.array([_parse_clock(r[TIME]) for r in rows], dtype=float)
    for i in range(1, len(clocks)):
        if clocks[i] < clocks[i - 1]:
            clocks[i:] += 86400.0
    t = clocks - clocks[0]

    def numeric(column: str) -> np.ndarray:
        values = np.full(len(rows), np.nan, dtype=float)
        last = np.nan
        for i, row in enumerate(rows):
            raw = (row.get(column) or "").strip()
            if raw:
                try:
                    last = float(raw)
                except ValueError:
                    pass
            values[i] = last
        first_valid = np.flatnonzero(np.isfinite(values))
        if first_valid.size == 0:
            raise ValueError(f"KIT column has no numeric data: {column}")
        first = int(first_valid[0])
        if first > 0:
            values[:first] = values[first]
        return values

    dataset = ValidationDataset(
        dataset_id=dataset_id or path.stem,
        source_name="KIT Automotive OBD-II Dataset",
        time_s=t,
        measured_coolant_temp_c=numeric(COOLANT),
        engine_speed_rpm=numeric(RPM),
        vehicle_speed_m_s=numeric(SPEED) / 3.6,
        ambient_temp_c=numeric(AMBIENT),
        mass_air_flow_g_s=numeric(MAF),
        metadata={
            "source_file": path.name,
            "source_doi": "10.35097/1130",
            "license": "CC BY 4.0",
            "synchronization": "source timestamp order with forward fill of asynchronous OBD PID updates",
        },
    )
    dataset.validate()
    return dataset
