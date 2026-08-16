# VTMS Web UI

This directory contains the executable web layer for the Vehicle Thermal Management Simulation Platform.

## Current scope

- Next.js App Router with TypeScript
- Responsive desktop and mobile engineering-workstation shell
- Overview, Simulation Lab, System Explorer, Scenario Library, Validation, Model, Roadmap, and Results routes
- Synchronized thermal-system playback
- Frozen S-03 demonstration fixture for the Overview and System Explorer
- UI-2 FastAPI execution path for Simulation Lab runs
- Session-scoped computed result routes under `/results/[runId]`
- Browser-renderable KIT plausibility evidence

## Engineering boundary

The web application does **not** calculate VTMS thermal physics.

UI-2 submits human-facing scenario inputs to the FastAPI service. FastAPI translates those inputs into the existing Python `Scenario` contract, invokes `SimulationRunner`, and returns the authoritative serialized `SimulationResult`. React stores the returned result only in browser session storage and visualizes it as computed simulation playback.

Canonical scenario IDs are protected on the server. If physical inputs are edited, the browser labels the request `CUSTOM-...`, and the API rejects altered inputs that attempt to retain a frozen S-01 through S-09 identity.

## Frontend development

Requires Node.js 20.9 or newer.

Copy the example environment value if the API is not running at the default local address:

```text
NEXT_PUBLIC_VTMS_API_URL=http://localhost:8000
```

Then run:

```text
npm install
npm run dev
```

Quality gates:

```text
npm run lint
npm run typecheck
npm run build
```

## Backend development

From the repository root, install the API dependencies and run FastAPI:

```text
python -m pip install -e ".[api,dev]"
python -m uvicorn vtms_api.app:app --reload --port 8000
```

The local API allows `http://localhost:3000` and `http://127.0.0.1:3000` by default. Deployment origins are supplied through `VTMS_CORS_ORIGINS`.

GitHub Actions independently checks the web build and the Python/API test suite.
