from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "validation_outputs" / "ARGONNE_VAL_SSS_01_CONFIRMATORY_RESULT.json"
PRIMARY_PATH = ROOT / "validation_outputs" / "ARGONNE_VAL_HOT_01_FORMAL_RESULT.json"
PLAN_PATH = ROOT / "validation_configs" / "argonne_validation_plan.json"


def test_secondary_confirmatory_holdout_failure_is_frozen_without_retuning():
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    assert result["execution_identity"]["run_id"] == "VAL-SSS-01"
    assert result["execution_identity"]["source_test_id"] == "71207052"
    assert result["execution_identity"]["parameter_fitting_performed"] is False
    assert result["acceptance"]["claim_label"] == "formal_holdout_acceptance_fail"
    assert result["acceptance"]["overall_threshold_pass"] is False
    assert result["acceptance"]["formal_validation_pass"] is False
    assert result["interpretation"]["retuning_permitted_after_result"] is False
    assert result["interpretation"]["secondary_result_may_overturn_primary_formal_failure"] is False


def test_secondary_failure_is_confirmatory_and_primary_formal_failure_remains_authoritative():
    secondary = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_PATH.read_text(encoding="utf-8"))

    assert primary["acceptance"]["claim_label"] == "formal_holdout_acceptance_fail"
    assert secondary["interpretation"]["primary_formal_validation_status_remains"] == "formal_holdout_acceptance_fail"
    assert secondary["metrics"]["rmse_c"] > 5.0
    assert secondary["metrics"]["mae_c"] > 4.0
    assert abs(secondary["metrics"]["bias_c"]) > 3.0
    assert secondary["metrics"]["p90_abs_error_c"] > 7.0
    assert secondary["metrics"]["threshold_arrival_error_s"]["80C"] < 60.0
    assert secondary["metrics"]["threshold_arrival_error_s"]["90C"] < 60.0


def test_validation_plan_records_both_independent_holdout_failures():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    primary = next(item for item in plan["runs"] if item["run_id"] == "VAL-HOT-01")
    secondary = next(item for item in plan["runs"] if item["run_id"] == "VAL-SSS-01")

    assert plan["formal_validation_status"] == "failed_primary_independent_holdout_confirmed_by_secondary_failure"
    assert primary["claim_label"] == "formal_holdout_acceptance_fail"
    assert secondary["claim_label"] == "formal_holdout_acceptance_fail"
    assert secondary["purpose"] == "confirmatory_generalization_evidence_only"
    assert secondary["primary_formal_failure_overturned"] is False
    assert plan["selection_audit"]["secondary_holdout_triggered_retuning"] is False
