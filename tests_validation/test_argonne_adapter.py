import json

import numpy as np
import pytest

from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap


def _mapping(**overrides) -> ArgonneSignalMap:
    payload = {
        "dataset_id": "ARGONNE-D3-TEST",
        "source_name": "Argonne D3 test fixture",
        "file_format": "tsv",
        "delimiter": "\t",
        "columns": {
            "time_s": "Time [s]",
            "engine_coolant_temp_c": "EngineCoolantTemp[C]",
            "engine_speed_rpm": "Eng_Spd[RPM]",
            "vehicle_speed_m_s": "Dyno_Spd[mph]",
            "ambient_temp_c": "Cell_Temp[C]",
            "fuel_rate_kg_s": "Eng_FuelFlow_Direct[cc/s]",
        },
        "units": {
            "time_s": "s",
            "engine_coolant_temp_c": "C",
            "engine_speed_rpm": "rpm",
            "vehicle_speed_m_s": "mph",
            "ambient_temp_c": "C",
            "fuel_rate_kg_s": "cc/s",
        },
        "metadata": {"fuel_density_g_ml": 0.743},
    }
    payload.update(overrides)
    return ArgonneSignalMap(**payload)


def _write_tsv(path, rows):
    headers = [
        "Time [s]",
        "EngineCoolantTemp[C]",
        "Eng_Spd[RPM]",
        "Dyno_Spd[mph]",
        "Cell_Temp[C]",
        "Eng_FuelFlow_Direct[cc/s]",
    ]
    path.write_text(
        "\t".join(headers)
        + "\n"
        + "\n".join("\t".join(str(value) for value in row) for row in rows)
        + "\n",
        encoding="utf-8",
    )


def test_argonne_adapter_loads_reviewed_tsv_and_converts_direct_fuel(tmp_path):
    source = tmp_path / "71207062 Test Data.txt"
    _write_tsv(
        source,
        [
            (-1.0, 25.0, 0.0, 0.0, 21.0, 0.0),
            (0.0, 25.0, 650.0, 10.0, 21.0, 1.0),
            (1.0, 25.5, 900.0, 20.0, 21.1, 2.0),
        ],
    )

    dataset = ArgonneD3Adapter().load(
        source,
        _mapping(start_time_s=0.0),
    )

    np.testing.assert_allclose(dataset.time_s, [0.0, 1.0])
    np.testing.assert_allclose(dataset.vehicle_speed_m_s, [4.4704, 8.9408])
    np.testing.assert_allclose(dataset.fuel_rate_kg_s, [0.000743, 0.001486])
    np.testing.assert_allclose(dataset.engine_speed_rpm, [650.0, 900.0])
    assert dataset.metadata["source_rows_before_selection"] == 3
    assert dataset.metadata["source_rows_after_selection"] == 2
    assert dataset.metadata["mapping_policy"] == "explicit_no_schema_guessing"
    assert dataset.metadata["cleanup_policy"] == "explicit_reviewed_no_cleanup_guessing"


def test_argonne_volumetric_fuel_requires_explicit_density():
    mapping = _mapping(metadata={})
    with pytest.raises(ValueError, match="fuel_density_g_ml"):
        mapping.validate()


def test_argonne_row_selection_is_explicit_and_rezeros_selected_time(tmp_path):
    source = tmp_path / "source.txt"
    _write_tsv(
        source,
        [
            (8.7, 25.0, 900.0, 0.0, 21.0, 1.0),
            (8.8, 25.0, 900.0, 0.0, 21.0, 1.0),
            (8.9, 12.5, 900.0, 0.0, 21.0, 1.0),
            (9.0, 25.5, 900.0, 0.0, 21.0, 1.0),
        ],
    )

    dataset = ArgonneD3Adapter().load(
        source,
        _mapping(
            start_time_s=8.7,
            exclude_time_intervals_s=((8.9, 8.9),),
        ),
    )

    np.testing.assert_allclose(dataset.time_s, [0.0, 0.1, 0.3])
    np.testing.assert_allclose(dataset.measured_coolant_temp_c, [25.0, 25.0, 25.5])
    assert dataset.metadata["row_selection"]["exclude_time_intervals_s"] == [[8.9, 8.9]]


def test_argonne_row_selection_rejects_overlapping_exclusions():
    mapping = _mapping(
        exclude_time_intervals_s=((10.0, 12.0), (11.0, 13.0)),
    )
    with pytest.raises(ValueError, match="overlap"):
        mapping.validate()


def test_argonne_mapping_json_preserves_reviewed_row_selection(tmp_path):
    path = tmp_path / "mapping.json"
    path.write_text(
        json.dumps(
            {
                "dataset_id": "ARGONNE-D3-71207062",
                "source_name": "Argonne D3",
                "file_format": "tsv",
                "delimiter": "\t",
                "columns": _mapping().columns,
                "units": _mapping().units,
                "row_selection": {
                    "start_time_s": 8.7,
                    "end_time_s": 100.0,
                    "exclude_time_intervals_s": [[20.0, 20.1]],
                },
                "metadata": {"fuel_density_g_ml": 0.743},
            }
        ),
        encoding="utf-8",
    )

    mapping = ArgonneSignalMap.from_json(path)
    mapping.validate()
    assert mapping.start_time_s == 8.7
    assert mapping.end_time_s == 100.0
    assert mapping.exclude_time_intervals_s == ((20.0, 20.1),)
    assert mapping.snapshot()["row_selection"]["start_time_s"] == 8.7


def test_argonne_adapter_still_refuses_schema_guessing(tmp_path):
    source = tmp_path / "unknown.txt"
    source.write_text("unknown\n1\n2\n", encoding="utf-8")
    with pytest.raises(NotImplementedError, match="not guessed"):
        ArgonneD3Adapter().load(source)
