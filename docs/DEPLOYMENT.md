# VTMS Production Deployment

## Scope

UI-3 packages VTMS as two independently deployable services from the same GitHub repository:

1. `vtms-api`: FastAPI plus the authoritative VTMS-V1 Python engine.
2. `vtms-web`: the Next.js engineering interface.

The web service never calculates thermal physics. Browser simulation requests cross the HTTP boundary to `vtms-api`, which invokes `SimulationRunner` and returns the serialized authoritative result.

## Production topology

```text
Browser
   |
   | HTTPS
   v
vtms-web
Next.js standalone server
   |
   | HTTPS /api/v1/simulations
   v
vtms-api
FastAPI + VTMS-V1 Python engine
   |
   v
SimulationResult
```

## Railway service configuration

### 1. API service

Create a Railway service from the GitHub repository and name it `vtms-api`.

Use:

```text
Root Directory: /
Config File Path: /railway.json
```

The repository configuration selects `Dockerfile.api` and verifies `/health` before a deployment becomes active.

Set these service variables:

```text
VTMS_ENV=production
VTMS_ENABLE_DOCS=false
VTMS_MAX_CONCURRENT_SIMULATIONS=2
VTMS_CORS_ORIGINS=https://<vtms-web-public-domain>
```

Generate a public Railway domain for the API.

The container listens on Railway's injected `PORT` variable and runs one Uvicorn worker. Within that worker, the API limits concurrent simulation executions with an application semaphore. This protects the public demonstration endpoint from unbounded simultaneous solver work while preserving deterministic model behavior.

### 2. Web service

Create a second Railway service from the same repository and name it `vtms-web`.

Use:

```text
Root Directory: /web
Config File Path: /web/railway.json
```

The repository configuration selects `web/Dockerfile` and verifies `/api/health` before a deployment becomes active.

Set this service variable:

```text
NEXT_PUBLIC_VTMS_API_URL=https://<vtms-api-public-domain>
```

Generate a public Railway domain for the web service.

`NEXT_PUBLIC_VTMS_API_URL` is required during the Next.js build because browser-visible environment variables are compiled into the production bundle. The Dockerfile explicitly accepts this Railway variable as a build argument.

### 3. Complete the CORS pairing

After the web domain exists, confirm the API variable contains the exact HTTPS origin:

```text
VTMS_CORS_ORIGINS=https://<vtms-web-public-domain>
```

Do not include a trailing slash. Multiple approved origins can be supplied as a comma-separated list.

Redeploy the API if the CORS value changed after its first deployment.

## Health checks

API:

```text
GET /health
```

Expected identifying fields include:

```text
status: ok
model_id: VTMS-V1
equation_set: EM-V1
runtime_environment: production
```

Web:

```text
GET /api/health
```

Expected identifying fields include:

```text
status: ok
service: vtms-web
modelBoundary: FastAPI
```

Railway uses these endpoints during deployment activation. They are deployment readiness checks, not continuous uptime monitoring.

## Production verification

After both domains are live:

1. Open the web application on desktop and mobile.
2. Open Simulation Lab.
3. Run frozen scenario `S-03` without editing its physical inputs.
4. Confirm the returned page is `/results/<run_id>` and is labeled `AUTHORITATIVE COMPUTED RESULT`.
5. Confirm final S-03 temperatures remain within the existing regression tolerance around 101.06 C engine structure and 96.50 C coolant.
6. Confirm the result reports `VTMS-V1` and `EM-V1` provenance.
7. Modify one operating input and run again.
8. Confirm the run is labeled with a `CUSTOM-` scenario identity rather than redefining the frozen canonical scenario.
9. Exercise one supported fault case and verify the returned result changes physically through the Python model.
10. Verify browser developer tools show no failed CORS requests or mixed HTTP/HTTPS requests.

## Production security controls

UI-3 adds the following deployment controls without altering the governing physics:

- non-root API container user
- non-root Next.js container user
- standalone Next.js production output
- deterministic `npm ci` in CI and container builds
- production npm vulnerability gate at high severity and above
- weekly Dependabot checks for Python and npm dependencies
- API response compression for large simulation results
- explicit API `no-store` caching policy
- baseline clickjacking, MIME sniffing, referrer, and browser permission headers
- configurable FastAPI documentation exposure
- bounded API simulation concurrency
- strict request schema and existing canonical scenario identity enforcement
- Railway deployment health checks
- Docker image build and boot smoke tests in GitHub Actions

## Environment rules

Never commit Railway secrets or deployment-specific environment values to the repository.

The public API URL is not a secret. It is intentionally exposed to the web client through `NEXT_PUBLIC_VTMS_API_URL`.

`VTMS_CORS_ORIGINS` should contain only origins that are intentionally allowed to invoke the public simulation API from a browser.

## Rollback

If a production deployment fails its health check, Railway should not activate the unhealthy revision. If a later issue is discovered after activation, roll back to the preceding successful deployment in Railway and preserve the failing Git commit for diagnosis rather than modifying the frozen physics to solve an infrastructure problem.

## Engineering boundary

Deployment configuration may alter transport, process management, compression, security headers, concurrency, and environment handling. It must not alter:

- VTMS-V1 governing equations
- EM-V1 equation set
- parameter values
- canonical S-01 through S-09 definitions
- verification acceptance criteria
- calibration or validation evidence

Infrastructure failures and model-validation failures are separate evidence categories and must remain separate in reporting.
