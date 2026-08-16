from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.normalized import load_normalized_sample_csv
from vtms_validation.heat_input import MafStoichiometricHeatEstimator
from vtms_validation.runner import run_kit_plausibility

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "validation_data" / "KIT_2018-02-20_Seat_Leon_KA_KA_Frei_sample_60s.csv"
OUT = ROOT / "validation_outputs"
OUT.mkdir(exist_ok=True)


def main() -> None:
    dataset = load_normalized_sample_csv(
        DATA,
        dataset_id="KIT-2018-02-20-KA-KA-FREI-60S",
        source_name="KIT Automotive OBD-II Dataset",
    )
    parameters = ModelParameters()
    estimator = MafStoichiometricHeatEstimator(wall_heat_fraction=parameters.wall_heat_fraction)
    q_engine = np.asarray(estimator.engine_heat_w(dataset.mass_air_flow_g_s), dtype=float)
    comparison = run_kit_plausibility(dataset, parameters=parameters, estimator=estimator)

    comparison_csv = OUT / "KIT_2018-02-20_plausibility_comparison.csv"
    with comparison_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_s",
                "measured_coolant_temp_c",
                "predicted_coolant_temp_c",
                "residual_pred_minus_meas_c",
                "rpm",
                "vehicle_speed_m_s",
                "ambient_temp_c",
                "maf_g_s",
                "derived_engine_heat_w",
            ]
        )
        for i, time_s in enumerate(dataset.time_s):
            writer.writerow(
                [
                    f"{time_s:.3f}",
                    f"{dataset.measured_coolant_temp_c[i]:.6f}",
                    f"{comparison.predicted_coolant_temp_c[i]:.6f}",
                    f"{comparison.residual_c[i]:.6f}",
                    f"{dataset.engine_speed_rpm[i]:.6f}",
                    f"{dataset.vehicle_speed_m_s[i]:.6f}",
                    f"{dataset.ambient_temp_c[i]:.6f}",
                    f"{dataset.mass_air_flow_g_s[i]:.6f}",
                    f"{q_engine[i]:.6f}",
                ]
            )

    payload = {
        "evidence_label": comparison.evidence_label,
        "dataset": {
            "dataset_id": dataset.dataset_id,
            "source_name": dataset.source_name,
            "duration_s": dataset.duration_s,
            "samples": len(dataset.time_s),
            "metadata": dataset.metadata,
        },
        "model": comparison.simulation_result.model_metadata,
        "parameter_snapshot": comparison.simulation_result.parameter_snapshot,
        "heat_input": comparison.heat_input_metadata,
        "metrics": comparison.metrics.as_dict(),
        "interpretation_rules": {
            "formal_validation": False,
            "parameters_recalibrated": False,
            "acceptance_criteria_applied": False,
            "reason": "KIT run is a coarse external plausibility check using 60-second samples and MAF-derived heat input, not controlled dynamometer validation.",
        },
    }
    (OUT / "KIT_2018-02-20_plausibility_metrics.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    m = comparison.metrics
    report = f"""# KIT External Plausibility Comparison\n\n## Classification\n\n**External plausibility check only. Not formal VTMS validation.**\n\nVTMS-V1 parameters were not changed or calibrated for this comparison. The source is a real KIT Seat Leon OBD-II drive, represented here by 60-second samples extracted from the source CSV. Engine heat input is not measured. It is estimated from measured mass-air flow using a fixed 14.7:1 air-fuel mass ratio, gasoline lower heating value of 43.7 MJ/kg, and the frozen VTMS wall-heat fraction of 0.28.\n\n## Results\n\n- Samples: {m.n}\n- Duration: {dataset.duration_s:.0f} s\n- RMSE: {m.rmse_c:.2f} °C\n- MAE: {m.mae_c:.2f} °C\n- Bias (predicted minus measured): {m.bias_c:.2f} °C\n- Maximum absolute error: {m.max_abs_error_c:.2f} °C\n- 90th-percentile absolute error: {m.p90_abs_error_c:.2f} °C\n- Final measured coolant temperature: {m.measured_final_c:.2f} °C\n- Final predicted coolant temperature: {m.predicted_final_c:.2f} °C\n- Final error: {m.final_error_c:.2f} °C\n- 60 °C arrival error: {m.threshold_arrival_error_s['60C']} s\n- 80 °C arrival error: {m.threshold_arrival_error_s['80C']} s\n- 90 °C arrival error: {m.threshold_arrival_error_s['90C']} s\n\n## What this can tell us\n\nThis comparison can reveal order-of-magnitude warm-up errors, directional inconsistencies, adapter problems, and gross mismatches between generic VTMS behavior and a real vehicle temperature trajectory.\n\n## What this cannot tell us\n\nIt cannot establish vehicle-specific physical accuracy. The Seat Leon is not the generic VTMS reference vehicle, heat input is derived rather than directly measured, the data used here are coarse 60-second samples, HVAC state is unknown, and the source is a road drive rather than a controlled dynamometer test. The preregistered Argonne protocol remains the formal validation path.\n"""
    (OUT / "KIT_2018-02-20_PLAUSIBILITY_REPORT.md").write_text(report, encoding="utf-8")

    print(report)
    print(f"Comparison CSV: {comparison_csv}")


if __name__ == "__main__":
    main()
