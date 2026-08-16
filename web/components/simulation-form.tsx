"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { scenarioById, scenarios } from "@/lib/scenarios";

export function SimulationForm() {
  const searchParams = useSearchParams();
  const requestedScenario = searchParams.get("scenario");
  const initialScenario = scenarios.some((item) => item.id === requestedScenario) ? requestedScenario! : "S-03";
  const [scenarioId, setScenarioId] = useState(initialScenario);
  const scenario = useMemo(() => scenarioById(scenarioId), [scenarioId]);
  const [custom, setCustom] = useState(false);

  const selectScenario = (id: string) => { setScenarioId(id); setCustom(false); };

  return (
    <div className="simulation-layout">
      <form className="simulation-form">
        <label className="field full"><span>Scenario preset</span><select value={scenarioId} onChange={(event) => selectScenario(event.target.value)}>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}</select></label>
        {custom && <div className="custom-note">Custom configuration based on {scenarioId}. UI-1 does not execute edited inputs yet.</div>}
        <fieldset><legend>Operating conditions</legend><div className="field-grid"><label className="field"><span>Ambient</span><div className="input-unit"><input defaultValue={scenario.ambient} type="number" onChange={() => setCustom(true)} /><em>°C</em></div></label><label className="field"><span>Engine speed</span><div className="input-unit"><input defaultValue={scenario.rpm} min="700" max="6500" type="number" onChange={() => setCustom(true)} /><em>rpm</em></div></label><label className="field"><span>Effective load</span><div className="input-unit"><input defaultValue={scenario.load} min="0" max="100" type="number" onChange={() => setCustom(true)} /><em>%</em></div></label><label className="field"><span>Vehicle speed</span><div className="input-unit"><input defaultValue={scenario.speedKmh} min="0" type="number" onChange={() => setCustom(true)} /><em>km/h</em></div></label><label className="field"><span>Duration</span><div className="input-unit"><input defaultValue={scenario.duration} min="1" type="number" onChange={() => setCustom(true)} /><em>s</em></div></label></div></fieldset>
        <fieldset><legend>Initial conditions</legend><div className="field-grid"><label className="field"><span>Engine structure</span><div className="input-unit"><input defaultValue={scenarioId === "S-01" ? 20 : 105} type="number" onChange={() => setCustom(true)} /><em>°C</em></div></label><label className="field"><span>Coolant</span><div className="input-unit"><input defaultValue={scenarioId === "S-01" ? 20 : 92} type="number" onChange={() => setCustom(true)} /><em>°C</em></div></label></div></fieldset>
        <details className="form-disclosure"><summary>Fault injection</summary><p>Fan failure, thermostat mode, pump health, radiator health, and airflow health will connect to the API contract in UI-2.</p></details>
        <details className="form-disclosure"><summary>Advanced heat override</summary><p>Direct engine heat input is intentionally an advanced engineering control and remains collapsed by default.</p></details>
        <div className="form-action">
          {scenarioId === "S-03" && !custom ? <Link className="button primary" href="/results/demo-s03">Open authoritative S-03 fixture</Link> : <button className="button primary" disabled type="button">Run Simulation in UI-2</button>}
          <span>The browser never calculates VTMS thermal physics.</span>
        </div>
      </form>
      <aside className="scenario-preview"><span className="eyebrow">ENGINEERING CONTEXT</span><h2>{scenario.id} {scenario.name}</h2><p>{scenario.purpose}</p><dl><div><dt>Ambient</dt><dd>{scenario.ambient} °C</dd></div><div><dt>Engine</dt><dd>{scenario.rpm} rpm</dd></div><div><dt>Load</dt><dd>{scenario.load}%</dd></div><div><dt>Vehicle</dt><dd>{scenario.speedKmh} km/h</dd></div><div><dt>Duration</dt><dd>{scenario.duration} s</dd></div></dl><div className="model-card"><strong>VTMS-V1 / EM-V1</strong><span>Generic parameter set</span><span>Numerically verified</span><span>Controlled physical validation pending</span></div></aside>
    </div>
  );
}
