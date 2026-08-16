import numpy as np

from vtms_v1 import SimulationRunner, canonical_scenarios


def test_solver_convergence_s01():
    runner = SimulationRunner()
    scenario = canonical_scenarios()["S-01"]
    baseline = runner.run(scenario)
    tight = runner.run(scenario, rtol=1e-7, atol=1e-9, max_step_s=0.5)

    base_engine = np.array([p.engine_structure_temp_c for p in baseline.time_series])
    tight_engine = np.array([p.engine_structure_temp_c for p in tight.time_series])
    base_coolant = np.array([p.coolant_temp_c for p in baseline.time_series])
    tight_coolant = np.array([p.coolant_temp_c for p in tight.time_series])

    max_diff = max(
        float(np.max(np.abs(base_engine - tight_engine))),
        float(np.max(np.abs(base_coolant - tight_coolant))),
    )
    assert max_diff < 0.05
