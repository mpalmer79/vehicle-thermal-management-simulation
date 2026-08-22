from __future__ import annotations

import numpy as np
import pytest

from vtms_v1.scenario import Scenario
from vtms_v2.m0.airflow import AirflowBoundary, AirflowBoundaryClass
from vtms_v2.m2 import (
    M2IndependentCase,
    M2Parameters,
    M2SimulationRunner,
    run_independent_ensemble,
)


def _boundary() -> AirflowBoundary:
    return AirflowBoundary(
        boundary_class=AirflowBoundaryClass.OTHER_DOCUMENTED_BOUNDARY,
        documented_core_vol_flow_m3_s=0.60,
        source_note="synthetic independent-M2 ensemble test",
    )


def _scenario(case_id: str) -> Scenario:
    return Scenario(
        scenario_id=case_id,
        name="Independent M2 ensemble verification",
        duration_s=45.0,
        ambient_temp_c=25.0,
        engine_speed_rpm=1800.0,
        effective_load=0.45,
        vehicle_speed_m_s=8.0,
        initial_engine_temp_c=90.0,
        initial_coolant_temp_c=82.0,
        engine_heat_override_w=25000.0,
        output_interval_s=0.5,
    )


def test_independent_ensemble_matches_separate_direct_runs() -> None:
    first_parameters = M2Parameters(head_heat_fraction=0.70)
    second_parameters = M2Parameters(
        head_thermal_capacitance_fraction=0.50,
        head_heat_fraction=0.95,
        head_block_ua_w_per_k=3000.0,
    )
    cases = (
        M2IndependentCase(
            case_id="CASE-A",
            parameters=first_parameters,
            scenario=_scenario("SYN-M2-INDEPENDENT-A"),
            airflow_boundary=_boundary(),
        ),
        M2IndependentCase(
            case_id="CASE-B",
            parameters=second_parameters,
            scenario=_scenario("SYN-M2-INDEPENDENT-B"),
            airflow_boundary=_boundary(),
            initial_head_temp_c=100.0,
            initial_block_temp_c=95.0,
            initial_cold_temp_c=75.0,
        ),
    )

    ensemble = run_independent_ensemble(cases)
    assert [item.case_id for item in ensemble] == ["CASE-A", "CASE-B"]

    for case, item in zip(cases, ensemble, strict=True):
        direct = M2SimulationRunner(case.parameters).run(
            case.scenario,
            airflow_boundary=case.airflow_boundary,
            initial_head_temp_c=case.initial_head_temp_c,
            initial_block_temp_c=case.initial_block_temp_c,
            initial_cold_temp_c=case.initial_cold_temp_c,
        )
        ensemble_ect = np.asarray(
            [point.ect_predicted_c for point in item.result.time_series],
            dtype=float,
        )
        direct_ect = np.asarray(
            [point.ect_predicted_c for point in direct.time_series],
            dtype=float,
        )
        assert np.allclose(ensemble_ect, direct_ect, rtol=0.0, atol=0.0)
        assert (
            item.result.solver_diagnostics.function_evaluations
            == direct.solver_diagnostics.function_evaluations
        )


def test_independent_ensemble_rejects_duplicate_case_ids() -> None:
    case = M2IndependentCase(
        case_id="DUPLICATE",
        parameters=M2Parameters(),
        scenario=_scenario("SYN-M2-DUPLICATE"),
        airflow_boundary=_boundary(),
    )
    with pytest.raises(ValueError, match="duplicate"):
        run_independent_ensemble((case, case))


def test_independent_ensemble_requires_at_least_one_case() -> None:
    with pytest.raises(ValueError, match="at least one"):
        run_independent_ensemble(())
