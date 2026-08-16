"use client";

import { useEffect, useMemo, useState } from "react";
import fixtureJson from "@/lib/fixtures/s03.json";
import type { SimulationFixture } from "@/lib/vtms-types";
import { c, flow, kw, pct } from "@/lib/format";
import { ThermalLoop } from "@/components/thermal-loop";
import { SignalChart } from "@/components/signal-chart";

const defaultFixture = fixtureJson as unknown as SimulationFixture;

export function PlaybackWorkspace({
  mode = "results",
  data,
}: {
  mode?: "overview" | "results" | "system";
  data?: SimulationFixture;
}) {
  const fixture = data ?? defaultFixture;
  const [index, setIndex] = useState(Math.min(6, fixture.timeSeries.length - 1));
  const [playing, setPlaying] = useState(false);
  const point = fixture.timeSeries[index];
  const maxIndex = fixture.timeSeries.length - 1;
  const finalPoint = fixture.timeSeries[maxIndex];
  const balancePass = fixture.energyBalance.normalized_residual <= 0.001;
  const selected = useMemo(() => ({
    engine: c(point.engine_structure_temp_c), coolant: c(point.coolant_temp_c), radiator: kw(point.radiator_heat_w),
    pump: flow(point.pump_flow_kg_s), air: flow(point.air_flow_kg_s), thermostat: pct(point.thermostat_fraction), fan: pct(point.fan_fraction),
  }), [point]);

  useEffect(() => {
    if (!playing) return;
    if (index >= maxIndex) {
      setPlaying(false);
      return;
    }
    const timer = window.setTimeout(() => {
      setIndex((value) => Math.min(value + 1, maxIndex));
    }, 500);
    return () => window.clearTimeout(timer);
  }, [index, maxIndex, playing]);

  const togglePlayback = () => {
    if (!playing && index >= maxIndex) setIndex(0);
    setPlaying((value) => !value);
  };

  const scrubTo = (nextIndex: number) => {
    setPlaying(false);
    setIndex(nextIndex);
  };

  const playbackControl = (prominent = false) => (
    <div className={prominent ? "playback-control prominent" : "playback-control"}>
      <button className="playback-button" type="button" onClick={togglePlayback} aria-label={playing ? "Pause simulation playback" : "Play simulation playback"}>
        {playing ? "Ⅱ" : "▶"}
      </button>
      <span className="playback-time">t = {point.time_s.toFixed(0)} s</span>
      <input aria-label="Simulation playback time" min="0" max={maxIndex} value={index} onChange={(event) => scrubTo(Number(event.target.value))} type="range" />
      <span>{fixture.scenario.duration_s.toFixed(0)} s</span>
    </div>
  );

  if (mode === "overview") {
    return (
      <div className="overview-playback">
        <div className="section-head"><div><span className="eyebrow">CANONICAL SIMULATION PLAYBACK</span><h2>S-03 Hot Ambient Idle</h2></div><span className="fixture-badge">Frozen VTMS-V1 fixture</span></div>
        <ThermalLoop point={point} compact />
        {playbackControl()}
        <div className="metric-strip"><div><span>Engine</span><strong>{selected.engine}</strong></div><div><span>Coolant</span><strong>{selected.coolant}</strong></div><div><span>Radiator</span><strong>{selected.radiator}</strong></div><div><span>Pump</span><strong>{selected.pump}</strong></div></div>
      </div>
    );
  }

  if (mode === "system") {
    return (
      <div className="system-workspace">
        <div className="system-stage"><ThermalLoop point={point} />{playbackControl()}</div>
        <aside className="component-inspector"><span className="eyebrow">SELECTED STATE</span><h3>System at {point.time_s.toFixed(0)} s</h3><dl><div><dt>Engine</dt><dd>{selected.engine}</dd></div><div><dt>Coolant</dt><dd>{selected.coolant}</dd></div><div><dt>Thermostat</dt><dd>{selected.thermostat}</dd></div><div><dt>Fan command</dt><dd>{selected.fan}</dd></div><div><dt>Radiator heat</dt><dd>{selected.radiator}</dd></div><div><dt>Air flow</dt><dd>{selected.air}</dd></div></dl><p className="muted-note">Playback uses a computed result returned by the Python engine. It is not live telemetry.</p></aside>
      </div>
    );
  }

  return (
    <div className="results-workspace">
      <div className="result-summary">
        <article><span>Current time</span><strong>{point.time_s.toFixed(0)} s</strong></article>
        <article><span>Final engine</span><strong className="hot-value">{c(finalPoint.engine_structure_temp_c)}</strong></article>
        <article><span>Final coolant</span><strong className="cool-value">{c(finalPoint.coolant_temp_c)}</strong></article>
        <article><span>Energy balance</span><strong className={balancePass ? "pass-value" : ""}>{balancePass ? "PASS" : "CHECK"}</strong></article>
      </div>
      <SignalChart points={fixture.timeSeries} selectedIndex={index} />
      {playbackControl(true)}
      <div className="results-grid"><ThermalLoop point={point} /><div className="selected-values"><span className="eyebrow">SELECTED VALUES</span><dl><div><dt>Q engine</dt><dd>{kw(point.engine_heat_w)}</dd></div><div><dt>Q radiator</dt><dd>{selected.radiator}</dd></div><div><dt>Pump flow</dt><dd>{selected.pump}</dd></div><div><dt>Air flow</dt><dd>{selected.air}</dd></div><div><dt>Thermostat</dt><dd>{selected.thermostat}</dd></div><div><dt>Fan</dt><dd>{selected.fan}</dd></div></dl></div></div>
      {fixture.warnings.map((warning) => <div className="engineering-warning" key={warning}><strong>Model warning</strong><span>{warning}</span></div>)}
      <div className={balancePass ? "energy-banner pass" : "energy-banner warn"}><strong>Energy balance: {balancePass ? "PASS" : "CHECK"}</strong><span>Normalized residual {(fixture.energyBalance.normalized_residual * 100).toFixed(5)}%</span></div>
    </div>
  );
}
