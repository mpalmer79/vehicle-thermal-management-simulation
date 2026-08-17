from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from ..dataset import ValidationDataset
from ..manifest import DatasetFingerprint, sha256_mapping


_REQUIRED_LOGICAL_CHANNELS = (
    "time_s",
    "engine_coolant_temp_c",
    "engine_speed_rpm",
    "vehicle_speed_m_s",
    "ambient_temp_c",
)

_OPTIONAL_LOGICAL_CHANNELS = (
    "mass_air_flow_g_s",
    "fuel_rate_kg_s",
    "fuel_energy_rate_w",
    "engine_torque_nm",
)

_ALLOWED_UNITS: dict[str, set[str]] = {
    "time_s": {"s", "ms"},
    "engine_coolant_temp_c": {"C", "F"},
    "engine_speed_rpm": {"rpm"},
    "vehicle_speed_m_s": {"m/s", "km/h", "mph"},
    "ambient_temp_c": {"C", "F"},
    "mass_air_flow_g_s": {"g/s", "kg/s"},
    "fuel_rate_kg_s": {"kg/s", "g/s", "cc/s"},
    "fuel_energy_rate_w": {"W", "kW"},
    "engine_torque_nm": {"N*m", "Nm"},
}


@dataclass(frozen=True)
class ArgonneSignalMap:
    """Explicit D3 source-to-VTMS mapping. No source column or cleanup rule is inferred."""

    dataset_id: str
    source_name: str
    file_format: str
    columns: dict[str, str]
    units: dict[str, str]
    delimiter: str = ","
    start_time_s: float | None = None
    end_time_s: float | None = None
    exclude_time_intervals_s: tuple[tuple[float, float], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str | Path) -> "ArgonneSignalMap":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        selection = dict(payload.get("row_selection", {}))
        raw_exclusions = selection.get("exclude_time_intervals_s", [])
        exclusions = tuple((float(pair[0]), float(pair[1])) for pair in raw_exclusions)
        return cls(
            dataset_id=payload["dataset_id"],
            source_name=payload["source_name"],
            file_format=payload["file_format"],
            delimiter=payload.get("delimiter", ","),
            columns=dict(payload["columns"]),
            units=dict(payload["units"]),
            start_time_s=_optional_float(selection.get("start_time_s")),
            end_time_s=_optional_float(selection.get("end_time_s")),
            exclude_time_intervals_s=exclusions,
            metadata=dict(payload.get("metadata", {})),
        )

    def validate(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("Argonne signal map requires dataset_id")
        if "REPLACE" in self.dataset_id.upper():
            raise ValueError("Argonne signal map dataset_id is unresolved")
        if not self.source_name.strip():
            raise ValueError("Argonne signal map requires source_name")

        file_format = self.file_format.lower()
        if file_format not in {"csv", "tsv", "txt"}:
            raise NotImplementedError(
                "Argonne adapter supports only explicitly mapped CSV, TSV, or delimited text files."
            )
        if len(self.delimiter) != 1:
            raise ValueError("Argonne signal map delimiter must be exactly one character")

        missing = [name for name in _REQUIRED_LOGICAL_CHANNELS if name not in self.columns]
        if missing:
            raise ValueError(f"Argonne signal map missing required logical channels: {missing}")
        unknown = sorted(
            set(self.columns) - set(_REQUIRED_LOGICAL_CHANNELS) - set(_OPTIONAL_LOGICAL_CHANNELS)
        )
        if unknown:
            raise ValueError(f"Argonne signal map contains unsupported logical channels: {unknown}")

        for logical_name, source_column in self.columns.items():
            if not source_column.strip() or "REPLACE" in source_column.upper():
                raise ValueError(f"Argonne source column for {logical_name} is unresolved")
            if logical_name not in self.units:
                raise ValueError(f"Argonne signal map missing unit declaration for {logical_name}")
            unit = self.units[logical_name]
            if unit not in _ALLOWED_UNITS[logical_name]:
                raise ValueError(
                    f"unsupported unit {unit!r} for {logical_name}; "
                    f"allowed: {sorted(_ALLOWED_UNITS[logical_name])}"
                )

        _validate_row_selection(self)

        if self.units.get("fuel_rate_kg_s") == "cc/s":
            density = self.metadata.get("fuel_density_g_ml")
            if not _is_positive_finite_number(density):
                raise ValueError(
                    "Argonne volumetric fuel flow in cc/s requires positive finite "
                    "metadata.fuel_density_g_ml"
                )

    def snapshot(self) -> dict[str, Any]:
        self.validate()
        snapshot = asdict(self)
        snapshot["row_selection"] = {
            "start_time_s": snapshot.pop("start_time_s"),
            "end_time_s": snapshot.pop("end_time_s"),
            "exclude_time_intervals_s": snapshot.pop("exclude_time_intervals_s"),
        }
        return snapshot


class ArgonneD3Adapter:
    """Normalize D3 data only through a reviewed, explicit signal map."""

    REQUIRED_LOGICAL_CHANNELS = _REQUIRED_LOGICAL_CHANNELS
    PREFERRED_HEAT_CHANNELS = (
        "fuel_rate_kg_s",
        "fuel_energy_rate_w",
        "engine_torque_nm",
    )

    def load(
        self,
        path: str | Path,
        signal_map: ArgonneSignalMap | str | Path | None = None,
    ) -> ValidationDataset:
        if signal_map is None:
            raise NotImplementedError(
                "Argonne D3 channel names/units are intentionally not guessed. "
                "Provide a reviewed ArgonneSignalMap."
            )
        mapping = (
            ArgonneSignalMap.from_json(signal_map)
            if isinstance(signal_map, (str, Path))
            else signal_map
        )
        mapping.validate()

        source = Path(path)
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=mapping.delimiter)
            fieldnames = set(reader.fieldnames or [])
            missing_columns = sorted(set(mapping.columns.values()) - fieldnames)
            if missing_columns:
                raise ValueError(f"Argonne source file is missing mapped columns: {missing_columns}")
            rows = list(reader)

        if len(rows) < 2:
            raise ValueError("Argonne source file requires at least two data rows")

        normalized: dict[str, np.ndarray] = {}
        for logical_name, source_column in mapping.columns.items():
            try:
                raw = np.asarray([float(row[source_column]) for row in rows], dtype=float)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Argonne column {source_column!r} contains non-numeric or missing values"
                ) from exc
            normalized[logical_name] = _convert_units(
                logical_name,
                raw,
                mapping.units[logical_name],
                mapping.metadata,
            )

        selected, selection_metadata = _apply_row_selection(normalized, mapping)
        time_s = selected["time_s"] - selected["time_s"][0]

        fingerprint = DatasetFingerprint.from_path(source)
        metadata = {
            **mapping.metadata,
            "adapter": "ArgonneD3Adapter",
            "source_file": fingerprint.file_name,
            "source_sha256": fingerprint.sha256_hex,
            "source_size_bytes": fingerprint.size_bytes,
            "signal_map_sha256": sha256_mapping(mapping.snapshot()),
            "mapping_policy": "explicit_no_schema_guessing",
            "cleanup_policy": "explicit_reviewed_no_cleanup_guessing",
            **selection_metadata,
        }

        dataset = ValidationDataset(
            dataset_id=mapping.dataset_id,
            source_name=mapping.source_name,
            time_s=time_s,
            measured_coolant_temp_c=selected["engine_coolant_temp_c"],
            engine_speed_rpm=selected["engine_speed_rpm"],
            vehicle_speed_m_s=selected["vehicle_speed_m_s"],
            ambient_temp_c=selected["ambient_temp_c"],
            mass_air_flow_g_s=selected.get("mass_air_flow_g_s"),
            fuel_rate_kg_s=selected.get("fuel_rate_kg_s"),
            fuel_energy_rate_w=selected.get("fuel_energy_rate_w"),
            engine_torque_nm=selected.get("engine_torque_nm"),
            metadata=metadata,
        )
        dataset.validate()
        return dataset


def _optional_float(value: object) -> float | None:
    return None if value is None else float(value)


def _is_positive_finite_number(value: object) -> bool:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(parsed) and parsed > 0.0


def _validate_row_selection(mapping: ArgonneSignalMap) -> None:
    for name, value in (
        ("start_time_s", mapping.start_time_s),
        ("end_time_s", mapping.end_time_s),
    ):
        if value is not None and not math.isfinite(float(value)):
            raise ValueError(f"Argonne row selection {name} must be finite")

    if (
        mapping.start_time_s is not None
        and mapping.end_time_s is not None
        and mapping.end_time_s < mapping.start_time_s
    ):
        raise ValueError("Argonne row selection end_time_s must be >= start_time_s")

    prior_end: float | None = None
    for index, interval in enumerate(sorted(mapping.exclude_time_intervals_s)):
        if len(interval) != 2:
            raise ValueError("Argonne exclusion intervals must be [start_s, end_s] pairs")
        start_s, end_s = float(interval[0]), float(interval[1])
        if not math.isfinite(start_s) or not math.isfinite(end_s):
            raise ValueError("Argonne exclusion interval bounds must be finite")
        if end_s < start_s:
            raise ValueError("Argonne exclusion interval end must be >= start")
        if prior_end is not None and start_s <= prior_end:
            raise ValueError(
                f"Argonne exclusion intervals overlap or touch at sorted interval index {index}"
            )
        prior_end = end_s


def _apply_row_selection(
    normalized: dict[str, np.ndarray],
    mapping: ArgonneSignalMap,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    source_time_s = normalized["time_s"]
    if len(source_time_s) < 2:
        raise ValueError("Argonne source file requires at least two mapped time samples")
    if not np.all(np.isfinite(source_time_s)):
        raise ValueError("Argonne mapped time contains non-finite values")
    if np.any(np.diff(source_time_s) <= 0):
        raise ValueError("Argonne mapped source time must be strictly increasing before selection")

    mask = np.ones(len(source_time_s), dtype=bool)
    if mapping.start_time_s is not None:
        mask &= source_time_s >= float(mapping.start_time_s)
    if mapping.end_time_s is not None:
        mask &= source_time_s <= float(mapping.end_time_s)

    for start_s, end_s in mapping.exclude_time_intervals_s:
        mask &= ~((source_time_s >= float(start_s)) & (source_time_s <= float(end_s)))

    if int(np.count_nonzero(mask)) < 2:
        raise ValueError("Argonne row selection leaves fewer than two samples")

    selected = {name: values[mask] for name, values in normalized.items()}
    selected_source_time = selected["time_s"]

    selection_metadata = {
        "source_rows_before_selection": len(source_time_s),
        "source_rows_after_selection": len(selected_source_time),
        "source_time_start_s_before_selection": float(source_time_s[0]),
        "source_time_end_s_before_selection": float(source_time_s[-1]),
        "source_time_start_s_after_selection": float(selected_source_time[0]),
        "source_time_end_s_after_selection": float(selected_source_time[-1]),
        "row_selection": {
            "start_time_s": mapping.start_time_s,
            "end_time_s": mapping.end_time_s,
            "exclude_time_intervals_s": [
                [float(start_s), float(end_s)]
                for start_s, end_s in mapping.exclude_time_intervals_s
            ],
            "policy": "explicit_reviewed_source_time_selection",
        },
    }
    return selected, selection_metadata


def _convert_units(
    logical_name: str,
    values: np.ndarray,
    unit: str,
    metadata: dict[str, Any],
) -> np.ndarray:
    if logical_name == "time_s":
        return values if unit == "s" else values / 1000.0
    if logical_name in {"engine_coolant_temp_c", "ambient_temp_c"}:
        return values if unit == "C" else (values - 32.0) * (5.0 / 9.0)
    if logical_name == "engine_speed_rpm":
        return values
    if logical_name == "vehicle_speed_m_s":
        if unit == "m/s":
            return values
        if unit == "km/h":
            return values / 3.6
        return values * 0.44704
    if logical_name == "mass_air_flow_g_s":
        return values if unit == "g/s" else values * 1000.0
    if logical_name == "fuel_rate_kg_s":
        if unit == "kg/s":
            return values
        if unit == "g/s":
            return values / 1000.0
        density_g_ml = float(metadata["fuel_density_g_ml"])
        return values * density_g_ml / 1000.0
    if logical_name == "fuel_energy_rate_w":
        return values if unit == "W" else values * 1000.0
    if logical_name == "engine_torque_nm":
        return values
    raise ValueError(f"no unit conversion registered for {logical_name}")
