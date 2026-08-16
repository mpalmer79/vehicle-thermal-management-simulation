from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

import numpy as np

from .manifest import AcceptanceCriteria, ValidationRole, ValidationRunManifest
from .metrics import ValidationMetrics

if TYPE_CHECKING:
    from .runner import ComparisonResult


class AcceptanceStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_EVALUABLE = "not_evaluable"


@dataclass(frozen=True)
class AcceptanceCheck:
    check_id: str
    label: str
    status: AcceptanceStatus
    observed: float | None
    limit: float | None
    units: str
    note: str = ""

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class AcceptanceEvaluation:
    role: ValidationRole
    overall_threshold_pass: bool
    formal_validation_pass: bool
    claim_label: str
    checks: tuple[AcceptanceCheck, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "role": self.role.value,
            "overall_threshold_pass": self.overall_threshold_pass,
            "formal_validation_pass": self.formal_validation_pass,
            "claim_label": self.claim_label,
            "checks": [check.as_dict() for check in self.checks],
        }


def _first_crossing(time_s: np.ndarray, values: np.ndarray, threshold_c: float) -> float | None:
    idx = np.flatnonzero(values >= threshold_c)
    if idx.size == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(time_s[0])
    t0, t1 = float(time_s[i - 1]), float(time_s[i])
    y0, y1 = float(values[i - 1]), float(values[i])
    if y1 == y0:
        return t1
    frac = (threshold_c - y0) / (y1 - y0)
    return t0 + frac * (t1 - t0)


def _upper_limit_check(
    check_id: str,
    label: str,
    observed: float,
    limit: float,
    units: str,
) -> AcceptanceCheck:
    passed = observed <= limit
    return AcceptanceCheck(
        check_id=check_id,
        label=label,
        status=AcceptanceStatus.PASS if passed else AcceptanceStatus.FAIL,
        observed=float(observed),
        limit=float(limit),
        units=units,
    )


def evaluate_acceptance(
    comparison: "ComparisonResult",
    manifest: ValidationRunManifest,
    *,
    criteria: AcceptanceCriteria | None = None,
    thresholds_c: tuple[float, ...] = (60.0, 80.0, 90.0),
) -> AcceptanceEvaluation:
    """Evaluate a controlled comparison against the preregistered project criteria.

    The numeric criteria can be evaluated for calibration, holdout, or challenge
    runs, but only an independent holdout is eligible to produce a formal
    validation pass claim. Challenge runs remain challenge evidence even when
    every numeric threshold passes.
    """

    manifest.validate()
    if comparison.dataset_id != manifest.dataset_id:
        raise ValueError("comparison dataset_id does not match validation manifest")

    criteria = criteria or manifest.acceptance_criteria
    metrics: ValidationMetrics = comparison.metrics
    checks: list[AcceptanceCheck] = [
        _upper_limit_check("rmse", "RMSE", metrics.rmse_c, criteria.rmse_c_max, "degC"),
        _upper_limit_check("mae", "MAE", metrics.mae_c, criteria.mae_c_max, "degC"),
        _upper_limit_check(
            "abs_bias",
            "Absolute mean bias",
            abs(metrics.bias_c),
            criteria.abs_bias_c_max,
            "degC",
        ),
        _upper_limit_check(
            "p90_abs_error",
            "P90 absolute error",
            metrics.p90_abs_error_c,
            criteria.p90_abs_error_c_max,
            "degC",
        ),
    ]

    time_s = np.asarray(comparison.comparison_time_s, dtype=float)
    measured = np.asarray(comparison.measured_coolant_temp_c, dtype=float)
    predicted = np.asarray(comparison.predicted_coolant_temp_c, dtype=float)

    for threshold_c in thresholds_c:
        measured_t = _first_crossing(time_s, measured, threshold_c)
        predicted_t = _first_crossing(time_s, predicted, threshold_c)
        check_id = f"arrival_{threshold_c:g}c"
        label = f"{threshold_c:g} degC arrival-time error"

        if measured_t is None:
            checks.append(
                AcceptanceCheck(
                    check_id=check_id,
                    label=label,
                    status=AcceptanceStatus.NOT_EVALUABLE,
                    observed=None,
                    limit=None,
                    units="s",
                    note="Measured trace did not reach the threshold; timing acceptance is not applicable.",
                )
            )
            continue

        allowed_s = max(
            criteria.threshold_arrival_error_s_max,
            criteria.threshold_arrival_error_fraction_max * measured_t,
        )
        if predicted_t is None:
            checks.append(
                AcceptanceCheck(
                    check_id=check_id,
                    label=label,
                    status=AcceptanceStatus.FAIL,
                    observed=None,
                    limit=float(allowed_s),
                    units="s",
                    note="Measured trace reached the threshold but the prediction did not.",
                )
            )
            continue

        arrival_error_s = abs(predicted_t - measured_t)
        checks.append(
            _upper_limit_check(check_id, label, arrival_error_s, allowed_s, "s")
        )

    required = [check for check in checks if check.status is not AcceptanceStatus.NOT_EVALUABLE]
    overall_threshold_pass = bool(required) and all(
        check.status is AcceptanceStatus.PASS for check in required
    )
    formal_validation_pass = (
        manifest.role is ValidationRole.HOLDOUT and overall_threshold_pass
    )

    if manifest.role is ValidationRole.HOLDOUT:
        claim_label = (
            "formal_holdout_acceptance_pass"
            if formal_validation_pass
            else "formal_holdout_acceptance_fail"
        )
    elif manifest.role is ValidationRole.CALIBRATION:
        claim_label = (
            "calibration_fit_within_project_thresholds"
            if overall_threshold_pass
            else "calibration_fit_outside_project_thresholds"
        )
    elif manifest.role is ValidationRole.CHALLENGE:
        claim_label = (
            "challenge_within_project_thresholds"
            if overall_threshold_pass
            else "challenge_outside_project_thresholds"
        )
    else:
        claim_label = "plausibility_not_formal_acceptance"

    return AcceptanceEvaluation(
        role=manifest.role,
        overall_threshold_pass=overall_threshold_pass,
        formal_validation_pass=formal_validation_pass,
        claim_label=claim_label,
        checks=tuple(checks),
    )
