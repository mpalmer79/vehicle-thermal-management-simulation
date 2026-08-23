from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

from vtms_validation.adapters.argonne import ArgonneD3Adapter, ArgonneSignalMap
from vtms_v2.m0.config import M0Parameters
from vtms_v2.m0.development import (
    constant_external_fan_boundary,
    feasibility_grid_points,
    parameters_for_grid_point,
    run_m0_development_comparison,
    summarize_feasibility,
)


def _find_source(root: Path, file_name: str) -> Path:
    matches = list(root.rglob(file_name))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected exactly one {file_name!r} below {root}, found {len(matches)}"
        )
    return matches[0]


def _load_dataset(
    *,
    root: Path,
    mapping_path: Path,
    expected_sha256: str,
):
    mapping = ArgonneSignalMap.from_json(mapping_path)
    source_file = _find_source(root, mapping.metadata["source_test_id"] + " Test Data.txt")
    dataset = ArgonneD3Adapter().load(source_file, mapping)
    actual_sha = dataset.metadata.get("source_sha256")
    if actual_sha != expected_sha256:
        raise ValueError(
            f"source SHA mismatch for {mapping.metadata['source_test_id']}: "
            f"expected {expected_sha256}, got {actual_sha}"
        )
    return dataset, mapping


def _fuel_lhv(mapping: ArgonneSignalMap) -> float:
    value = mapping.metadata.get("fuel_net_heating_value_j_per_kg_reference")
    if value is None or float(value) <= 0.0:
        raise ValueError("mapping lacks a positive fuel LHV reference")
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the preregistered VTMS-V2 M0 FEAS-01 consumed-development "
            "feasibility envelope. This script does not inspect reserved blind evidence "
            "and does not identify or rank physical parameter sets."
        )
    )
    parser.add_argument(
        "--argonne-dir",
        type=Path,
        required=True,
        help="Directory containing the recovered Argonne comprehensive test-data files.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("validation_configs/vtms_v2_m0_feasibility_plan.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for the aggregate JSON result.",
    )
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan.get("plan_id") != "VTMS-V2-M0-FEAS-01":
        raise ValueError("unexpected feasibility plan identity")
    if plan.get("status") != "frozen_before_execution":
        raise ValueError("FEAS-01 plan must be frozen before execution")
    if plan.get("reserved_blind_prediction_authorized") is not False:
        raise ValueError("FEAS-01 must not authorize reserved blind prediction")

    repository_root = args.plan.resolve().parents[1]
    loaded: dict[str, object] = {}
    mappings: dict[str, ArgonneSignalMap] = {}
    source_records: dict[str, dict[str, object]] = {}

    for record in plan["development_tests"]:
        test_id = str(record["test_id"])
        mapping_path = repository_root / str(record["mapping"])
        dataset, mapping = _load_dataset(
            root=args.argonne_dir,
            mapping_path=mapping_path,
            expected_sha256=str(record["source_sha256"]),
        )
        loaded[test_id] = dataset
        mappings[test_id] = mapping
        source_records[test_id] = {
            "dataset_id": dataset.dataset_id,
            "source_sha256": dataset.metadata["source_sha256"],
            "source_size_bytes": dataset.metadata["source_size_bytes"],
            "retained_rows": len(dataset.time_s),
            "duration_s": dataset.duration_s,
            "airflow_boundary_class": record["airflow_boundary_class"],
            "hood": record.get("hood"),
        }

    lhv_values = {_fuel_lhv(mapping) for mapping in mappings.values()}
    if len(lhv_values) != 1:
        raise ValueError(f"development mappings disagree on fuel LHV: {sorted(lhv_values)}")
    fuel_lhv = lhv_values.pop()

    thermal = plan["fixed_thermal_snapshot"]
    fixed = plan["fixed_m0_terms"]
    base_parameters = M0Parameters(
        wall_heat_fraction=float(thermal["wall_heat_fraction"]),
        engine_thermal_capacitance_j_per_k=float(
            thermal["engine_thermal_capacitance_j_per_k"]
        ),
        engine_coolant_ua_w_per_k=float(thermal["engine_coolant_ua_w_per_k"]),
        thermostat_open_c=float(fixed["thermostat_open_c"]),
        f_closed=float(fixed["f_closed"]),
        external_fan_capacity_m3_s=float(fixed["external_fan_capacity_m3_s"]),
        ags_static_restriction_factor=1.0,
    )
    base_parameters.validate()

    points = feasibility_grid_points(plan["non_optimized_design_grid"])
    expected_grid_size = int(plan["grid_size"])
    if len(points) != expected_grid_size:
        raise ValueError(
            f"frozen grid-size mismatch: plan={expected_grid_size}, generated={len(points)}"
        )

    boundary = constant_external_fan_boundary(
        capacity_m3_s=float(fixed["external_fan_capacity_m3_s"])
    )
    all_results: list[dict[str, object]] = []

    for point in points:
        parameters = parameters_for_grid_point(base_parameters, point)
        per_test: dict[str, object] = {}
        for test_id, dataset in loaded.items():
            per_test[test_id] = run_m0_development_comparison(
                dataset,
                parameters=parameters,
                airflow_boundary=boundary,
                fuel_lhv_j_per_kg=fuel_lhv,
            )
        all_results.append(per_test)

    summary = summarize_feasibility(points=points, results=all_results)
    payload = {
        "plan_id": plan["plan_id"],
        "status": "completed_consumed_development_feasibility_only",
        "physical_parameter_identification": False,
        "blind_prediction_inspected": False,
        "source_records": source_records,
        "fixed_thermal_snapshot": thermal,
        "fixed_m0_terms": fixed,
        "non_optimized_design_grid": plan["non_optimized_design_grid"],
        "summary": summary.as_dict(),
        "governance": {
            "best_fit_parameter_set_reported": False,
            "grid_points_ranked": False,
            "vehicle_specific_parameter_claim": False,
            "validation_claim": False,
        },
        "interpretation": plan["interpretation"],
    }

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
