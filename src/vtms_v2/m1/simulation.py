from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from vtms_v1.constants import LIQUID_MODEL_CAUTION_C
from vtms_v1.scenario import Scenario
from vtms_v1.types import EnergyBalance, SolverDiagnostics
from vtms_v2.m0.airflow import AirflowBoundary

from .config import M1ModelMetadata, M1Parameters
from .thermal import M1ThermalModel
from .types import M1SimulationResult, M1TimeSeriesPoint


class M1SimulationError(RuntimeError):
    def __init__(self, diagnostics: SolverDiagnostics) -> None:
        super().__init__(diagnostics.message)
        self.diagnostics = diagnostics


class M1SimulationRunner:
    def __init__(
        self,
        parameters: M1Parameters | None = None,
        metadata: M1ModelMetadata | None = None,
    ) -> None:
        self.parameters = parameters or M1Parameters()
        self.metadata = metadata or M1ModelMetadata()
        self.parameters.validate()
        self.thermal_model = M1ThermalModel(self.parameters)

    @staticmethod
    def _output_times(duration_s: float, interval_s: float) -> np.ndarray:
        times = np.arange(0.0, duration_s + 0.5 * interval_s, interval_s, dtype=float)
        times = times[times <= duration_s]
        if times.size == 0 or not np.isclose(times[-1], duration_s):
            times = np.append(times, duration_s)
        return times

    def run(
        self,
        scenario: Scenario,
        *,
        airflow_boundary: AirflowBoundary,
        initial_cold_temp_c: float | None = None,
        rtol: float | None = None,
        atol: float | None = None,
        max_step_s: float | None = None,
    ) -> M1SimulationResult:
        scenario.validate()
        airflow_boundary.validate()
        rtol = self.parameters.solver_rtol if rtol is None else rtol
        atol = self.parameters.solver_atol if atol is None else atol
        max_step_s = self.parameters.solver_max_step_s if max_step_s is None else max_step_s
        if rtol <= 0.0 or atol <= 0.0 or max_step_s <= 0.0:
            raise ValueError("solver tolerances and max_step_s must be > 0")

        initial_cold = scenario.initial_coolant_temp_c if initial_cold_temp_c is None else float(initial_cold_temp_c)
        output_times = self._output_times(scenario.duration_s, scenario.output_interval_s)

        def rhs(time_s: float, state: np.ndarray) -> list[float]:
            op = scenario.at(time_s)
            return list(
                self.thermal_model.rhs(
                    float(state[0]),
                    float(state[1]),
                    float(state[2]),
                    op,
                    scenario.faults,
                    airflow_boundary,
                    time_s=time_s,
                )
            )

        solution = solve_ivp(
            rhs,
            (0.0, scenario.duration_s),
            [scenario.initial_engine_temp_c, scenario.initial_coolant_temp_c, initial_cold],
            method="RK45",
            rtol=rtol,
            atol=atol,
            max_step=max_step_s,
            t_eval=output_times,
        )
        diagnostics = SolverDiagnostics(
            success=bool(solution.success),
            status=int(solution.status),
            message=str(solution.message),
            function_evaluations=int(solution.nfev),
            jacobian_evaluations=int(solution.njev),
            lu_decompositions=int(solution.nlu),
        )
        if not solution.success:
            raise M1SimulationError(diagnostics)

        points: list[M1TimeSeriesPoint] = []
        for index, time_s in enumerate(solution.t):
            engine_temp_c = float(solution.y[0, index])
            hot_temp_c = float(solution.y[1, index])
            cold_temp_c = float(solution.y[2, index])
            op = scenario.at(float(time_s))
            c = self.thermal_model.evaluate_components(
                engine_temp_c,
                hot_temp_c,
                cold_temp_c,
                op,
                scenario.faults,
                airflow_boundary,
                time_s=float(time_s),
            )
            points.append(
                M1TimeSeriesPoint(
                    time_s=float(time_s),
                    engine_structure_temp_c=engine_temp_c,
                    hot_coolant_temp_c=hot_temp_c,
                    cold_coolant_temp_c=cold_temp_c,
                    ect_predicted_c=hot_temp_c,
                    radiator_outlet_temp_c=c.radiator.outlet_temp_c,
                    engine_heat_w=c.engine_heat_w,
                    engine_to_coolant_w=c.engine_to_coolant_w,
                    engine_to_ambient_w=c.engine_to_ambient_w,
                    radiator_heat_w=c.radiator.heat_w,
                    pump_flow_kg_s=c.pump_flow_kg_s,
                    radiator_flow_kg_s=c.radiator_flow_kg_s,
                    bypass_flow_kg_s=c.bypass_flow_kg_s,
                    air_flow_kg_s=c.air_flow_kg_s,
                    thermostat_fraction=c.thermostat_fraction,
                    fan_fraction=c.fan_fraction,
                    radiator_effectiveness=c.radiator.effectiveness,
                    radiator_ntu=c.radiator.ntu,
                )
            )

        scenario_metadata = scenario.metadata()
        scenario_metadata["m1_airflow_boundary"] = airflow_boundary.metadata()
        scenario_metadata["m1_initialization"] = {
            "hot_coolant_initial_c": scenario.initial_coolant_temp_c,
            "cold_coolant_initial_c": initial_cold,
            "cold_initial_defaulted_to_hot": initial_cold_temp_c is None,
            "physical_hot_start_use_requires_separate_manifest": True,
        }

        return M1SimulationResult(
            model_metadata=self.metadata.snapshot(),
            scenario_metadata=scenario_metadata,
            parameter_snapshot=self.parameters.snapshot(),
            provenance_snapshot=self.parameters.provenance(),
            time_series=points,
            events=self._events(points),
            energy_balance=self._energy_balance(points),
            warnings=self._warnings(points),
            solver_diagnostics=diagnostics,
        )

    def _energy_balance(self, points: list[M1TimeSeriesPoint]) -> EnergyBalance:
        t = np.array([point.time_s for point in points], dtype=float)
        q_in = np.array([point.engine_heat_w for point in points], dtype=float)
        q_out = np.array([point.engine_to_ambient_w + point.radiator_heat_w for point in points], dtype=float)
        input_energy = float(np.trapezoid(q_in, t))
        rejected_energy = float(np.trapezoid(q_out, t))
        first, last = points[0], points[-1]
        p = self.parameters
        stored = (
            p.engine_thermal_capacitance_j_per_k * (last.engine_structure_temp_c - first.engine_structure_temp_c)
            + p.hot_coolant_capacitance_j_per_k * (last.hot_coolant_temp_c - first.hot_coolant_temp_c)
            + p.cold_coolant_capacitance_j_per_k * (last.cold_coolant_temp_c - first.cold_coolant_temp_c)
        )
        residual = input_energy - rejected_energy - stored
        normalized = abs(residual) / max(abs(input_energy), 1.0)
        return EnergyBalance(
            input_energy_j=input_energy,
            rejected_energy_j=rejected_energy,
            stored_energy_change_j=stored,
            residual_j=residual,
            normalized_residual=normalized,
        )

    @staticmethod
    def _events(points: list[M1TimeSeriesPoint]) -> list[dict[str, float | str]]:
        events: list[dict[str, float | str]] = []
        thermostat_seen = fan_seen = caution_seen = False
        for point in points:
            if not thermostat_seen and point.thermostat_fraction > 0.0:
                events.append({"event": "thermostat_opening_started", "time_s": point.time_s})
                thermostat_seen = True
            if not fan_seen and point.fan_fraction > 0.0:
                events.append({"event": "fan_command_started", "time_s": point.time_s})
                fan_seen = True
            if not caution_seen and max(point.hot_coolant_temp_c, point.cold_coolant_temp_c) >= LIQUID_MODEL_CAUTION_C:
                events.append({"event": "liquid_model_caution_boundary_crossed", "time_s": point.time_s})
                caution_seen = True
        return events

    @staticmethod
    def _warnings(points: list[M1TimeSeriesPoint]) -> list[str]:
        if any(max(point.hot_coolant_temp_c, point.cold_coolant_temp_c) >= LIQUID_MODEL_CAUTION_C for point in points):
            return [
                f"Simulated coolant temperature reached or exceeded {LIQUID_MODEL_CAUTION_C:.0f} C. "
                "VTMS-V2-M1 remains a liquid-only model-form test and does not predict boiling or engine damage."
            ]
        return []
