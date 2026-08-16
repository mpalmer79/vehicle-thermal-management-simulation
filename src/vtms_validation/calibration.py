from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Mapping

import numpy as np
from scipy.optimize import least_squares

from vtms_v1.config import ModelParameters

from .acceptance import AcceptanceEvaluation, evaluate_acceptance
from .dataset import ValidationDataset
from .manifest import ValidationRunManifest, sha256_mapping
from .runner import ComparisonResult, _run_comparison


@dataclass(frozen=True)
class ParameterBound:
    name: str
    lower: float
    upper: float

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("calibration bound requires a parameter name")
        if not np.isfinite(self.lower) or not np.isfinite(self.upper):
            raise ValueError(f"calibration bound for {self.name} must be finite")
        if self.lower >= self.upper:
            raise ValueError(f"calibration bound for {self.name} requires lower < upper")


@dataclass(frozen=True)
class CalibrationBounds:
    parameters: tuple[ParameterBound, ...]

    def validate(
        self,
        manifest: ValidationRunManifest,
        initial_parameters: ModelParameters,
    ) -> None:
        manifest.validate()
        initial_parameters.validate()
        names = [bound.name for bound in self.parameters]
        if len(names) != len(set(names)):
            raise ValueError("calibration bounds contain duplicate parameter names")
        if set(names) != set(manifest.calibration_parameters):
            raise ValueError(
                "calibration bounds must exactly match the parameters declared by the calibration manifest"
            )
        for bound in self.parameters:
            bound.validate()
            value = float(getattr(initial_parameters, bound.name))
            if not bound.lower <= value <= bound.upper:
                raise ValueError(
                    f"initial value for {bound.name}={value} lies outside [{bound.lower}, {bound.upper}]"
                )

    def ordered(self, names: tuple[str, ...]) -> tuple[ParameterBound, ...]:
        by_name = {bound.name: bound for bound in self.parameters}
        return tuple(by_name[name] for name in names)

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {
            bound.name: {"lower": float(bound.lower), "upper": float(bound.upper)}
            for bound in self.parameters
        }


@dataclass(frozen=True)
class CalibratedParameter:
    name: str
    initial: float
    fitted: float
    lower: float
    upper: float


@dataclass(frozen=True)
class BoundedCalibrationResult:
    success: bool
    optimizer_status: int
    optimizer_message: str
    nfev: int
    initial_cost: float
    final_cost: float
    initial_parameter_snapshot_sha256: str
    calibrated_parameter_snapshot_sha256: str
    parameters: tuple[CalibratedParameter, ...]
    calibrated_model_parameters: ModelParameters
    comparison: ComparisonResult
    acceptance: AcceptanceEvaluation

    def as_dict(self) -> dict[str, object]:
        return {
            "success": self.success,
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "nfev": self.nfev,
            "initial_cost": self.initial_cost,
            "final_cost": self.final_cost,
            "initial_parameter_snapshot_sha256": self.initial_parameter_snapshot_sha256,
            "calibrated_parameter_snapshot_sha256": self.calibrated_parameter_snapshot_sha256,
            "parameters": [asdict(parameter) for parameter in self.parameters],
            "calibrated_model_parameters": self.calibrated_model_parameters.snapshot(),
            "metrics": self.comparison.metrics.as_dict(),
            "acceptance": self.acceptance.as_dict(),
        }


def _fuel_energy_rate(dataset: ValidationDataset, fuel_lhv_j_per_kg: float | None) -> np.ndarray:
    if dataset.fuel_energy_rate_w is not None:
        return np.asarray(dataset.fuel_energy_rate_w, dtype=float)
    if dataset.fuel_rate_kg_s is not None:
        if fuel_lhv_j_per_kg is None or fuel_lhv_j_per_kg <= 0:
            raise ValueError("bounded calibration with fuel_rate_kg_s requires a positive fuel_lhv_j_per_kg")
        return np.asarray(dataset.fuel_rate_kg_s, dtype=float) * float(fuel_lhv_j_per_kg)
    raise ValueError(
        "bounded calibration requires fuel_energy_rate_w or fuel_rate_kg_s; MAF proxy evidence is not allowed"
    )


def _with_parameter_vector(
    base: ModelParameters,
    names: tuple[str, ...],
    vector: np.ndarray,
) -> ModelParameters:
    updates = {name: float(value) for name, value in zip(names, vector, strict=True)}
    candidate = replace(base, **updates)
    candidate.validate()
    return candidate


def run_bounded_calibration(
    dataset: ValidationDataset,
    manifest: ValidationRunManifest,
    *,
    initial_parameters: ModelParameters,
    bounds: CalibrationBounds,
    initial_engine_temp_c: float | None = None,
    fuel_lhv_j_per_kg: float | None = None,
    max_nfev: int = 80,
) -> BoundedCalibrationResult:
    """Fit only manifest-authorized parameters inside explicit caller-supplied bounds.

    This function does not provide physical calibration bounds. The caller must
    preregister them. The synthetic harness supplies its own test-only bounds,
    which are explicitly prohibited from being treated as future Argonne bounds.
    """

    dataset.validate()
    manifest.validate()
    initial_parameters.validate()
    if max_nfev <= 0:
        raise ValueError("max_nfev must be positive")

    fit_names = tuple(manifest.calibration_parameters)
    manifest.assert_parameter_fit_allowed(fit_names)
    bounds.validate(manifest, initial_parameters)

    initial_hash = sha256_mapping(initial_parameters.snapshot())
    if initial_hash != manifest.parameter_snapshot_sha256:
        raise ValueError("initial parameter snapshot does not match calibration manifest")

    source_sha = dataset.metadata.get("source_sha256")
    if source_sha != manifest.dataset_fingerprint.sha256_hex:
        raise ValueError("calibration dataset source SHA-256 does not match validation manifest")

    fuel_energy_rate_w = _fuel_energy_rate(dataset, fuel_lhv_j_per_kg)
    ordered_bounds = bounds.ordered(fit_names)
    x0 = np.asarray([float(getattr(initial_parameters, name)) for name in fit_names], dtype=float)
    lower = np.asarray([bound.lower for bound in ordered_bounds], dtype=float)
    upper = np.asarray([bound.upper for bound in ordered_bounds], dtype=float)

    def residual(vector: np.ndarray) -> np.ndarray:
        candidate = _with_parameter_vector(initial_parameters, fit_names, vector)
        q_engine_w = fuel_energy_rate_w * candidate.wall_heat_fraction
        _, measured, predicted, _ = _run_comparison(
            dataset,
            candidate,
            q_engine_w,
            scenario_id=f"CAL-OPT-{manifest.run_id}",
            scenario_name="VTMS bounded calibration candidate",
            initial_engine_temp_c=initial_engine_temp_c,
        )
        return predicted - measured

    initial_residual = residual(x0)
    initial_cost = 0.5 * float(np.dot(initial_residual, initial_residual))
    solution = least_squares(
        residual,
        x0,
        bounds=(lower, upper),
        x_scale="jac",
        max_nfev=max_nfev,
        ftol=1.0e-8,
        xtol=1.0e-8,
        gtol=1.0e-8,
    )

    calibrated = _with_parameter_vector(initial_parameters, fit_names, solution.x)
    q_engine_w = fuel_energy_rate_w * calibrated.wall_heat_fraction
    simulation_result, measured, predicted, metrics = _run_comparison(
        dataset,
        calibrated,
        q_engine_w,
        scenario_id=f"CAL-FINAL-{manifest.run_id}",
        scenario_name="VTMS bounded calibration final fit",
        initial_engine_temp_c=initial_engine_temp_c,
    )
    comparison = ComparisonResult(
        dataset_id=dataset.dataset_id,
        comparison_time_s=dataset.time_s.copy(),
        measured_coolant_temp_c=measured.copy(),
        predicted_coolant_temp_c=predicted,
        residual_c=predicted - measured,
        metrics=metrics,
        simulation_result=simulation_result,
        heat_input_metadata={
            "heat_input_source": "explicit_fuel_energy_evidence",
            "wall_heat_fraction": calibrated.wall_heat_fraction,
            "maf_proxy_used": False,
            "calibration_execution": True,
        },
        evidence_label=manifest.evidence_grade.value,
        validation_manifest=manifest.to_dict(),
    )
    acceptance = evaluate_acceptance(comparison, manifest)
    calibrated_hash = sha256_mapping(calibrated.snapshot())

    fitted = tuple(
        CalibratedParameter(
            name=name,
            initial=float(getattr(initial_parameters, name)),
            fitted=float(getattr(calibrated, name)),
            lower=float(bound.lower),
            upper=float(bound.upper),
        )
        for name, bound in zip(fit_names, ordered_bounds, strict=True)
    )

    return BoundedCalibrationResult(
        success=bool(solution.success),
        optimizer_status=int(solution.status),
        optimizer_message=str(solution.message),
        nfev=int(solution.nfev),
        initial_cost=initial_cost,
        final_cost=float(solution.cost),
        initial_parameter_snapshot_sha256=initial_hash,
        calibrated_parameter_snapshot_sha256=calibrated_hash,
        parameters=fitted,
        calibrated_model_parameters=calibrated,
        comparison=comparison,
        acceptance=acceptance,
    )
