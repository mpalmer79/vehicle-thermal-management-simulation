"""Generate the UI-5 scenario preview fixture from the authoritative VTMS-V1 engine.

This script does not define, alter, or approximate physics. It executes the frozen
canonical scenarios through the existing ``SimulationRunner`` and writes a sampled,
presentation-sized subset of the returned ``SimulationResult`` for the web layer.

Run from the repository root:

    python generate_ui_previews.py
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from vtms_v1.scenarios import canonical_scenarios
from vtms_v1.simulation import SimulationRunner

OUTPUT_PATH = Path("web/lib/fixtures/canonical-previews.json")
PREVIEW_SAMPLE_INTERVAL_S = 60.0
DECIMALS = 4


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), DECIMALS)


def _preview_for(scenario_id: str) -> dict[str, Any]:
    scenario = canonical_scenarios()[scenario_id]
    sampled = replace(scenario, output_interval_s=PREVIEW_SAMPLE_INTERVAL_S)
    result = SimulationRunner().run(sampled)

    series = result.time_series
    final = series[-1]

    return {
        "scenarioId": scenario.scenario_id,
        "name": scenario.name,
        "durationS": scenario.duration_s,
        "trace": [
            {
                "t": _round(point.time_s),
                "engineC": _round(point.engine_structure_temp_c),
                "coolantC": _round(point.coolant_temp_c),
            }
            for point in series
        ],
        "endState": {
            "engineC": _round(final.engine_structure_temp_c),
            "coolantC": _round(final.coolant_temp_c),
            "thermostatFraction": _round(final.thermostat_fraction),
            "fanFraction": _round(final.fan_fraction),
            "radiatorHeatW": _round(final.radiator_heat_w),
            "airFlowKgS": _round(final.air_flow_kg_s),
            "pumpFlowKgS": _round(final.pump_flow_kg_s),
        },
        "peak": {
            "engineC": _round(max(point.engine_structure_temp_c for point in series)),
            "coolantC": _round(max(point.coolant_temp_c for point in series)),
        },
        "energyBalance": {
            "normalizedResidual": _round(result.energy_balance.normalized_residual),
        },
        "warnings": list(result.warnings),
    }


def main() -> None:
    payload = {
        "fixtureId": "canonical-previews-ui5",
        "generatedBy": "VTMS-V1 Python physics engine via generate_ui_previews.py",
        "samplingNote": (
            f"Canonical scenarios re-executed with a {PREVIEW_SAMPLE_INTERVAL_S:.0f} second "
            "result output interval for scenario preview rendering. Governing equations, "
            "parameters, solver settings, and canonical inputs are unchanged."
        ),
        "model": {
            "modelId": "VTMS-V1",
            "equationSet": "EM-V1",
            "status": "numerical_verified_generic_uncalibrated",
        },
        "scenarios": [_preview_for(scenario_id) for scenario_id in sorted(canonical_scenarios())],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(OUTPUT_PATH), "scenarios": len(payload["scenarios"])}))


if __name__ == "__main__":
    main()
