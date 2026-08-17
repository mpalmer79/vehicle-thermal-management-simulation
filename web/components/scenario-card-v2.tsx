import Link from "next/link";

import { MiniSparkline } from "@/components/visuals/mini-sparkline";
import { ScenarioVisual } from "@/components/visuals/scenario-visual";
import { previewFor } from "@/lib/canonical-previews";
import type { ScenarioCardData } from "@/lib/scenarios";

export function ScenarioCardV2({ scenario }: { scenario: ScenarioCardData }) {
  const preview = previewFor(scenario.id);
  const hasWarning = (preview?.warnings.length ?? 0) > 0;

  return (
    <article className={`scenario-card-v2 ${scenario.category.toLowerCase()}`}>
      <div className="scenario-media">
        <ScenarioVisual scenario={scenario} />
        <span className="scenario-id-chip">{scenario.id}</span>
        <span className={`scenario-type ${scenario.category.toLowerCase()}`}>{scenario.category}</span>
        <span className="scenario-behavior">{scenario.behavior}</span>
      </div>

      <div className="scenario-body">
        <h3>{scenario.name}</h3>

        <dl className="scenario-conditions">
          <div><dt>Ambient</dt><dd>{scenario.ambient} °C</dd></div>
          <div><dt>Engine</dt><dd>{scenario.rpm} rpm</dd></div>
          <div><dt>Load</dt><dd>{scenario.load}%</dd></div>
          <div><dt>Vehicle</dt><dd>{scenario.speedKmh} km/h</dd></div>
        </dl>

        {preview && (
          <div className="scenario-outcome">
            <div className="scenario-outcome-trace">
              <MiniSparkline
                height={54}
                series={[
                  { id: `${scenario.id}-engine`, tone: "engine", values: preview.trace.map((point) => point.engineC) },
                  { id: `${scenario.id}-coolant`, tone: "coolant", values: preview.trace.map((point) => point.coolantC) },
                ]}
                title={`${scenario.id} canonical engine and coolant temperature over ${preview.durationS.toFixed(0)} seconds`}
                width={260}
              />
              <span className="scenario-outcome-label">Canonical run · {preview.durationS.toFixed(0)} s</span>
            </div>
            <div className="scenario-outcome-values">
              <span className="engine"><b>{preview.endState.engineC.toFixed(1)}</b> °C engine</span>
              <span className="coolant"><b>{preview.endState.coolantC.toFixed(1)}</b> °C coolant</span>
            </div>
          </div>
        )}

        {hasWarning && (
          <p className="scenario-caution">
            <span aria-hidden="true">!</span>
            Model caution boundary reached · qualitative above 120 °C
          </p>
        )}

        <div className="scenario-cta">
          <Link className="button primary" href={`/simulate?scenario=${scenario.id}`}>
            Simulate this scenario
          </Link>
          {scenario.id === "S-03" && (
            <Link className="button ghost" href="/results/demo-s03">
              Result playback
            </Link>
          )}
        </div>
      </div>
    </article>
  );
}
