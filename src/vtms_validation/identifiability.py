from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import math
from typing import Mapping, Sequence

import numpy as np

from vtms_v1.config import ModelParameters

from .dataset import ValidationDataset
from .manifest import ALLOWED_CALIBRATION_PARAMETERS
from .runner import _run_comparison


_HIGH_COSINE_SIMILARITY = 0.95
_ILL_CONDITIONED_THRESHOLD = 100.0


@dataclass(frozen=True)
class ParameterSensitivity:
    name: str
    baseline_value: float
    relative_step: float
    rms_c_per_fractional_change: float
    max_abs_c_per_fractional_change: float
    l2_norm_c_per_fractional_change: float


@dataclass(frozen=True)
class PairwiseSensitivity:
    parameter_a: str
    parameter_b: str
    cosine_similarity: float
    absolute_cosine_similarity: float


@dataclass(frozen=True)
class IdentifiabilityDiagnostics:
    dataset_ids: tuple[str, ...]
    parameter_names: tuple[str, ...]
    relative_step: float
    sample_count: int
    sensitivities: tuple[ParameterSensitivity, ...]
    pairwise: tuple[PairwiseSensitivity, ...]
    singular_values: tuple[float, ...]
    normalized_singular_values: tuple[float, ...]
    numerical_rank: int
    condition_number: float | None
    strongest_confounding_pair: PairwiseSensitivity | None
    diagnostic_flags: tuple[str, ...]
    assessment: str
    disclaimer: str
    sensitivity_matrix: np.ndarray = field(repr=False, compare=False)

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_ids": list(self.dataset_ids),
            "parameter_names": list(self.parameter_names),
            "relative_step": self.relative_step,
            "sample_count": self.sample_count,
            "sensitivities": [asdict(item) for item in self.sensitivities],
            "pairwise": [asdict(item) for item in self.pairwise],
            "singular_values": list(self.singular_values),
            "normalized_singular_values": list(self.normalized_singular_values),
            "numerical_rank": self.numerical_rank,
            "condition_number": self.condition_number,
            "strongest_confounding_pair": (
                None if self.strongest_confounding_pair is None else asdict(self.strongest_confounding_pair)
            ),
            "diagnostic_flags": list(self.diagnostic_flags),
            "assessment": self.assessment,
            "disclaimer": self.disclaimer,
        }


def _require_synthetic_dataset(dataset: ValidationDataset) -> None:
    dataset.validate()
    if dataset.metadata.get("synthetic") is not True:
        raise ValueError(
            "pre-Argonne identifiability diagnostics are synthetic-only; physical datasets are prohibited"
        )
    if dataset.metadata.get("physical_validation_evidence") is not False:
        raise ValueError(
            "synthetic identifiability dataset must explicitly declare physical_validation_evidence=false"
        )
    if dataset.fuel_energy_rate_w is None:
        raise ValueError(
            "synthetic identifiability requires the deterministic fuel_energy_rate_w channel"
        )


def _prediction(
    dataset: ValidationDataset,
    parameters: ModelParameters,
    *,
    initial_engine_temp_c: float | None,
    scenario_suffix: str,
) -> np.ndarray:
    fuel_energy_rate_w = np.asarray(dataset.fuel_energy_rate_w, dtype=float)
    q_engine_w = fuel_energy_rate_w * parameters.wall_heat_fraction
    _, _, predicted, _ = _run_comparison(
        dataset,
        parameters,
        q_engine_w,
        scenario_id=f"SYN-ID-{dataset.dataset_id}-{scenario_suffix}",
        scenario_name="Synthetic local identifiability perturbation",
        initial_engine_temp_c=initial_engine_temp_c,
    )
    return np.asarray(predicted, dtype=float)


def _initial_engine_temperature(
    dataset: ValidationDataset,
    overrides: Mapping[str, float] | None,
) -> float | None:
    if overrides is not None and dataset.dataset_id in overrides:
        return float(overrides[dataset.dataset_id])
    value = dataset.metadata.get("initial_engine_temp_c")
    return None if value is None else float(value)


def _normalized_local_sensitivity(
    datasets: Sequence[ValidationDataset],
    parameters: ModelParameters,
    parameter_name: str,
    relative_step: float,
    initial_engine_temp_c_by_dataset: Mapping[str, float] | None,
) -> np.ndarray:
    baseline = float(getattr(parameters, parameter_name))
    if baseline == 0.0:
        raise ValueError(f"cannot form a relative perturbation around zero for {parameter_name}")

    lower_value = baseline * (1.0 - relative_step)
    upper_value = baseline * (1.0 + relative_step)
    lower = replace(parameters, **{parameter_name: lower_value})
    upper = replace(parameters, **{parameter_name: upper_value})
    lower.validate()
    upper.validate()

    blocks: list[np.ndarray] = []
    for dataset in datasets:
        initial_engine_temp_c = _initial_engine_temperature(
            dataset, initial_engine_temp_c_by_dataset
        )
        predicted_lower = _prediction(
            dataset,
            lower,
            initial_engine_temp_c=initial_engine_temp_c,
            scenario_suffix=f"{parameter_name}-minus",
        )
        predicted_upper = _prediction(
            dataset,
            upper,
            initial_engine_temp_c=initial_engine_temp_c,
            scenario_suffix=f"{parameter_name}-plus",
        )
        # The perturbation is expressed as a fractional change in the parameter.
        # This is approximately p_j * dT_c/dp_j and therefore places parameters
        # with different engineering units on a comparable local scale.
        blocks.append((predicted_upper - predicted_lower) / (2.0 * relative_step))
    return np.concatenate(blocks)


def _pairwise_diagnostics(
    matrix: np.ndarray,
    parameter_names: tuple[str, ...],
) -> tuple[PairwiseSensitivity, ...]:
    items: list[PairwiseSensitivity] = []
    for left in range(len(parameter_names)):
        for right in range(left + 1, len(parameter_names)):
            a = matrix[:, left]
            b = matrix[:, right]
            norm_product = float(np.linalg.norm(a) * np.linalg.norm(b))
            cosine = 0.0 if norm_product == 0.0 else float(np.dot(a, b) / norm_product)
            cosine = float(np.clip(cosine, -1.0, 1.0))
            items.append(
                PairwiseSensitivity(
                    parameter_a=parameter_names[left],
                    parameter_b=parameter_names[right],
                    cosine_similarity=cosine,
                    absolute_cosine_similarity=abs(cosine),
                )
            )
    return tuple(items)


def analyze_synthetic_identifiability(
    datasets: ValidationDataset | Sequence[ValidationDataset],
    *,
    parameters: ModelParameters | None = None,
    parameter_names: tuple[str, ...] = tuple(ALLOWED_CALIBRATION_PARAMETERS),
    relative_step: float = 0.01,
    initial_engine_temp_c_by_dataset: Mapping[str, float] | None = None,
) -> IdentifiabilityDiagnostics:
    """Evaluate local practical identifiability using synthetic coolant traces only.

    The returned matrix contains normalized central finite-difference sensitivities
    of predicted coolant temperature to fractional changes in each parameter. The
    diagnostic intentionally refuses physical datasets so this pre-fit work cannot
    inspect Argonne model residuals or influence role selection before bounds are frozen.

    The 0.95 pairwise cosine and condition-number 100 flags are VTMS diagnostic
    heuristics, not published validation standards or acceptance criteria.
    """

    if isinstance(datasets, ValidationDataset):
        dataset_sequence = (datasets,)
    else:
        dataset_sequence = tuple(datasets)
    if not dataset_sequence:
        raise ValueError("identifiability analysis requires at least one synthetic dataset")
    if not 0.0 < relative_step < 0.25:
        raise ValueError("relative_step must be between 0 and 0.25")
    if not parameter_names:
        raise ValueError("parameter_names cannot be empty")
    if len(parameter_names) != len(set(parameter_names)):
        raise ValueError("parameter_names contain duplicates")
    if set(parameter_names) != set(ALLOWED_CALIBRATION_PARAMETERS):
        raise ValueError(
            "pre-Argonne identifiability must analyze exactly the frozen calibration subset"
        )

    model_parameters = parameters or ModelParameters()
    model_parameters.validate()
    for dataset in dataset_sequence:
        _require_synthetic_dataset(dataset)

    columns = [
        _normalized_local_sensitivity(
            dataset_sequence,
            model_parameters,
            name,
            relative_step,
            initial_engine_temp_c_by_dataset,
        )
        for name in parameter_names
    ]
    sensitivity_matrix = np.column_stack(columns)

    sensitivities = tuple(
        ParameterSensitivity(
            name=name,
            baseline_value=float(getattr(model_parameters, name)),
            relative_step=relative_step,
            rms_c_per_fractional_change=float(np.sqrt(np.mean(column**2))),
            max_abs_c_per_fractional_change=float(np.max(np.abs(column))),
            l2_norm_c_per_fractional_change=float(np.linalg.norm(column)),
        )
        for name, column in zip(parameter_names, columns, strict=True)
    )

    pairwise = _pairwise_diagnostics(sensitivity_matrix, parameter_names)
    strongest_pair = max(pairwise, key=lambda item: item.absolute_cosine_similarity, default=None)

    column_norms = np.linalg.norm(sensitivity_matrix, axis=0)
    normalized_matrix = np.zeros_like(sensitivity_matrix)
    nonzero = column_norms > np.finfo(float).eps
    normalized_matrix[:, nonzero] = sensitivity_matrix[:, nonzero] / column_norms[nonzero]

    singular_values_array = np.linalg.svd(normalized_matrix, compute_uv=False)
    singular_values = tuple(float(value) for value in singular_values_array)
    largest = float(singular_values_array[0]) if singular_values_array.size else 0.0
    smallest = float(singular_values_array[-1]) if singular_values_array.size else 0.0
    normalized_singular_values = tuple(
        0.0 if largest == 0.0 else float(value / largest) for value in singular_values_array
    )
    numerical_rank = int(np.linalg.matrix_rank(normalized_matrix))
    condition_number = None
    if largest > 0.0 and smallest > np.finfo(float).eps * largest:
        condition_number = float(largest / smallest)
        if not math.isfinite(condition_number):
            condition_number = None

    flags: list[str] = []
    zero_columns = [name for name, active in zip(parameter_names, nonzero, strict=True) if not active]
    for name in zero_columns:
        flags.append(f"zero_local_sensitivity:{name}")
    if numerical_rank < len(parameter_names):
        flags.append(
            f"rank_deficient_normalized_jacobian:{numerical_rank}_of_{len(parameter_names)}"
        )
    if condition_number is None:
        flags.append("singular_or_numerically_singular_normalized_jacobian")
    elif condition_number >= _ILL_CONDITIONED_THRESHOLD:
        flags.append(f"ill_conditioned_normalized_jacobian:{condition_number:.3g}")
    for item in pairwise:
        if item.absolute_cosine_similarity >= _HIGH_COSINE_SIMILARITY:
            flags.append(
                "high_shape_similarity:"
                f"{item.parameter_a}:{item.parameter_b}:{item.absolute_cosine_similarity:.4f}"
            )

    assessment = (
        "diagnostic_confounding_detected"
        if flags
        else "no_strong_confounding_detected_at_local_synthetic_point"
    )
    return IdentifiabilityDiagnostics(
        dataset_ids=tuple(dataset.dataset_id for dataset in dataset_sequence),
        parameter_names=parameter_names,
        relative_step=relative_step,
        sample_count=int(sensitivity_matrix.shape[0]),
        sensitivities=sensitivities,
        pairwise=pairwise,
        singular_values=singular_values,
        normalized_singular_values=normalized_singular_values,
        numerical_rank=numerical_rank,
        condition_number=condition_number,
        strongest_confounding_pair=strongest_pair,
        diagnostic_flags=tuple(flags),
        assessment=assessment,
        disclaimer=(
            "Synthetic local sensitivity diagnostics are software and parameter-separation evidence only. "
            "They do not establish physical parameter bounds, model validity, vehicle accuracy, or an "
            "Argonne calibration result. Physical datasets are deliberately rejected by this function."
        ),
        sensitivity_matrix=sensitivity_matrix,
    )
