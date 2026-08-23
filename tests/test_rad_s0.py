from vtms_v2.rad_s0 import evaluate_rad_s0


REPORT = evaluate_rad_s0()


def test_rad_s0_preserves_preregistered_negative_identifiability_result() -> None:
    verification = REPORT["verification"]
    identifiability = REPORT["identifiability"]

    assert verification["status"] == "PASS"
    assert identifiability["status"] == "FAIL"
    assert REPORT["overall_status"] == "FAIL"

    assert identifiability["all_columns_active"] is True
    assert identifiability["n_air_relative_rms_to_strongest"] >= 0.02
    assert identifiability["normalized_jacobian_condition_number"] > 100.0
    assert identifiability["max_abs_pairwise_cosine_involving_n_air"] >= 0.95
    assert all(item["pass"] for item in identifiability["discrete_candidate_separation"])


def test_rad_s0_candidate_verification_and_constant_ua_collapse_remain_exact() -> None:
    verification = REPORT["verification"]

    assert verification["zero_flow_pass"] is True
    assert verification["reference_flow_pass"] is True
    assert verification["n_air_zero_constant_ua_collapse_pass"] is True
    assert verification["monotonic_heat_rejection_with_airflow_pass"] is True
    assert verification["effectiveness_bounds_pass"] is True
    assert verification["reference_flow_heat_error_w"] <= 1.0e-10
    assert verification["n_air_zero_max_heat_error_w"] <= 1.0e-10
    assert verification["normalized_energy_residual"] <= 0.001
