from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "validation_outputs" / "ARGONNE_VAL_HOT_01_FORMAL_RESULT.json"
PLAN_PATH = ROOT / "validation_configs" / "argonne_validation_plan.json"


def test_primary_physical_holdout_failure_is_frozen():
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    assert result["execution_identity"]["run_id"] == "VAL-HOT-01"
    assert result["execution_identity"]["source_test_id"] == "71207063"
    assert result["execution_identity"]["evidence_grade"] == "independent_holdout"
    assert result["execution_identity"]["physical_evidence"] is True
    assert result["execution_identity"]["parameter_fitting_performed"] is False
    assert result["acceptance"]["claim_label"] == "formal_holdout_acceptance_fail"
    assert result["acceptance"]["overall_threshold_pass"] is False
    assert result["acceptance"]["formal_validation_pass"] is False
    assert result["locks"]["retuning_after_result_permitted"] is False


def test_primary_holdout_metrics_remain_outside_project_criteria():
    metrics = json.loads(RESULT_PATH.read_text(encoding="utf-8"))["metrics"]

    assert metrics["rmse_c"] > 5.0
    assert metrics["mae_c"] > 4.0
    assert abs(metrics["bias_c"]) > 3.0
    assert metrics["p90_abs_error_c"] > 7.0
    assert metrics["threshold_arrival_error_s"]["60C"] is None
    assert metrics["threshold_arrival_error_s"]["80C"] is None
    assert metrics["threshold_arrival_error_s"]["90C"] > 60.0


def test_validation_plan_points_to_the_frozen_primary_holdout_result():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    run = next(item for item in plan["runs"] if item["run_id"] == "VAL-HOT-01")

    assert plan["formal_validation_status"].startswith("failed_primary_independent_holdout")
    assert run["execution_status"] == "executed_blind_failed_formal_acceptance"
    assert run["result_file"] == "../validation_outputs/ARGONNE_VAL_HOT_01_FORMAL_RESULT.json"
    assert run["claim_label"] == "formal_holdout_acceptance_fail"
    assert run["retuning_permitted"] is False
    assert plan["selection_audit"]["primary_holdout_triggered_retuning"] is False
