"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMemo, useSyncExternalStore } from "react";

import { PlaybackWorkspace } from "@/components/playback-workspace";
import { StatusPill } from "@/components/status-pill";
import { apiResponseToFixture } from "@/lib/api";
import type { SimulationApiResponse } from "@/lib/vtms-types";

const subscribe = () => () => {};
const getServerSnapshot = () => null;

export function StoredRunResult() {
  const params = useParams<{ runId: string }>();
  const runId = params.runId;
  const storageKey = `vtms:run:${runId}`;
  const raw = useSyncExternalStore(
    subscribe,
    () => window.sessionStorage.getItem(storageKey),
    getServerSnapshot,
  );

  const run = useMemo(() => {
    if (!raw) return null;
    try {
      return JSON.parse(raw) as SimulationApiResponse;
    } catch {
      return null;
    }
  }, [raw]);

  if (!run) {
    return (
      <div className="run-empty-state">
        <span className="eyebrow">RUN NOT AVAILABLE IN THIS SESSION</span>
        <h1>Simulation result not found</h1>
        <p>UI-2 keeps computed results in browser session storage only. Run the simulation again to recreate this result.</p>
        <Link className="button primary" href="/simulate">Open Simulation Lab</Link>
      </div>
    );
  }

  const fixture = apiResponseToFixture(run);
  const result = run.result;
  const scenario = result.scenario_metadata;
  const originalScenarioId = scenario.scenario_id.startsWith("CUSTOM-")
    ? scenario.scenario_id.replace("CUSTOM-", "")
    : scenario.scenario_id;

  return (
    <>
      <header className="result-header">
        <div>
          <span className="eyebrow">AUTHORITATIVE COMPUTED RESULT</span>
          <h1>{scenario.name}</h1>
          <div className="result-status">
            <StatusPill tone="verified">COMPLETE</StatusPill>
            <StatusPill>{result.model_metadata.model_id}</StatusPill>
            <StatusPill>{run.run_id}</StatusPill>
          </div>
        </div>
        <Link className="button secondary" href={`/simulate?scenario=${originalScenarioId}`}>Edit & rerun</Link>
      </header>

      <div className="fixture-disclosure">
        <strong>Engineering provenance</strong>
        <span>
          This result was returned by FastAPI after executing the authoritative VTMS-V1 Python engine. The browser stores it only for this session and does not calculate thermal physics. It is computed simulation playback, not live vehicle telemetry.
        </span>
      </div>

      <PlaybackWorkspace data={fixture} />

      <div className="run-metadata-grid">
        <article>
          <span className="eyebrow">MODEL</span>
          <strong>{result.model_metadata.model_id} / {result.model_metadata.equation_set}</strong>
          <small>{result.model_metadata.classification}</small>
        </article>
        <article>
          <span className="eyebrow">PARAMETER SET</span>
          <strong>{result.model_metadata.parameter_set}</strong>
          <small>{result.model_metadata.validation_status}</small>
        </article>
        <article>
          <span className="eyebrow">SOLVER</span>
          <strong>{result.solver_diagnostics.success ? "RK45 complete" : "Solver warning"}</strong>
          <small>{result.solver_diagnostics.function_evaluations} function evaluations</small>
        </article>
      </div>
    </>
  );
}
