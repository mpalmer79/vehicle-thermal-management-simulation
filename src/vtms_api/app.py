from __future__ import annotations

import os
from dataclasses import asdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from vtms_v1.config import ModelMetadata
from vtms_v1.scenarios import canonical_scenarios
from vtms_v1.simulation import SimulationError, SimulationRunner

from .models import SimulationRequest, SimulationResponse


def _allowed_origins() -> list[str]:
    raw = os.getenv(
        "VTMS_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="VTMS API",
    version="1.0.0",
    description=(
        "Thin HTTP boundary over the deterministic VTMS-V1 Python simulation engine. "
        "The API does not implement independent thermal equations."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

_runner = SimulationRunner()


@app.get("/health")
def health() -> dict[str, str]:
    metadata = ModelMetadata().snapshot()
    return {
        "status": "ok",
        "model_id": metadata["model_id"],
        "equation_set": metadata["equation_set"],
        "validation_status": metadata["validation_status"],
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
def run_simulation(payload: SimulationRequest) -> SimulationResponse:
    scenario = payload.to_core()
    try:
        result = _runner.run(scenario)
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
