from fastapi.testclient import TestClient

from vtms_api.app import app


client = TestClient(app)


def s03_payload() -> dict[str, object]:
    return {
        "scenario_id": "S-03",
        "name": "Hot ambient idle",
        "duration_s": 1200,
        "ambient_temp_c": 40,
        "engine_speed_rpm": 1000,
        "effective_load_percent": 25,
        "vehicle_speed_kmh": 0,
        "initial_engine_temp_c": 105,
        "initial_coolant_temp_c": 92,
        "output_interval_s": 2,
        "faults": {},
    }


def test_health_reports_frozen_model_identity() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_id"] == "VTMS-V1"
    assert body["equation_set"] == "EM-V1"


def test_simulation_endpoint_runs_authoritative_s03_model() -> None:
    response = client.post("/api/v1/simulations", json=s03_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "computed_simulation"
    assert body["run_id"].startswith("run_")

    result = body["result"]
    final = result["time_series"][-1]
    assert abs(final["engine_structure_temp_c"] - 101.06) < 0.2
    assert abs(final["coolant_temp_c"] - 96.50) < 0.2
    assert result["model_metadata"]["model_id"] == "VTMS-V1"
    assert result["model_metadata"]["digital_twin_status"] == "not_a_digital_twin_in_v1"
    assert result["energy_balance"]["normalized_residual"] <= 0.001


def test_api_translates_kmh_and_load_percent_to_core_units() -> None:
    payload = s03_payload()
    payload["vehicle_speed_kmh"] = 100
    payload["effective_load_percent"] = 45
    payload["duration_s"] = 10
    response = client.post("/api/v1/simulations", json=payload)
    assert response.status_code == 200
    metadata = response.json()["result"]["scenario_metadata"]
    assert abs(metadata["vehicle_speed_m_s"] - (100 / 3.6)) < 1e-10
    assert metadata["effective_load"] == 0.45


def test_invalid_reference_rpm_is_rejected_before_simulation() -> None:
    payload = s03_payload()
    payload["engine_speed_rpm"] = 500
    response = client.post("/api/v1/simulations", json=payload)
    assert response.status_code == 422


def test_fault_request_changes_physical_result_without_frontend_physics() -> None:
    payload = s03_payload()
    payload["faults"] = {"fan_failed": True}
    response = client.post("/api/v1/simulations", json=payload)
    assert response.status_code == 200
    result = response.json()["result"]
    final = result["time_series"][-1]
    assert final["coolant_temp_c"] > 150
    assert result["warnings"]


def test_scenario_catalog_exposes_all_frozen_canonical_cases() -> None:
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 200
    ids = {item["scenario_id"] for item in response.json()}
    assert ids == {f"S-{index:02d}" for index in range(1, 10)}
