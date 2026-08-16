from pathlib import Path

import numpy as np
import pytest

from vtms_v1.config import ModelParameters
from vtms_validation.adapters.argonne import ArgonneD3Adapter
from vtms_validation.adapters.kit import load_kit_csv
from vtms_validation.adapters.normalized import load_normalized_sample_csv
from vtms_validation.heat_input import MafStoichiometricHeatEstimator
from vtms_validation.metrics import calculate_metrics
from vtms_validation.runner import run_kit_plausibility


def test_maf_estimator_is_explicitly_derived_not_measured():
    estimator = MafStoichiometricHeatEstimator()
    fuel = estimator.fuel_rate_kg_s(14.7)
    assert float(fuel) == pytest.approx(0.001)
    assert float(estimator.engine_heat_w(14.7)) == pytest.approx(12236.0)
    metadata = estimator.metadata()
    assert metadata["fuel_rate_status"] == "derived_not_measured"
    assert metadata["evidence_level"] == "secondary_plausibility_only"


def test_metrics_sign_and_threshold_arrivals():
    time = np.array([0.0, 10.0, 20.0, 30.0])
    measured = np.array([20.0, 40.0, 60.0, 80.0])
    predicted = np.array([20.0, 35.0, 55.0, 75.0])
    metrics = calculate_metrics(time, measured, predicted, thresholds_c=(60.0, 80.0))
    assert metrics.bias_c < 0
    assert metrics.threshold_arrival_error_s["60C"] == pytest.approx(2.5)
    assert metrics.threshold_arrival_error_s["80C"] is None


def test_kit_adapter_forward_fills_asynchronous_pids(tmp_path: Path):
    csv_path = tmp_path / "kit.csv"
    csv_path.write_text(
        "Time,Engine Coolant Temperature [°C],Engine RPM [RPM],Vehicle Speed Sensor [km/h],Ambient Air Temperature [°C],Air Flow Rate from Mass Flow Sensor [g/s]\n"
        "10:00:00.000,20,900,0,10,5\n"
        "10:00:00.100,21,,,,\n"
        "10:00:00.200,,1000,36,,6\n",
        encoding="utf-8",
    )
    dataset = load_kit_csv(csv_path)
    assert dataset.time_s.tolist() == pytest.approx([0.0, 0.1, 0.2])
    assert dataset.measured_coolant_temp_c.tolist() == pytest.approx([20.0, 21.0, 21.0])
    assert dataset.engine_speed_rpm.tolist() == pytest.approx([900.0, 900.0, 1000.0])
    assert dataset.vehicle_speed_m_s[-1] == pytest.approx(10.0)
    assert dataset.mass_air_flow_g_s[-1] == pytest.approx(6.0)


def test_normalized_sample_runs_without_parameter_mutation():
    root = Path(__file__).resolve().parents[1]
    sample = root / "validation_data" / "KIT_2018-02-20_Seat_Leon_KA_KA_Frei_sample_60s.csv"
    dataset = load_normalized_sample_csv(
        sample,
        dataset_id="KIT-2018-02-20-60S",
        source_name="KIT Automotive OBD-II Dataset",
    )
    params = ModelParameters()
    before = params.snapshot()
    result = run_kit_plausibility(dataset, parameters=params)
    assert params.snapshot() == before
    assert result.evidence_label == "external_plausibility_not_formal_validation"
    assert result.metrics.n == 18
    assert result.simulation_result.model_metadata["model_version"] == "1.0.0"
    assert result.heat_input_metadata["fuel_rate_status"] == "derived_not_measured"


def test_argonne_adapter_refuses_to_guess_schema():
    with pytest.raises(NotImplementedError):
        ArgonneD3Adapter().load("placeholder.csv")
