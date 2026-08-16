from vtms_v1 import SimulationRunner, canonical_scenarios


EXPECTED_END_STATES = {
    "S-01": (102.68, 96.47),
    "S-02": (122.43, 90.87),
    "S-03": (101.06, 96.50),
    "S-04": (139.77, 96.35),
    "S-05": (168.02, 166.79),
    "S-06": (168.02, 166.79),
    "S-07": (146.11, 102.76),
    "S-08": (163.09, 119.96),
    "S-09": (145.27, 101.91),
}


def test_canonical_end_states_match_specification_audit():
    runner = SimulationRunner()
    for scenario_id, scenario in canonical_scenarios().items():
        result = runner.run(scenario)
        final = result.final_point()
        expected_engine, expected_coolant = EXPECTED_END_STATES[scenario_id]
        assert abs(final.engine_structure_temp_c - expected_engine) < 0.15
        assert abs(final.coolant_temp_c - expected_coolant) < 0.15
