from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class ValidationMetrics:
    n: int
    rmse_c: float
    mae_c: float
    bias_c: float
    max_abs_error_c: float
    p90_abs_error_c: float
    final_error_c: float
    measured_final_c: float
    predicted_final_c: float
    threshold_arrival_error_s: dict[str, float | None]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _first_crossing(time_s: np.ndarray, values: np.ndarray, threshold: float) -> float | None:
    idx = np.flatnonzero(values >= threshold)
    if idx.size == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(time_s[0])
    t0, t1 = float(time_s[i - 1]), float(time_s[i])
    y0, y1 = float(values[i - 1]), float(values[i])
    if y1 == y0:
        return t1
    frac = (threshold - y0) / (y1 - y0)
    return t0 + frac * (t1 - t0)


def calculate_metrics(
    time_s: np.ndarray,
    measured_c: np.ndarray,
    predicted_c: np.ndarray,
    thresholds_c: tuple[float, ...] = (60.0, 80.0, 90.0),
) -> ValidationMetrics:
    if not (len(time_s) == len(measured_c) == len(predicted_c)):
        raise ValueError("time, measured, and predicted arrays must have equal length")
    if len(time_s) == 0:
        raise ValueError("at least one comparison sample is required")
    error = predicted_c - measured_c
    abs_error = np.abs(error)
    arrivals: dict[str, float | None] = {}
    for threshold in thresholds_c:
        measured_t = _first_crossing(time_s, measured_c, threshold)
        predicted_t = _first_crossing(time_s, predicted_c, threshold)
        key = f"{threshold:g}C"
        if measured_t is None or predicted_t is None:
            arrivals[key] = None
        else:
            arrivals[key] = float(predicted_t - measured_t)
    return ValidationMetrics(
        n=len(time_s),
        rmse_c=float(np.sqrt(np.mean(error**2))),
        mae_c=float(np.mean(abs_error)),
        bias_c=float(np.mean(error)),
        max_abs_error_c=float(np.max(abs_error)),
        p90_abs_error_c=float(np.percentile(abs_error, 90)),
        final_error_c=float(error[-1]),
        measured_final_c=float(measured_c[-1]),
        predicted_final_c=float(predicted_c[-1]),
        threshold_arrival_error_s=arrivals,
    )
