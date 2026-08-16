from __future__ import annotations

from dataclasses import asdict

import numpy as np

from .config import ModelParameters
from .radiator import RadiatorModel
from .scenarios import canonical_scenarios
from .simulation import SimulationRunner
from .thermostat import ThermostatModel
from .types import ThermostatMode


class VerificationFailure(AssertionError):
    pass


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def run_verification_suite() -> dict[str, object]:
    parameters = ModelParameters()
    runner = SimulationRunner(parameters)
    scenarios = canonical_scenarios()
    results = {scenario_id: runner.run(scenario) for scenario_id, scenario in scenarios.items()}

    checks: list[dict[str, object]] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": passed, "detail": detail})
        _check(passed, f"{check_id}: {detail}")

    for scenario_id, result in results.items():
        residual = result.energy_balance.normalized_residual
        record(
            f"V-ENERGY-01/{scenario_id}",
            residual <= 0.001,
            f"normalized energy residual={residual:.9g}",
        )

    thermostat = ThermostatModel(parameters)
    record(
        "THERMOSTAT-CLOSED",
        thermostat.opening(parameters.thermostat_open_c - 0.1) == 0.0,
        "normal thermostat is exactly closed below T_open",
    )
    record(
        "THERMOSTAT-FULL",
        thermostat.opening(parameters.thermostat_full_c) == 1.0,
        "normal thermostat is exactly fully open at T_full",
    )
    record(
        "THERMOSTAT-STUCK-CLOSED",
        thermostat.opening(150.0, ThermostatMode.STUCK_CLOSED) == 0.0,
        "stuck-closed thermostat returns zero opening",
    )
    record(
        "THERMOSTAT-STUCK-OPEN",
        thermostat.opening(20.0, ThermostatMode.STUCK_OPEN) == 1.0,
        "stuck-open thermostat returns full opening",
    )

    radiator = RadiatorModel(parameters)
    zero_flow = radiator.evaluate(100.0, 25.0, 0.0, 1.0)
    record(
        "RADIATOR-ZERO-FLOW",
        zero_flow.heat_w == 0.0 and zero_flow.outlet_temp_c is None,
        "zero coolant flow returns zero heat transfer and no outlet temperature",
    )
    equal_temp = radiator.evaluate(90.0, 90.0, 0.5, 1.0)
    record(
        "RADIATOR-EQUAL-TEMP",
        abs(equal_temp.heat_w) <= 1e-12,
        "equal inlet temperatures return zero heat transfer",
    )
    nominal = radiator.evaluate(100.0, 25.0, 0.5, 1.0, health=1.0)
    degraded = radiator.evaluate(100.0, 25.0, 0.5, 1.0, health=0.6)
    record(
        "RADIATOR-HEALTH-MONOTONIC",
        abs(nominal.heat_w) >= abs(degraded.heat_w),
        "higher radiator health does not reduce heat rejection",
    )
    record(
        "RADIATOR-EFFECTIVENESS-BOUNDS",
        0.0 <= nominal.effectiveness <= 1.0,
        f"effectiveness={nominal.effectiveness:.6f}",
    )

    directional = {
        "S-07": results["S-07"].final_point().coolant_temp_c > results["S-04"].final_point().coolant_temp_c,
        "S-08": results["S-08"].final_point().coolant_temp_c > results["S-04"].final_point().coolant_temp_c,
        "S-09": results["S-09"].final_point().coolant_temp_c > results["S-04"].final_point().coolant_temp_c,
    }
    for sid, passed in directional.items():
        record(
            f"DIRECTIONAL/{sid}",
            passed,
            f"fault coolant end={results[sid].final_point().coolant_temp_c:.3f} C; "
            f"S-04 end={results['S-04'].final_point().coolant_temp_c:.3f} C",
        )

    baseline = results["S-01"]
    tight = runner.run(scenarios["S-01"], rtol=1e-7, atol=1e-9, max_step_s=0.5)
    base_engine = np.array([p.engine_structure_temp_c for p in baseline.time_series])
    tight_engine = np.array([p.engine_structure_temp_c for p in tight.time_series])
    base_coolant = np.array([p.coolant_temp_c for p in baseline.time_series])
    tight_coolant = np.array([p.coolant_temp_c for p in tight.time_series])
    max_diff = float(max(np.max(np.abs(base_engine - tight_engine)), np.max(np.abs(base_coolant - tight_coolant))))
    record(
        "V-NUM-01/S-01",
        max_diff < 0.05,
        f"maximum one-second state difference={max_diff:.9f} C",
    )

    summary = {}
    for sid, result in results.items():
        final = result.final_point()
        summary[sid] = {
            "name": result.scenario_metadata["name"],
            "end_engine_temp_c": final.engine_structure_temp_c,
            "end_coolant_temp_c": final.coolant_temp_c,
            "energy_residual_fraction": result.energy_balance.normalized_residual,
            "warnings": result.warnings,
        }

    return {
        "model_metadata": runner.metadata.snapshot(),
        "verification_status": "PASS",
        "checks": checks,
        "canonical_summary": summary,
    }
