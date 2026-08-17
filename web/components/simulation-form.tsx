"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ScenarioConfigPreview } from "@/components/visuals/scenario-config-preview";
import { runSimulation } from "@/lib/api";
import { scenarioById, scenarios } from "@/lib/scenarios";
import type { ThermostatMode } from "@/lib/vtms-types";

type FormState = {
  scenarioId: string;
  ambient: number;
  rpm: number;
  load: number;
  speedKmh: number;
  duration: number;
  engineTemp: number;
  coolantTemp: number;
  fanFailed: boolean;
  thermostatMode: ThermostatMode;
  thermostatHealthPct: number;
  pumpHealthPct: number;
  radiatorHealthPct: number;
  airflowHealthPct: number;
  engineHeatOverride: string;
};

const thermostatLabel: Record<ThermostatMode, string> = {
  normal: "Normal",
  stuck_closed: "Stuck closed",
  stuck_open: "Stuck open",
};

function defaultsForScenario(id: string): FormState {
  const scenario = scenarioById(id);
  return {
    scenarioId: scenario.id,
    ambient: scenario.ambient,
    rpm: scenario.rpm,
    load: scenario.load,
    speedKmh: scenario.speedKmh,
    duration: scenario.duration,
    engineTemp: scenario.id === "S-01" ? 20 : 105,
    coolantTemp: scenario.id === "S-01" ? 20 : 92,
    fanFailed: scenario.id === "S-05",
    thermostatMode: scenario.id === "S-06" ? "stuck_closed" : "normal",
    thermostatHealthPct: 100,
    pumpHealthPct: scenario.id === "S-07" ? 50 : 100,
    radiatorHealthPct: scenario.id === "S-08" ? 60 : 100,
    airflowHealthPct: scenario.id === "S-09" ? 50 : 100,
    engineHeatOverride: "",
  };
}

export function SimulationForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const requestedScenario = searchParams.get("scenario");
  const initialScenario = scenarios.some((item) => item.id === requestedScenario) ? requestedScenario! : "S-03";
  const [form, setForm] = useState<FormState>(() => defaultsForScenario(initialScenario));
  const [custom, setCustom] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scenario = useMemo(() => scenarioById(form.scenarioId), [form.scenarioId]);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
    setCustom(true);
  };

  const selectScenario = (id: string) => {
    setForm(defaultsForScenario(id));
    setCustom(false);
    setError(null);
  };

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setRunning(true);
    setError(null);

    try {
      const response = await runSimulation({
        scenario_id: custom ? `CUSTOM-${scenario.id}` : scenario.id,
        name: custom ? `Custom based on ${scenario.name}` : scenario.name,
        duration_s: form.duration,
        ambient_temp_c: form.ambient,
        engine_speed_rpm: form.rpm,
        effective_load_percent: form.load,
        vehicle_speed_kmh: form.speedKmh,
        initial_engine_temp_c: form.engineTemp,
        initial_coolant_temp_c: form.coolantTemp,
        engine_heat_override_w: form.engineHeatOverride.trim() === "" ? null : Number(form.engineHeatOverride),
        output_interval_s: 2,
        faults: {
          fan_failed: form.fanFailed,
          thermostat_mode: form.thermostatMode,
          thermostat_health: form.thermostatHealthPct / 100,
          pump_health: form.pumpHealthPct / 100,
          radiator_health: form.radiatorHealthPct / 100,
          airflow_health: form.airflowHealthPct / 100,
        },
      });

      window.sessionStorage.setItem(`vtms:run:${response.run_id}`, JSON.stringify(response));
      window.sessionStorage.setItem("vtms:last-run-id", response.run_id);
      router.push(`/results/${response.run_id}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Simulation request failed.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="simulation-layout">
      <form className="simulation-form" onSubmit={submit}>
        <label className="field full">
          <span>Scenario preset</span>
          <select value={form.scenarioId} onChange={(event) => selectScenario(event.target.value)}>
            {scenarios.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}
          </select>
        </label>

        {custom && <div className="custom-note">Custom configuration based on {form.scenarioId}. The run will be labeled separately from the frozen canonical case.</div>}

        <fieldset>
          <legend>Operating conditions</legend>
          <div className="field-grid">
            <label className="field"><span>Ambient</span><div className="input-unit"><input value={form.ambient} type="number" onChange={(event) => update("ambient", Number(event.target.value))} /><em>°C</em></div></label>
            <label className="field"><span>Engine speed</span><div className="input-unit"><input value={form.rpm} min="0" max="6500" type="number" onChange={(event) => update("rpm", Number(event.target.value))} /><em>rpm</em></div></label>
            <label className="field"><span>Effective load</span><div className="input-unit"><input value={form.load} min="0" max="100" type="number" onChange={(event) => update("load", Number(event.target.value))} /><em>%</em></div></label>
            <label className="field"><span>Vehicle speed</span><div className="input-unit"><input value={form.speedKmh} min="0" type="number" step="0.1" onChange={(event) => update("speedKmh", Number(event.target.value))} /><em>km/h</em></div></label>
            <label className="field"><span>Duration</span><div className="input-unit"><input value={form.duration} min="1" max="7200" type="number" onChange={(event) => update("duration", Number(event.target.value))} /><em>s</em></div></label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Initial conditions</legend>
          <div className="field-grid">
            <label className="field"><span>Engine structure</span><div className="input-unit"><input value={form.engineTemp} type="number" onChange={(event) => update("engineTemp", Number(event.target.value))} /><em>°C</em></div></label>
            <label className="field"><span>Coolant</span><div className="input-unit"><input value={form.coolantTemp} type="number" onChange={(event) => update("coolantTemp", Number(event.target.value))} /><em>°C</em></div></label>
          </div>
        </fieldset>

        <details className="form-disclosure">
          <summary>Fault injection</summary>
          <div className="fault-controls">
            <label className="check-field"><input checked={form.fanFailed} type="checkbox" onChange={(event) => update("fanFailed", event.target.checked)} /><span>Cooling fan failed</span></label>
            <label className="field"><span>Thermostat mode</span><select value={form.thermostatMode} onChange={(event) => update("thermostatMode", event.target.value as ThermostatMode)}><option value="normal">Normal</option><option value="stuck_closed">Stuck closed</option><option value="stuck_open">Stuck open</option></select></label>
            <div className="field-grid">
              <label className="field"><span>Thermostat health</span><div className="input-unit"><input value={form.thermostatHealthPct} min="0" max="100" type="number" onChange={(event) => update("thermostatHealthPct", Number(event.target.value))} /><em>%</em></div></label>
              <label className="field"><span>Pump health</span><div className="input-unit"><input value={form.pumpHealthPct} min="0" max="100" type="number" onChange={(event) => update("pumpHealthPct", Number(event.target.value))} /><em>%</em></div></label>
              <label className="field"><span>Radiator health</span><div className="input-unit"><input value={form.radiatorHealthPct} min="0" max="100" type="number" onChange={(event) => update("radiatorHealthPct", Number(event.target.value))} /><em>%</em></div></label>
              <label className="field"><span>Airflow health</span><div className="input-unit"><input value={form.airflowHealthPct} min="0" max="100" type="number" onChange={(event) => update("airflowHealthPct", Number(event.target.value))} /><em>%</em></div></label>
            </div>
          </div>
        </details>

        <details className="form-disclosure">
          <summary>Advanced heat override</summary>
          <p>When supplied, direct engine heat input bypasses the generic RPM/load heat-generation adapter. This remains an engineering control, not an AI estimate.</p>
          <label className="field"><span>Engine heat override</span><div className="input-unit"><input value={form.engineHeatOverride} min="0" type="number" placeholder="Leave blank for RPM/load model" onChange={(event) => update("engineHeatOverride", event.target.value)} /><em>W</em></div></label>
        </details>

        {error && <div className="api-error" role="alert"><strong>Simulation not completed</strong><span>{error}</span></div>}

        <div className="form-action">
          <button className="button primary" disabled={running} type="submit">{running ? "Running VTMS..." : "Run Simulation"}</button>
          <span>FastAPI executes the authoritative Python model. React only submits inputs and visualizes the returned result.</span>
        </div>

        <div className="run-dock">
          <button className="button primary" disabled={running} type="submit">{running ? "Running VTMS..." : "Run Simulation"}</button>
          <span>Executed by the VTMS-V1 Python engine through FastAPI</span>
        </div>
      </form>

      <aside className="scenario-preview">
        <div>
          <span className="eyebrow">CONFIGURATION PREVIEW</span>
          <h2>{custom ? "CUSTOM · " : ""}{scenario.id} {scenario.name}</h2>
        </div>

        <div className="config-preview-stage">
          <ScenarioConfigPreview
            config={{
              ambientC: form.ambient,
              rpm: form.rpm,
              loadPercent: form.load,
              speedKmh: form.speedKmh,
              fanFailed: form.fanFailed,
              thermostatMode: form.thermostatMode,
              pumpHealthPct: form.pumpHealthPct,
              radiatorHealthPct: form.radiatorHealthPct,
              airflowHealthPct: form.airflowHealthPct,
            }}
          />
        </div>

        <div className="config-states">
          <div className={`config-state${form.fanFailed ? " fault" : ""}`}>
            <span>Fan</span>
            <strong>{form.fanFailed ? "Failed" : "Available"}</strong>
          </div>
          <div className={`config-state${form.thermostatMode === "normal" ? "" : " fault"}`}>
            <span>Thermostat</span>
            <strong>{thermostatLabel[form.thermostatMode]}</strong>
          </div>
          <div className={`config-state${form.pumpHealthPct < 100 ? " alert" : ""}`}>
            <span>Pump health</span>
            <strong>{form.pumpHealthPct}%</strong>
          </div>
          <div className={`config-state${form.radiatorHealthPct < 100 ? " alert" : ""}`}>
            <span>Radiator health</span>
            <strong>{form.radiatorHealthPct}%</strong>
          </div>
          <div className={`config-state${form.airflowHealthPct < 100 ? " alert" : ""}`}>
            <span>Airflow health</span>
            <strong>{form.airflowHealthPct}%</strong>
          </div>
          <div className="config-state">
            <span>Duration</span>
            <strong>{form.duration} s</strong>
          </div>
        </div>

        <p className="config-preview-note">
          Configuration only. Temperatures, flows, and heat rejection are computed by the Python
          engine after the run.
        </p>

        <div className="model-card">
          <strong>VTMS-V1 / EM-V1</strong>
          <span>FastAPI execution boundary active</span>
          <span>Generic parameter set · numerically verified</span>
          <span>Controlled physical validation pending</span>
        </div>
      </aside>
    </div>
  );
}
