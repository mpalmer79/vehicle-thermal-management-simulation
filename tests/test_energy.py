from vtms_v1 import SimulationRunner, canonical_scenarios


def test_energy_conservation_all_canonical_scenarios():
    runner = SimulationRunner()
    for scenario_id, scenario in canonical_scenarios().items():
        result = runner.run(scenario)
        assert result.energy_balance.normalized_residual <= 0.001, (
            scenario_id,
            result.energy_balance.normalized_residual,
        )
