from __future__ import annotations

from dataclasses import dataclass

from vtms_v1.scenario import Scenario
from vtms_v2.m0.airflow import AirflowBoundary

from .config import M2Parameters
from .simulation import M2SimulationRunner
from .types import M2SimulationResult


@dataclass(frozen=True)
class M2IndependentCase:
    """One authoritative M2 numerical experiment with its own RK45 controller."""

    case_id: str
    parameters: M2Parameters
    scenario: Scenario
    airflow_boundary: AirflowBoundary
    initial_head_temp_c: float | None = None
    initial_block_temp_c: float | None = None
    initial_cold_temp_c: float | None = None

    def validate(self) -> None:
        if not self.case_id.strip():
            raise ValueError("M2 independent case requires a non-empty case_id")
        self.parameters.validate()
        self.scenario.validate()
        self.airflow_boundary.validate()


@dataclass(frozen=True)
class M2IndependentResult:
    case_id: str
    result: M2SimulationResult


def run_independent_ensemble(
    cases: list[M2IndependentCase] | tuple[M2IndependentCase, ...],
) -> tuple[M2IndependentResult, ...]:
    """Run each M2 case as a separate four-state solve_ivp integration.

    This function intentionally does not flatten independent configurations into one
    large ODE state. Each case receives its own M2SimulationRunner and therefore its
    own SciPy RK45 adaptive error norm and step sequence. This is the authoritative
    execution semantics for M2 physical-development acceptance after numerical
    execution amendment VTMS-V2-M2-NUMERICAL-EXECUTION-A1.

    Process-level parallelism may be placed outside this function as long as every
    process still executes one independent four-state solve per case.
    """

    if not cases:
        raise ValueError("at least one M2 independent case is required")

    seen: set[str] = set()
    outputs: list[M2IndependentResult] = []
    for case in cases:
        case.validate()
        if case.case_id in seen:
            raise ValueError(f"duplicate M2 independent case_id: {case.case_id!r}")
        seen.add(case.case_id)

        result = M2SimulationRunner(parameters=case.parameters).run(
            case.scenario,
            airflow_boundary=case.airflow_boundary,
            initial_head_temp_c=case.initial_head_temp_c,
            initial_block_temp_c=case.initial_block_temp_c,
            initial_cold_temp_c=case.initial_cold_temp_c,
        )
        outputs.append(M2IndependentResult(case_id=case.case_id, result=result))

    return tuple(outputs)
