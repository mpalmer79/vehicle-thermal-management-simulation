import numpy as np
import pytest

pytest.importorskip("numba")

from vtms_validation.dataset import ValidationDataset
from vtms_v2.m2.stage_b import case_from_global_index
from vtms_v2.m2.stage_b_accel import compare_stage_b_acceleration


def _synthetic_stage_b_dataset() -> ValidationDataset:
    time_s = np.arange(0.0, 181.0, 1.0)
    measured = 95.0 + 2.5 * (1.0 - np.exp(-time_s / 50.0))
    engine_speed = 1800.0 + 500.0 * np.sin(time_s / 19.0)
    ambient = 25.0 + 1.5 * np.sin(time_s / 37.0)
    fuel_energy = 100_000.0 + 25_000.0 * np.sin(time_s / 23.0)
    return ValidationDataset(
        dataset_id="M2-STAGE-B-ACCEL-SYNTHETIC",
        source_name="synthetic acceleration equivalence fixture",
        time_s=time_s,
        measured_coolant_temp_c=measured,
        engine_speed_rpm=engine_speed,
        vehicle_speed_m_s=np.zeros_like(time_s),
        ambient_temp_c=ambient,
        fuel_energy_rate_w=fuel_energy,
    )


@pytest.mark.parametrize("global_index", [0, 3248, 3550])
def test_stage_b_compiled_rhs_matches_reference_trace(global_index: int) -> None:
    dataset = _synthetic_stage_b_dataset()
    comparison = compare_stage_b_acceleration(
        dataset,
        case_from_global_index(global_index),
        trace_atol_c=1.0e-9,
    )

    assert comparison.equivalent is True
    assert comparison.max_abs_trace_error_c <= 1.0e-9
    assert comparison.rms_trace_error_c <= 1.0e-9
    assert comparison.reference_pass == comparison.accelerated_pass


def test_stage_b_compiled_rhs_matches_reference_with_hidden_state_offsets() -> None:
    dataset = _synthetic_stage_b_dataset()
    comparison = compare_stage_b_acceleration(
        dataset,
        case_from_global_index(3248),
        initial_head_offset_c=30.0,
        initial_block_offset_c=20.0,
        initial_cold_offset_c=-10.0,
        trace_atol_c=1.0e-9,
    )

    assert comparison.equivalent is True
    assert comparison.max_abs_trace_error_c <= 1.0e-9
    assert comparison.reference_pass == comparison.accelerated_pass
