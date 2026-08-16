from __future__ import annotations

import asyncio
import os
from dataclasses import asdict, replace
from math import isclose
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.concurrency import run_in_threadpool

from vtms_v1.config import ModelMetadata
from vtms_v1.scenario import Scenario
from vtms_v1.scenarios import canonical_scenarios
from vtms_v1.simulation import SimulationError, SimulationRunner

from .models import SimulationRequest, SimulationResponse


def _allowed_origins() -> list[str]:
    raw = os.getenv(
        "VTMS_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _positive_int_env(name: str, default: int, *, maximum: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return min(max(value, 1), maximum)


def _resolve_scenario(payload: SimulationRequest) -> Scenario:
    requested = payload.to_core()
    canonical = canonical_scenarios().get(payload.scenario_id)
    if canonical is None:
        return requested

    requested_op = requested.at(0.0)
    canonical_op = canonical.at(0.0)
    numeric_pairs = [
        (requested.duration_s, canonical.duration_s),
        (requested.initial_engine_temp_c, canonical.initial_engine_temp_c),
        (requested.initial_coolant_temp_c, canonical.initial_coolant_temp_c),
        (requested_op.ambient_temp_c, canonical_op.ambient_temp_c),
        (requested_op.engine_speed_rpm, canonical_op.engine_speed_rpm),
        (requested_op.effective_load, canonical_op.effective_load),
        (requested_op.vehicle_speed_m_s, canonical_op.vehicle_speed_m_s),
    ]
    numeric_match = all(isclose(left, right, rel_tol=0.0, abs_tol=1.0e-9) for left, right in numeric_pairs)
    override_match = requested_op.engine_heat_override_w == canonical_op.engine_heat_override_w
    fault_match = requested.faults == canonical.faults

    if not (numeric_match and override_match and fault_match):
        raise HTTPException(
            status_code=422,
            detail=(
                f"{payload.scenario_id} is a frozen canonical scenario. Altered physical inputs "
                "must use a CUSTOM- scenario_id so canonical evidence remains reproducible."
            ),
        )

    return replace(canonical, output_interval_s=payload.output_interval_s)


_runtime_env = os.getenv("VTMS_ENV", "development").strip().lower()
_docs_enabled = _runtime_env != "production" or os.getenv("VTMS_ENABLE_DOCS", "false").lower() == "true"
_simulation_concurrency = _positive_int_env("VTMS_MAX_CONCURRENT_SIMULATIONS", 2, maximum=8)
_simulation_slots = asyncio.Semaphore(_simulation_concurrency)

app = FastAPI(
    title="VTMS API",
    version="1.0.0",
    description=(
        "Thin HTTP boundary over the deterministic VTMS-V1 Python simulation engine. "
        "The API does not implement independent thermal equations."
    ),
    docs_url="/docs" if _docs_enabled else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

_runner = SimulationRunner()


@app.middleware("http")
async def production_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-VTMS-Model-ID"] = _runner.metadata.model_id
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", uuid4().hex)
    return response


@app.get("/health")
def health() -> dict[str, str | int]:
    metadata = ModelMetadata().snapshot()
    return {
        "status": "ok",
        "model_id": metadata["model_id"],
        "equation_set": metadata["equation_set"],
        "validation_status": metadata["validation_status"],
        "runtime_environment": _runtime_env,
        "max_concurrent_simulations": _simulation_concurrency,
    }


@app.get("/api/v1/model")
def model_info() -> dict[str, object]:
    return {
        "model": _runner.metadata.snapshot(),
        "parameters": _runner.parameters.snapshot(),
        "provenance": _runner.parameters.provenance(),
    }


@app.get("/api/v1/scenarios")
def scenario_catalog() -> list[dict[str, object]]:
    return [scenario.metadata() for scenario in canonical_scenarios().values()]


@app.post("/api/v1/simulations", response_model=SimulationResponse)
async def run_simulation(payload: SimulationRequest) -> SimulationResponse:
    scenario = _resolve_scenario(payload)
    try:
        async with _simulation_slots:
            result = await run_in_threadpool(_runner.run, scenario)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SimulationError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "VTMS solver failed",
                "solver": asdict(exc.diagnostics),
            },
        ) from exc

    return SimulationResponse(
        run_id=f"run_{uuid4().hex[:12]}",
        result=asdict(result),
    )
