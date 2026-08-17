import { c, kw, pct } from "@/lib/format";
import type { SimulationFixture } from "@/lib/vtms-types";

/**
 * Deterministic summary of a returned result.
 *
 * Every item is a direct read or an arithmetic reduction of values already present in the
 * authoritative SimulationResult. Nothing here diagnoses a mechanical condition, infers a
 * damage threshold, or estimates a quantity the model did not compute.
 */
export function ResultSnapshot({ fixture }: { fixture: SimulationFixture }) {
  const series = fixture.timeSeries;
  const final = series[series.length - 1];

  const peakEngine = Math.max(...series.map((point) => point.engine_structure_temp_c));
  const peakCoolant = Math.max(...series.map((point) => point.coolant_temp_c));
  const maxFan = Math.max(...series.map((point) => point.fan_fraction));
  const fanFirst = series.find((point) => point.fan_fraction > 0);
  const radiatorFlowing = series.some((point) => point.radiator_flow_kg_s > 0);
  const balancePass = fixture.energyBalance.normalized_residual <= 0.001;

  const items = [
    {
      key: "peak",
      label: "Peak engine",
      value: c(peakEngine),
      detail: `coolant peak ${c(peakCoolant)}`,
      state: "",
    },
    {
      key: "fan",
      label: "Fan activated",
      value: maxFan > 0 ? "Yes" : "No",
      detail: maxFan > 0
        ? `first command at ${fanFirst!.time_s.toFixed(0)} s · max ${pct(maxFan)}`
        : "fan command stayed at 0% for the whole run",
      state: maxFan > 0 ? "state-yes" : "state-no",
    },
    {
      key: "thermostat",
      label: "Thermostat at end",
      value: pct(final.thermostat_fraction),
      detail: radiatorFlowing ? "radiator branch carried flow" : "no radiator flow during the run",
      state: "",
    },
    {
      key: "rejection",
      label: "Radiator at end",
      value: kw(final.radiator_heat_w),
      detail: `engine input ${kw(final.engine_heat_w)}`,
      state: "",
    },
  ];

  return (
    <section className="snapshot">
      <div className="section-head">
        <div>
          <span className="eyebrow">DETERMINISTIC RESULT SUMMARY</span>
          <h2>What the run shows</h2>
        </div>
        <span className={balancePass ? "status-pill verified" : "status-pill warning"}>
          Energy balance {balancePass ? "PASS" : "CHECK"}
        </span>
      </div>

      <div className="snapshot-grid">
        {items.map((item) => (
          <article className={`snapshot-item ${item.state}`} key={item.key}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </article>
        ))}
      </div>

      {fixture.warnings.map((warning) => (
        <div className="engineering-warning" key={warning}>
          <strong>Model warning</strong>
          <span>{warning}</span>
        </div>
      ))}
    </section>
  );
}
