from vtms_v2.rad_s0 import evaluate_rad_s0


def test_rad_s0_candidate_passes_preregistered_synthetic_gate() -> None:
    report = evaluate_rad_s0()

    assert report["verification"]["status"] == "PASS"
    assert report["identifiability"]["status"] == "PASS"
    assert report["overall_status"] == "PASS"


def test_rad_s0_constant_ua_collapse_is_exact() -> None:
    report = evaluate_rad_s0()

    verification = report["verification"]
    assert verification["reference_flow_pass"] is True
    assert verification["n_air_zero_constant_ua_collapse_pass"] is True
    assert verification["reference_flow_heat_error_w"] <= 1.0e-10
    assert verification["n_air_zero_max_heat_error_w"] <= 1.0e-10
