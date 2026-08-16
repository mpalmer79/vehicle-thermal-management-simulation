# VTMS Web UI

This directory contains the executable web layer for the Vehicle Thermal Management Simulation Platform.

## Current scope

- Next.js App Router with TypeScript
- Responsive desktop and mobile engineering-workstation shell
- Overview, Simulation Lab, System Explorer, Scenario Library, Validation, Model, Roadmap, and Results routes
- Synchronized thermal-system playback
- Frozen S-03 demonstration fixture for the Overview and System Explorer
- FastAPI execution path for Simulation Lab runs
- Session-scoped computed result routes under `/results/[runId]`
- Browser-renderable KIT plausibility evidence
- UI-3 standalone production output and non-root Docker image
- Web health endpoint at `/api/health`
- Production browser security headers
- Railway service configuration under `railway.json`

## Engineering boundary

The web application does **not** calculate VTMS thermal physics.

Simulation Lab submits human-facing scenario inputs to the FastAPI service. FastAPI translates those inputs into the existing Python `Scenario` contract, invokes `SimulationRunner`, and returns the authoritative serialized `SimulationResult`. React stores the returned result only in browser session storage and visualizes it as computed simulation playback.

Canonical scenario IDs are protected on the server. If physical inputs are edited, the browser labels the request `CUSTOM-...`, and the API rejects altered inputs that attempt to retain a frozen S-01 through S-09 identity.

## Production packaging

The Next.js configuration uses standalone output for self-hosted production deployment. `web/Dockerfile` builds that standalone server and runs it as a non-root user.

The production image accepts:

```text
NEXT_PUBLIC_VTMS_API_URL=https://your-api.example
```

The value is a browser-visible endpoint, not a secret. It must point to the deployed FastAPI service and is compiled into the production web bundle.

The repository currently does not contain a committed `package-lock.json`, so installation uses `npm install`. GitHub Actions separately blocks high-severity production dependency advisories with `npm audit --omit=dev --audit-level=high` and runs weekly Dependabot monitoring.

## Frontend development

Requires Node.js 20.9 or newer.

Set the API endpoint if FastAPI is not running at the default local address:

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

## CI and deployment readiness

GitHub Actions independently checks:

- Python/API tests on Python 3.11, 3.12, and 3.13
- production npm dependency audit
- ESLint
- TypeScript
- Next.js production build
- production API Docker image build, boot, and health endpoint
- production web Docker image build, boot, and health endpoint

See [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md) for the Railway service topology, variables, CORS pairing, production verification, and rollback procedure.
