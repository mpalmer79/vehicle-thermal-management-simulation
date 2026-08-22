from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy

from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap
from vtms_v2.m2.stage_b import (
    GLOBAL_CASE_COUNT,
    HOT_INITIALIZATION_GRID,
    StageBCase,
    case_from_global_index,
    run_stage_b_case_reference,
)


EXPECTED_COLD_SHA256 = "4065b06eedefa5728ac6b8cb7c268f5f354021cf8bd98bf204dbdfcd74985e09"
EXPECTED_HOT_SHA256 = "8a1953112752e35ade720ab9a64201b05b37c70d172839234f12504e68f2aa8d"
COLD_MAP = Path("validation_configs/argonne_2012_focus_71207062_calibration.json")
HOT_MAP = Path("validation_configs/argonne_2012_focus_71207063_holdout.json")

_COLD_DATASET = None
_HOT_DATASET = None


def _load_dataset(source: Path, mapping_path: Path, expected_sha256: str):
    mapping = ArgonneSignalMap.from_json(mapping_path)
    dataset = ArgonneD3Adapter().load(source, mapping)
    actual = dataset.metadata.get("source_sha256")
    if actual != expected_sha256:
        raise ValueError(
            f"source SHA-256 mismatch for {source}: expected {expected_sha256}, got {actual}"
        )
    return dataset


def _init_worker(cold_source: str, hot_source: str) -> None:
    global _COLD_DATASET, _HOT_DATASET
    _COLD_DATASET = _load_dataset(Path(cold_source), COLD_MAP, EXPECTED_COLD_SHA256)
    _HOT_DATASET = _load_dataset(Path(hot_source), HOT_MAP, EXPECTED_HOT_SHA256)


def _compact_metrics(run) -> dict[str, object]:
    return {
        "rmse_c": run.metrics.rmse_c,
        "mae_c": run.metrics.mae_c,
        "bias_c": run.metrics.bias_c,
        "p90_abs_error_c": run.metrics.p90_abs_error_c,
        "final_error_c": run.metrics.final_error_c,
        "arrival_errors_s": run.acceptance.arrival_errors_s,
        "hot_region_mean_residual_c": run.acceptance.hot_region_mean_residual_c,
        "passed": run.acceptance.passed,
    }


def _evaluate_index(global_index: int) -> dict[str, object]:
    if _COLD_DATASET is None or _HOT_DATASET is None:
        raise RuntimeError("worker datasets were not initialized")
    case = case_from_global_index(global_index)
    cold = run_stage_b_case_reference(_COLD_DATASET, case)
    if not cold.acceptance.passed:
        return {
            "global_index": global_index,
            "cold_pass": False,
            "hot_evaluations": 0,
            "conditional_joint_survivor": False,
            "robust_joint_survivor": False,
        }

    hot_passes: list[dict[str, object]] = []
    for head_offset_c, block_offset_c, cold_offset_c in HOT_INITIALIZATION_GRID:
        hot = run_stage_b_case_reference(
            _HOT_DATASET,
            case,
            initial_head_offset_c=head_offset_c,
            initial_block_offset_c=block_offset_c,
            initial_cold_offset_c=cold_offset_c,
        )
        if hot.acceptance.passed:
            hot_passes.append(
                {
                    "head_offset_c": head_offset_c,
                    "block_offset_c": block_offset_c,
                    "cold_offset_c": cold_offset_c,
                    "metrics": _compact_metrics(hot),
                }
            )

    return {
        "global_index": global_index,
        "cold_pass": True,
        "cold_metrics": _compact_metrics(cold),
        "hot_evaluations": len(HOT_INITIALIZATION_GRID),
        "hot_pass_count": len(hot_passes),
        "hot_passes": hot_passes,
        "conditional_joint_survivor": len(hot_passes) > 0,
        "robust_joint_survivor": len(hot_passes) == len(HOT_INITIALIZATION_GRID),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Authoritative committed-source VTMS-V2 M2 Stage B independent executor."
    )
    parser.add_argument("--cold-source", type=Path, required=True)
    parser.add_argument("--hot-source", type=Path, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--runner-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if not 0 <= args.start < args.stop <= GLOBAL_CASE_COUNT:
        raise ValueError(
            f"range must satisfy 0 <= start < stop <= {GLOBAL_CASE_COUNT}"
        )
    if args.workers < 1:
        raise ValueError("workers must be >= 1")

    # Verify source identity once in the parent before any process is launched.
    cold = _load_dataset(args.cold_source, COLD_MAP, EXPECTED_COLD_SHA256)
    hot = _load_dataset(args.hot_source, HOT_MAP, EXPECTED_HOT_SHA256)
    del cold, hot

    started = time.perf_counter()
    indices = range(args.start, args.stop)
    if args.workers == 1:
        _init_worker(str(args.cold_source), str(args.hot_source))
        rows = [_evaluate_index(index) for index in indices]
    else:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=_init_worker,
            initargs=(str(args.cold_source), str(args.hot_source)),
        ) as executor:
            rows = list(executor.map(_evaluate_index, indices, chunksize=1))
    elapsed = time.perf_counter() - started

    cold_survivors = [row for row in rows if row["cold_pass"]]
    conditional = [row for row in rows if row["conditional_joint_survivor"]]
    robust = [row for row in rows if row["robust_joint_survivor"]]
    hot_evaluations = int(sum(int(row["hot_evaluations"]) for row in rows))

    payload = {
        "checkpoint_id": f"VTMS-V2-M2-STAGE-B-A2-{args.start}-{args.stop}",
        "status": "partial_authoritative_committed_source_stage_B_checkpoint_not_a_gate_decision",
        "model_id": "VTMS-V2-M2",
        "manifest_id": "VTMS-V2-M2-DEV-01",
        "numerical_execution_amendments": [
            "VTMS-V2-M2-NUMERICAL-EXECUTION-A1",
            "VTMS-V2-M2-NUMERICAL-EXECUTION-A2",
        ],
        "runner_commit": args.runner_commit,
        "runner_path": "scripts/run_m2_stage_b_independent.py",
        "stage_b_contract_path": "src/vtms_v2/m2/stage_b.py",
        "reserved_blind_evidence_used": False,
        "global_index_range": [args.start, args.stop],
        "coverage": "contiguous_complete_range",
        "configuration_count": args.stop - args.start,
        "cold_start_pass_count": len(cold_survivors),
        "cold_start_pass_indices": [int(row["global_index"]) for row in cold_survivors],
        "hot_start_configuration_initialization_evaluations": hot_evaluations,
        "conditional_joint_survivor_count": len(conditional),
        "conditional_joint_survivor_indices": [int(row["global_index"]) for row in conditional],
        "robust_joint_survivor_count": len(robust),
        "robust_joint_survivor_indices": [int(row["global_index"]) for row in robust],
        "cold_survivor_details": cold_survivors,
        "source_identity": {
            "cold_test_id": "71207062",
            "cold_sha256": EXPECTED_COLD_SHA256,
            "hot_test_id": "71207063",
            "hot_sha256": EXPECTED_HOT_SHA256,
        },
        "authoritative_numerics": {
            "one_scipy_solve_ivp_per_configuration": True,
            "solver": "RK45",
            "rtol": 1.0e-6,
            "atol": 1.0e-8,
            "max_step_s": 1.0,
            "output_interval_s": 1.0,
            "adaptive_controller_shared_between_configurations": False,
            "parallelism": "independent process parallelism only",
        },
        "execution_environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "workers": args.workers,
            "wall_time_s": elapsed,
        },
        "governance": {
            "parameter_optimizer_used": False,
            "parameter_ranges_changed": False,
            "hidden_initial_state_fitted": False,
            "dynamic_thermostat_added": False,
            "m2_rejected": False,
            "m3_authorized": False,
            "gate_decision_authorized_from_this_partial_checkpoint": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "range": [args.start, args.stop],
                "cold_passes": len(cold_survivors),
                "conditional_joint_survivors": len(conditional),
                "robust_joint_survivors": len(robust),
                "hot_evaluations": hot_evaluations,
                "wall_time_s": elapsed,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
