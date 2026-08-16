from vtms_v1 import SimulationRunner, canonical_scenarios
from vtms_v1.constants import LIQUID_MODEL_CAUTION_C


def test_result_contains_reproducibility_metadata():
    result = SimulationRunner().run(canonical_scenarios()["S-01"])
    assert result.model_metadata["model_id"] == "VTMS-V1"
    assert result.model_metadata["model_version"] == "1.0.0"
    assert result.model_metadata["equation_set"] == "EM-V1"
    assert result.model_metadata["digital_twin_status"] == "not_a_digital_twin_in_v1"
    assert "engine_thermal_capacitance_j_per_k" in result.parameter_snapshot
    assert result.provenance_snapshot["engine_thermal_capacitance_j_per_k"] == "CALIBRATED"


def test_failure_case_produces_liquid_model_warning_if_threshold_crossed():
    result = SimulationRunner().run(canonical_scenarios()["S-06"])
    if max(p.coolant_temp_c for p in result.time_series) >= LIQUID_MODEL_CAUTION_C:
        assert result.warnings
        assert any(e["event"] == "liquid_model_caution_boundary_crossed" for e in result.events)
