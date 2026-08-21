from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class ResidualBin:
    lower: float
    upper: float
    count: int
    mean_residual_c: float | None
    mae_c: float | None
    rmse_c: float | None


@dataclass(frozen=True)
class TransitionWindow:
    threshold_c: float
    half_width_c: float
    count: int
    mean_residual_c: float | None
    mae_c: float | None
    rmse_c: float | None


@dataclass(frozen=True)
class ResidualCorrelation:
    name: str
    count: int
    pearson_r: float | None


@dataclass(frozen=True)
class ResidualDiagnosticReport:
    count: int
    mean_residual_c: float
    mae_c: float
    rmse_c: float
    max_abs_residual_c: float
    bias_fraction_of_mse: float
    positive_fraction: float
    negative_fraction: float
    temperature_bins: tuple[ResidualBin, ...]
    thermostat_transition: TransitionWindow
    correlations: tuple[ResidualCorrelation, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _as_vector(name: str, values: Iterable[float]) -> np.ndarray:
    vector = np.asarray(list(values), dtype=float)
    if vector.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def _validate_aligned(reference: np.ndarray, name: str, values: np.ndarray) -> None:
    if values.shape != reference.shape:
        raise ValueError(
            f"{name} must have shape {reference.shape}, got {values.shape}"
        )


def _metrics(values: np.ndarray) -> tuple[float | None, float | None, float | None]:
    if values.size == 0:
        return None, None, None
    mean = float(np.mean(values))
    mae = float(np.mean(np.abs(values)))
    rmse = float(np.sqrt(np.mean(values * values)))
    return mean, mae, rmse


def _safe_pearson(x: np.ndarray, y: np.ndarray) -> float | None:
    if x.size < 3 or y.size < 3:
        return None
    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)
    denom = float(
        np.sqrt(np.sum(x_centered * x_centered) * np.sum(y_centered * y_centered))
    )
    if denom <= np.finfo(float).eps:
        return None
    return float(np.sum(x_centered * y_centered) / denom)


def _bin_residuals(
    independent: np.ndarray,
    residual: np.ndarray,
    edges: np.ndarray,
) -> tuple[ResidualBin, ...]:
    if edges.ndim != 1 or edges.size < 2:
        raise ValueError("bin edges must contain at least two values")
    if np.any(np.diff(edges) <= 0):
        raise ValueError("bin edges must be strictly increasing")

    result: list[ResidualBin] = []
    for index in range(edges.size - 1):
        lower = float(edges[index])
        upper = float(edges[index + 1])
        if index == edges.size - 2:
            mask = (independent >= lower) & (independent <= upper)
        else:
            mask = (independent >= lower) & (independent < upper)
        selected = residual[mask]
        mean, mae, rmse = _metrics(selected)
        result.append(
            ResidualBin(
                lower=lower,
                upper=upper,
                count=int(selected.size),
                mean_residual_c=mean,
                mae_c=mae,
                rmse_c=rmse,
            )
        )
    return tuple(result)


def analyze_residuals(
    *,
    measured_coolant_temp_c: Iterable[float],
    predicted_coolant_temp_c: Iterable[float],
    engine_speed_rpm: Iterable[float] | None = None,
    vehicle_speed_m_s: Iterable[float] | None = None,
    fuel_energy_rate_w: Iterable[float] | None = None,
    engine_load_fraction: Iterable[float] | None = None,
    thermostat_open_c: float = 88.0,
    thermostat_full_c: float = 98.0,
    thermostat_transition_half_width_c: float = 2.0,
    temperature_bin_edges_c: Iterable[float] = (0.0, 60.0, 80.0, 88.0, 98.0, 105.0, 130.0),
) -> ResidualDiagnosticReport:
    """Summarize time-series residual structure without fitting model parameters.

    Residual sign follows the VTMS validation convention:
    ``predicted - measured``. Negative residuals therefore mean VTMS is
    underpredicting coolant temperature.

    This function is diagnostic only. It must not be used to modify a frozen
    validation holdout or to authorize post-hoc fitting to consumed holdout data.
    """

    measured = _as_vector("measured_coolant_temp_c", measured_coolant_temp_c)
    predicted = _as_vector("predicted_coolant_temp_c", predicted_coolant_temp_c)
    _validate_aligned(measured, "predicted_coolant_temp_c", predicted)

    residual = predicted - measured
    mse = float(np.mean(residual * residual))
    bias = float(np.mean(residual))
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(mse))
    bias_fraction = 0.0 if mse <= np.finfo(float).eps else float((bias * bias) / mse)

    temperature_edges = _as_vector("temperature_bin_edges_c", temperature_bin_edges_c)
    temperature_bins = _bin_residuals(measured, residual, temperature_edges)

    transition_low = thermostat_open_c - thermostat_transition_half_width_c
    transition_high = thermostat_full_c + thermostat_transition_half_width_c
    transition_mask = (measured >= transition_low) & (measured <= transition_high)
    transition_values = residual[transition_mask]
    transition_mean, transition_mae, transition_rmse = _metrics(transition_values)
    transition = TransitionWindow(
        threshold_c=(thermostat_open_c + thermostat_full_c) / 2.0,
        half_width_c=(transition_high - transition_low) / 2.0,
        count=int(transition_values.size),
        mean_residual_c=transition_mean,
        mae_c=transition_mae,
        rmse_c=transition_rmse,
    )

    correlations: list[ResidualCorrelation] = []
    candidates = {
        "measured_coolant_temp_c": measured,
        "engine_speed_rpm": engine_speed_rpm,
        "vehicle_speed_m_s": vehicle_speed_m_s,
        "fuel_energy_rate_w": fuel_energy_rate_w,
        "engine_load_fraction": engine_load_fraction,
    }
    for name, raw_values in candidates.items():
        if raw_values is None:
            continue
        values = measured if name == "measured_coolant_temp_c" else _as_vector(name, raw_values)
        _validate_aligned(measured, name, values)
        correlations.append(
            ResidualCorrelation(
                name=name,
                count=int(values.size),
                pearson_r=_safe_pearson(values, residual),
            )
        )

    return ResidualDiagnosticReport(
        count=int(residual.size),
        mean_residual_c=bias,
        mae_c=mae,
        rmse_c=rmse,
        max_abs_residual_c=float(np.max(np.abs(residual))),
        bias_fraction_of_mse=bias_fraction,
        positive_fraction=float(np.mean(residual > 0.0)),
        negative_fraction=float(np.mean(residual < 0.0)),
        temperature_bins=temperature_bins,
        thermostat_transition=transition,
        correlations=tuple(correlations),
    )
