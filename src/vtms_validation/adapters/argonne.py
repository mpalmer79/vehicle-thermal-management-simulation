from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
import json
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
    "fuel_rate_kg_s": {"kg/s", "g/s"},
    "fuel_energy_rate_w": {"W", "kW"},
    "engine_torque_nm": {"N*m", "Nm"},
}


@dataclass(frozen=True)
class ArgonneSignalMap:
    """Explicit D3 source-to-VTMS mapping. No source column is inferred."""

    dataset_id: str
    source_name: str
    file_format: str
    columns: dict[str, str]
    units: dict[str, str]
    delimiter: str = ","
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str | Path) -> "ArgonneSignalMap":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            dataset_id=payload["dataset_id"],
            source_name=payload["source_name"],
            file_format=payload["file_format"],
            delimiter=payload.get("delimiter", ","),
            columns=dict(payload["columns"]),
            units=dict(payload["units"]),
            metadata=dict(payload.get("metadata", {})),
        )

    def validate(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("Argonne signal map requires dataset_id")
        if not self.source_name.strip():
            raise ValueError("Argonne signal map requires source_name")
        if self.file_format.lower() != "csv":
            raise NotImplementedError(
                "Only explicitly mapped CSV is implemented. Add a dedicated parser after the received D3 format is documented."
            )
        missing = [name for name in _REQUIRED_LOGICAL_CHANNELS if name not in self.columns]
        if missing:
            raise ValueError(f"Argonne signal map missing required logical channels: {missing}")
        unknown = sorted(set(self.columns) - set(_REQUIRED_LOGICAL_CHANNELS) - set(_OPTIONAL_LOGICAL_CHANNELS))
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
                    f"unsupported unit {unit!r} for {logical_name}; allowed: {sorted(_ALLOWED_UNITS[logical_name])}"
                )

    def snapshot(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


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
                "Provide a reviewed ArgonneSignalMap after the D3 signal dictionary is received."
            )
        mapping = ArgonneSignalMap.from_json(signal_map) if isinstance(signal_map, (str, Path)) else signal_map
        mapping.validate()

        source = Path(path)
        rows: list[dict[str, str]] = []
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
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Argonne column {source_column!r} contains non-numeric or missing values") from exc
            normalized[logical_name] = _convert_units(logical_name, raw, mapping.units[logical_name])

        time_s = normalized["time_s"] - normalized["time_s"][0]
        fingerprint = DatasetFingerprint.from_path(source)
        metadata = {
            **mapping.metadata,
            "adapter": "ArgonneD3Adapter",
            "source_file": fingerprint.file_name,
            "source_sha256": fingerprint.sha256_hex,
            "source_size_bytes": fingerprint.size_bytes,
            "signal_map_sha256": sha256_mapping(mapping.snapshot()),
            "mapping_policy": "explicit_no_schema_guessing",
        }

        dataset = ValidationDataset(
            dataset_id=mapping.dataset_id,
            source_name=mapping.source_name,
            time_s=time_s,
            measured_coolant_temp_c=normalized["engine_coolant_temp_c"],
            engine_speed_rpm=normalized["engine_speed_rpm"],
            vehicle_speed_m_s=normalized["vehicle_speed_m_s"],
            ambient_temp_c=normalized["ambient_temp_c"],
            mass_air_flow_g_s=normalized.get("mass_air_flow_g_s"),
            fuel_rate_kg_s=normalized.get("fuel_rate_kg_s"),
            fuel_energy_rate_w=normalized.get("fuel_energy_rate_w"),
            engine_torque_nm=normalized.get("engine_torque_nm"),
            metadata=metadata,
        )
        dataset.validate()
        return dataset


def _convert_units(logical_name: str, values: np.ndarray, unit: str) -> np.ndarray:
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
        return values if unit == "kg/s" else values / 1000.0
    if logical_name == "fuel_energy_rate_w":
        return values if unit == "W" else values * 1000.0
    if logical_name == "engine_torque_nm":
        return values
    raise ValueError(f"no unit conversion registered for {logical_name}")
