from vtms_v1 import SimulationRunner, canonical_scenarios


def test_all_canonical_scenarios_solve_successfully():
    runner = SimulationRunner()
    for scenario in canonical_scenarios().values():
        result = runner.run(scenario)
        assert result.solver_diagnostics.success
        assert len(result.time_series) >= 2


def test_fault_direction_behavior():
    runner = SimulationRunner()
    scenarios = canonical_scenarios()
    nominal_high = runner.run(scenarios["S-04"]).final_point().coolant_temp_c
    for sid in ("S-07", "S-08", "S-09"):
        fault_temp = runner.run(scenarios[sid]).final_point().coolant_temp_c
        assert fault_temp > nominal_high


def test_closed_thermostat_removes_radiator_flow():
    result = SimulationRunner().run(canonical_scenarios()["S-06"])
    assert all(point.radiator_flow_kg_s == 0.0 for point in result.time_series)
    assert all(point.radiator_heat_w == 0.0 for point in result.time_series)
    assert all(point.radiator_outlet_temp_c is None for point in result.time_series)


def test_fan_failure_removes_forced_air_at_idle():
    result = SimulationRunner().run(canonical_scenarios()["S-05"])
    assert all(point.fan_fraction == 0.0 for point in result.time_series)
    assert all(point.air_flow_kg_s == 0.0 for point in result.time_series)
