from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from vtms_v1.config import ModelParameters
from vtms_v1.scenario import Scenario
from vtms_v1.simulation import SimulationRunner

from .dataset import ValidationDataset
from .heat_input import MafStoichiometricHeatEstimator
from .manifest import ValidationRole, ValidationRunManifest, sha256_mapping
from .metrics import ValidationMetrics, calculate_metrics


_REFERENCE_MIN_NONZERO_RPM = 700.0
_REFERENCE_MAX_RPM = 6500.0


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
    validation_manifest: dict[str, object] | None = None
    input_preprocessing_metadata: dict[str, object] = field(default_factory=dict)


def _profile(dataset: ValidationDataset, values: np.ndarray):
    return lambda time_s: dataset.interp(values, time_s)


def _project_engine_speed_to_reference_domain(
    engine_speed_rpm: np.ndarray,
) -> tuple[np.ndarray, dict[str, object]]:
    """Project measured RPM only at the Scenario boundary.

    ValidationDataset retains the measured source values. The frozen VTMS-V1
    Scenario contract accepts 0 rpm or 700..6500 rpm. Controlled validation
    supplies engine heat through an independent heat override, so this projection
    is used only for component-model compatibility and does not replace the raw
    evidence stored in the dataset.
    """

    raw = np.asarray(engine_speed_rpm, dtype=float)
    projected = raw.copy()
    low_mask = (projected > 0.0) & (projected < _REFERENCE_MIN_NONZERO_RPM)
    high_mask = projected > _REFERENCE_MAX_RPM
    projected[low_mask] = _REFERENCE_MIN_NONZERO_RPM
    projected[high_mask] = _REFERENCE_MAX_RPM

    changed_mask = low_mask | high_mask
    metadata: dict[str, object] = {
        "policy": "project_measured_rpm_at_frozen_vtms_v1_scenario_boundary",
        "reference_nonzero_rpm_min": _REFERENCE_MIN_NONZERO_RPM,
        "reference_rpm_max": _REFERENCE_MAX_RPM,
        "raw_min_rpm": float(np.min(raw)),
        "raw_max_rpm": float(np.max(raw)),
        "projected_sample_count": int(np.count_nonzero(changed_mask)),
        "projected_low_sample_count": int(np.count_nonzero(low_mask)),
        "projected_high_sample_count": int(np.count_nonzero(high_mask)),
        "raw_dataset_values_preserved": True,
        "engine_heat_uses_rpm_load_estimator": False,
    }
    return projected, metadata


def _run_comparison(
    dataset: ValidationDataset,
    parameters: ModelParameters,
    q_engine_w: np.ndarray,
    *,
    scenario_id: str,
    scenario_name: str,
    initial_engine_temp_c: float | None,
) -> tuple[object, np.ndarray, np.ndarray, ValidationMetrics]:
    te0 = (
        float(dataset.measured_coolant_temp_c[0])
        if initial_engine_temp_c is None
        else float(initial_engine_temp_c)
    )
    reference_rpm, _ = _project_engine_speed_to_reference_domain(dataset.engine_speed_rpm)
    scenario = Scenario(
        scenario_id=scenario_id,
        name=scenario_name,
        duration_s=dataset.duration_s,
        ambient_temp_c=_profile(dataset, dataset.ambient_temp_c),
        engine_speed_rpm=_profile(dataset, reference_rpm),
        effective_load=0.0,
        vehicle_speed_m_s=_profile(dataset, dataset.vehicle_speed_m_s),
        initial_engine_temp_c=te0,
        initial_coolant_temp_c=float(dataset.measured_coolant_temp_c[0]),
        engine_heat_override_w=_profile(dataset, q_engine_w),
        output_interval_s=1.0,
    )
    result = SimulationRunner(parameters=parameters).run(scenario)
    sim_t = np.array([p.time_s for p in result.time_series], dtype=float)
    sim_c = np.array([p.coolant_temp_c for p in result.time_series], dtype=float)
    predicted = np.interp(dataset.time_s, sim_t, sim_c)
    measured = dataset.measured_coolant_temp_c.astype(float)
    metrics = calculate_metrics(dataset.time_s, measured, predicted)
    return result, measured, predicted, metrics


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
    _, rpm_metadata = _project_engine_speed_to_reference_domain(dataset.engine_speed_rpm)
    preprocessing = {"engine_speed_rpm": rpm_metadata}
    result, measured, predicted, metrics = _run_comparison(
        dataset,
        parameters,
        q_engine,
        scenario_id=f"KIT-{dataset.dataset_id}",
        scenario_name="KIT external plausibility comparison",
        initial_engine_temp_c=initial_engine_temp_c,
    )
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
        input_preprocessing_metadata=preprocessing,
    )


def run_controlled_comparison(
    dataset: ValidationDataset,
    manifest: ValidationRunManifest,
    *,
    parameters: ModelParameters,
    initial_engine_temp_c: float | None = None,
    fuel_lhv_j_per_kg: float | None = None,
) -> ComparisonResult:
    """Run calibration/holdout/challenge evidence under a locked provenance manifest.

    MAF-derived heat is intentionally prohibited here. Formal controlled evidence
    must use an explicit fuel-energy-rate channel or a fuel-rate channel with an
    explicitly supplied lower heating value.
    """

    dataset.validate()
    manifest.validate()
    parameters.validate()

    if manifest.role is ValidationRole.PLAUSIBILITY:
        raise ValueError("controlled comparison runner does not accept plausibility manifests")
    if dataset.dataset_id != manifest.dataset_id:
        raise ValueError(
            f"dataset_id mismatch: dataset={dataset.dataset_id!r}, manifest={manifest.dataset_id!r}"
        )

    source_sha = dataset.metadata.get("source_sha256")
    if source_sha is None:
        raise ValueError("controlled comparison requires source_sha256 in normalized dataset metadata")
    if source_sha != manifest.dataset_fingerprint.sha256_hex:
        raise ValueError("normalized dataset source SHA-256 does not match validation manifest")

    if manifest.preprocessing_snapshot_sha256 is not None:
        preprocessing_sha = dataset.metadata.get("signal_map_sha256")
        if preprocessing_sha != manifest.preprocessing_snapshot_sha256:
            raise ValueError("controlled comparison preprocessing snapshot does not match validation manifest")

    current_parameter_hash = sha256_mapping(parameters.snapshot())
    if current_parameter_hash != manifest.parameter_snapshot_sha256:
        raise ValueError("current parameter snapshot does not match validation manifest")

    if dataset.fuel_energy_rate_w is not None:
        fuel_energy_rate_w = np.asarray(dataset.fuel_energy_rate_w, dtype=float)
        heat_source = "explicit_fuel_energy_rate_channel"
        heat_metadata: dict[str, object] = {
            "heat_input_source": heat_source,
            "wall_heat_fraction": parameters.wall_heat_fraction,
            "maf_proxy_used": False,
        }
    elif dataset.fuel_rate_kg_s is not None:
        if fuel_lhv_j_per_kg is None or fuel_lhv_j_per_kg <= 0:
            raise ValueError(
                "fuel-rate controlled comparison requires an explicit positive fuel_lhv_j_per_kg"
            )
        fuel_energy_rate_w = np.asarray(dataset.fuel_rate_kg_s, dtype=float) * fuel_lhv_j_per_kg
        heat_source = "explicit_fuel_rate_channel_with_declared_lhv"
        heat_metadata = {
            "heat_input_source": heat_source,
            "fuel_lhv_j_per_kg": float(fuel_lhv_j_per_kg),
            "wall_heat_fraction": parameters.wall_heat_fraction,
            "maf_proxy_used": False,
        }
    else:
        raise ValueError(
            "controlled comparison requires fuel_energy_rate_w or fuel_rate_kg_s; "
            "MAF-derived heat is reserved for plausibility evidence"
        )

    q_engine = fuel_energy_rate_w * parameters.wall_heat_fraction
    _, rpm_metadata = _project_engine_speed_to_reference_domain(dataset.engine_speed_rpm)
    preprocessing = {"engine_speed_rpm": rpm_metadata}
    result, measured, predicted, metrics = _run_comparison(
        dataset,
        parameters,
        q_engine,
        scenario_id=f"VAL-{manifest.run_id}",
        scenario_name=f"VTMS controlled {manifest.role.value} comparison",
        initial_engine_temp_c=initial_engine_temp_c,
    )
    heat_metadata["engine_heat_status"] = "derived_from_explicit_fuel_energy_evidence"

    return ComparisonResult(
        dataset_id=dataset.dataset_id,
        comparison_time_s=dataset.time_s.copy(),
        measured_coolant_temp_c=measured.copy(),
        predicted_coolant_temp_c=predicted,
        residual_c=predicted - measured,
        metrics=metrics,
        simulation_result=result,
        heat_input_metadata=heat_metadata,
        evidence_label=manifest.evidence_grade.value,
        validation_manifest=manifest.to_dict(),
        input_preprocessing_metadata=preprocessing,
    )
