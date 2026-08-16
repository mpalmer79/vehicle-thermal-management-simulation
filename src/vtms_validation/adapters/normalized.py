from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from ..dataset import ValidationDataset


def load_normalized_sample_csv(path: str | Path, *, dataset_id: str, source_name: str) -> ValidationDataset:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("normalized validation CSV contains no rows")

    def values(name: str) -> np.ndarray:
        return np.asarray([float(row[name]) for row in rows], dtype=float)

    dataset = ValidationDataset(
        dataset_id=dataset_id,
        source_name=source_name,
        time_s=values("time_s"),
        measured_coolant_temp_c=values("measured_coolant_temp_c"),
        engine_speed_rpm=values("engine_speed_rpm"),
        vehicle_speed_m_s=values("vehicle_speed_kmh") / 3.6,
        ambient_temp_c=values("ambient_temp_c"),
        mass_air_flow_g_s=values("mass_air_flow_g_s"),
        metadata={
            "source_file": path.name,
            "sampling": "60-second representative samples extracted from a real KIT CSV",
            "evidence_grade": "coarse_external_plausibility_only",
            "raw_pid_behavior": "source rows are asynchronous OBD PID updates",
        },
    )
    dataset.validate()
    return dataset
