"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { ResultSnapshot } from "@/components/result-snapshot";
import { SignalChart } from "@/components/signal-chart";
import { InteractiveThermalSchematic } from "@/components/visuals/thermal-schematic";
import { TemperatureGauge } from "@/components/visuals/temperature-gauge";
import fixtureJson from "@/lib/fixtures/s03.json";
import { c, flow, kw, pct } from "@/lib/format";
import { defaultControlThresholds, type ControlThresholds } from "@/lib/model-thresholds";
import type { SimulationFixture } from "@/lib/vtms-types";

const defaultFixture = fixtureJson as unknown as SimulationFixture;

export function PlaybackWorkspace({
  mode = "results",
  data,
  thresholds = defaultControlThresholds,
}: {
  mode?: "overview" | "results" | "system";
  data?: SimulationFixture;
  thresholds?: ControlThresholds;
}) {
  const fixture = data ?? defaultFixture;
  const maxIndex = fixture.timeSeries.length - 1;
  /* Open on the end state so the schematic and the summary values agree on load.
     Pressing play restarts the run from t = 0. */
  const [index, setIndex] = useState(maxIndex);
  const [playing, setPlaying] = useState(false);
  const point = fixture.timeSeries[index];
  const finalPoint = fixture.timeSeries[maxIndex];
  const balancePass = fixture.energyBalance.normalized_residual <= 0.001;

  /* Scale references and gauge domains are derived from this result only. */
  const derived = useMemo(() => {
    const series = fixture.timeSeries;
    const temps = series.flatMap((item) => [item.engine_structure_temp_c, item.coolant_temp_c]);
    return {
      reference: {
        pump: Math.max(...series.map((item) => item.pump_flow_kg_s), 0),
        heat: Math.max(...series.map((item) => item.engine_to_coolant_w), 0),
      },
      domainMin: Math.floor(Math.min(...temps) / 10) * 10 - 5,
      domainMax: Math.ceil(Math.max(...temps) / 10) * 10 + 5,
      peakEngine: Math.max(...series.map((item) => item.engine_structure_temp_c)),
      peakCoolant: Math.max(...series.map((item) => item.coolant_temp_c)),
    };
  }, [fixture]);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => {
      if (index >= maxIndex) {
        setPlaying(false);
        return;
      }
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

  const ambientC = fixture.scenario?.ambient_temp_c ?? null;

  const gaugeMarks = [
    { label: "thermostat", valueC: thresholds.thermostatOpenC },
    { label: "fan", valueC: thresholds.fanStartC },
  ].filter((mark) => mark.valueC > derived.domainMin && mark.valueC < derived.domainMax);

  const playbackControl = (prominent = false) => (
    <div className={prominent ? "playback-control prominent" : "playback-control"}>
      <button
        aria-label={playing ? "Pause simulation playback" : "Play simulation playback"}
        className="playback-button"
        onClick={togglePlayback}
        type="button"
      >
        {playing ? "❙❙" : "▶"}
      </button>
      <span className="playback-time">t = {point.time_s.toFixed(0)} s</span>
      <input
        aria-label="Simulation playback time"
        max={maxIndex}
        min="0"
        onChange={(event) => scrubTo(Number(event.target.value))}
        type="range"
        value={index}
      />
      <span className="playback-duration">{fixture.scenario.duration_s.toFixed(0)} s</span>
    </div>
  );

  const gauges = (
    <div className="overview-gauges">
      <TemperatureGauge
        label="Engine"
        marks={gaugeMarks}
        maxC={derived.domainMax}
        minC={derived.domainMin}
        peakC={derived.peakEngine}
        tone="engine"
        valueC={point.engine_structure_temp_c}
      />
      <TemperatureGauge
        label="Coolant"
        marks={gaugeMarks}
        maxC={derived.domainMax}
        minC={derived.domainMin}
        peakC={derived.peakCoolant}
        tone="coolant"
        valueC={point.coolant_temp_c}
      />
    </div>
  );

  if (mode === "overview") {
    return (
      <div className="overview-playback">
        <div className="section-head">
          <div>
            <span className="eyebrow">CANONICAL SIMULATION PLAYBACK</span>
            <h2>S-03 Hot Ambient Idle</h2>
          </div>
          <span className="fixture-badge">Frozen VTMS-V1 fixture</span>
        </div>

        <div className="overview-playback-body">
          <SignalChart points={fixture.timeSeries} selectedIndex={index} thresholds={thresholds} title="Engine and coolant response" />
          {gauges}
        </div>

        {playbackControl()}

        <div className="metric-strip">
          <div><span>Radiator</span><strong>{kw(point.radiator_heat_w)}</strong></div>
          <div><span>Thermostat</span><strong>{pct(point.thermostat_fraction)}</strong></div>
          <div><span>Fan</span><strong>{pct(point.fan_fraction)}</strong></div>
          <div><span>Pump</span><strong>{flow(point.pump_flow_kg_s)}</strong></div>
        </div>

        <div className="overview-playback-foot">
          <span>Computed by the VTMS-V1 Python engine · not live telemetry</span>
          <Link className="button ghost" href="/results/demo-s03">Open full result</Link>
        </div>
      </div>
    );
  }

  if (mode === "system") {
    return (
      <div className="system-workspace">
        <div className="system-stage">
          <InteractiveThermalSchematic
            ambientC={ambientC}
            caption="Playback uses a computed result returned by the Python engine. It is not live telemetry, and the schematic is not engine-bay geometry."
            point={point}
            reference={derived.reference}
          />
          {playbackControl()}
        </div>

        <aside className="component-inspector">
          <span className="eyebrow">SYSTEM STATE</span>
          <h3>At {point.time_s.toFixed(0)} s</h3>
          {gauges}
          <dl className="inspector-values">
            <div><dt>Thermostat</dt><dd>{pct(point.thermostat_fraction)}</dd></div>
            <div><dt>Fan command</dt><dd>{pct(point.fan_fraction)}</dd></div>
            <div><dt>Radiator heat</dt><dd>{kw(point.radiator_heat_w)}</dd></div>
            <div><dt>Air flow</dt><dd>{flow(point.air_flow_kg_s)}</dd></div>
            <div><dt>Pump flow</dt><dd>{flow(point.pump_flow_kg_s)}</dd></div>
          </dl>
        </aside>
      </div>
    );
  }

  return (
    <div className="results-workspace">
      <div className="result-hero">
        <TemperatureGauge
          label="Final engine"
          marks={gaugeMarks}
          maxC={derived.domainMax}
          minC={derived.domainMin}
          peakC={derived.peakEngine}
          tone="engine"
          valueC={finalPoint.engine_structure_temp_c}
        />
        <TemperatureGauge
          label="Final coolant"
          marks={gaugeMarks}
          maxC={derived.domainMax}
          minC={derived.domainMin}
          peakC={derived.peakCoolant}
          tone="coolant"
          valueC={finalPoint.coolant_temp_c}
        />
        <div className="result-hero-facts">
          <div className="result-fact"><span>Scenario</span><strong>{fixture.scenario.scenario_id}</strong></div>
          <div className="result-fact"><span>Model</span><strong>{fixture.model.modelId} / {fixture.model.equationSet}</strong></div>
          <div className="result-fact"><span>Duration</span><strong>{fixture.scenario.duration_s.toFixed(0)} s</strong></div>
          <div className="result-fact"><span>Ambient</span><strong>{c(fixture.scenario.ambient_temp_c)}</strong></div>
          <div className="result-fact">
            <span>Energy balance</span>
            <strong className={balancePass ? "pass" : "check"}>{balancePass ? "PASS" : "CHECK"}</strong>
          </div>
        </div>
      </div>

      <SignalChart points={fixture.timeSeries} selectedIndex={index} thresholds={thresholds} />
      {playbackControl(true)}

      <InteractiveThermalSchematic
        ambientC={ambientC}
        caption="Values are read directly from the returned SimulationResult at the selected time."
        point={point}
        reference={derived.reference}
      />

      <ResultSnapshot fixture={fixture} />

      <div className={balancePass ? "energy-banner pass" : "energy-banner warn"}>
        <strong>Energy balance: {balancePass ? "PASS" : "CHECK"}</strong>
        <span>Normalized residual {(fixture.energyBalance.normalized_residual * 100).toFixed(5)}%</span>
      </div>
    </div>
  );
}
