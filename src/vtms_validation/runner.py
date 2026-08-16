from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from vtms_v1.config import ModelParameters
from vtms_v1.scenario import Scenario
from vtms_v1.simulation import SimulationRunner

from .dataset import ValidationDataset
from .heat_input import MafStoichiometricHeatEstimator
from .metrics import ValidationMetrics, calculate_metrics


@dataclass(frozen=True)
class ComparisonResult:
    dataset_id: str
    comparison_time_s: np.ndarray
    measured_coolant_temp_c: np.ndarray
    predicted_coolant_temp_c: np.ndarray
    residual_c: np.ndarray
    metrics: ValidationMetrics
    simulation_result: object
    heat_input_metadata: dict[str, object]
    evidence_label: str


def _profile(dataset: ValidationDataset, values: np.ndarray):
    return lambda time_s: dataset.interp(values, time_s)


def run_kit_plausibility(
    dataset: ValidationDataset,
    *,
    parameters: ModelParameters | None = None,
    initial_engine_temp_c: float | None = None,
    estimator: MafStoichiometricHeatEstimator | None = None,
) -> ComparisonResult:
    dataset.validate()
    if dataset.mass_air_flow_g_s is None:
        raise ValueError("KIT plausibility runner requires MAF")
    parameters = parameters or ModelParameters()
    estimator = estimator or MafStoichiometricHeatEstimator(
        wall_heat_fraction=parameters.wall_heat_fraction
    )
    q_engine = np.asarray(estimator.engine_heat_w(dataset.mass_air_flow_g_s), dtype=float)
    te0 = (
        float(dataset.measured_coolant_temp_c[0])
        if initial_engine_temp_c is None
        else float(initial_engine_temp_c)
    )

    scenario = Scenario(
        scenario_id=f"KIT-{dataset.dataset_id}",
        name="KIT external plausibility comparison",
        duration_s=dataset.duration_s,
        ambient_temp_c=_profile(dataset, dataset.ambient_temp_c),
        engine_speed_rpm=_profile(dataset, dataset.engine_speed_rpm),
        effective_load=0.0,
        vehicle_speed_m_s=_profile(dataset, dataset.vehicle_speed_m_s),
        initial_engine_temp_c=te0,
        initial_coolant_temp_c=float(dataset.measured_coolant_temp_c[0]),
        engine_heat_override_w=_profile(dataset, q_engine),
        output_interval_s=1.0,
    )
    result = SimulationRunner(parameters=parameters).run(scenario)
    sim_t = np.array([p.time_s for p in result.time_series], dtype=float)
    sim_c = np.array([p.coolant_temp_c for p in result.time_series], dtype=float)
    predicted = np.interp(dataset.time_s, sim_t, sim_c)
    measured = dataset.measured_coolant_temp_c.astype(float)
    metrics = calculate_metrics(dataset.time_s, measured, predicted)
    return ComparisonResult(
        dataset_id=dataset.dataset_id,
        comparison_time_s=dataset.time_s.copy(),
        measured_coolant_temp_c=measured.copy(),
        predicted_coolant_temp_c=predicted,
        residual_c=predicted - measured,
        metrics=metrics,
        simulation_result=result,
        heat_input_metadata=estimator.metadata(),
        evidence_label="external_plausibility_not_formal_validation",
    )
