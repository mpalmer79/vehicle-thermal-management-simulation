import type { ScenarioCardData, ScenarioVisualKey } from "@/lib/scenarios";

type VisualTraits = {
  /** Relative air-side intensity implied by the scenario configuration, 0 to 1. */
  air: number;
  fan: "commanded" | "failed" | "none";
  thermostat: "modulating" | "closed" | "warming";
  branch: "open" | "blocked";
  /** Which element carries a degradation marker, if any. */
  degraded: "pump" | "radiator" | "airflow" | null;
  /** Relative engine thermal input implied by rpm and load, 0 to 1. */
  input: number;
  field: "cold" | "temperate" | "hot";
};

const traits: Record<ScenarioVisualKey, VisualTraits> = {
  "cold-start": { air: 0.12, fan: "none", thermostat: "warming", branch: "open", degraded: null, input: 0.35, field: "cold" },
  "ram-air": { air: 1, fan: "none", thermostat: "modulating", branch: "open", degraded: null, input: 0.68, field: "temperate" },
  "fan-idle": { air: 0.42, fan: "commanded", thermostat: "modulating", branch: "open", degraded: null, input: 0.3, field: "hot" },
  "high-load": { air: 0.6, fan: "commanded", thermostat: "modulating", branch: "open", degraded: null, input: 0.92, field: "hot" },
  "fan-failed": { air: 0, fan: "failed", thermostat: "modulating", branch: "open", degraded: null, input: 0.3, field: "hot" },
  "thermostat-closed": { air: 0.42, fan: "commanded", thermostat: "closed", branch: "blocked", degraded: null, input: 0.3, field: "hot" },
  "pump-degraded": { air: 0.6, fan: "commanded", thermostat: "modulating", branch: "open", degraded: "pump", input: 0.92, field: "hot" },
  "radiator-degraded": { air: 0.6, fan: "commanded", thermostat: "modulating", branch: "open", degraded: "radiator", input: 0.92, field: "hot" },
  "airflow-degraded": { air: 0.22, fan: "commanded", thermostat: "modulating", branch: "open", degraded: "airflow", input: 0.92, field: "hot" },
};

const W = 320;
const H = 128;

/**
 * Scenario-specific configuration visual. Every element is driven by the frozen
 * canonical scenario inputs and its declared fault state. Nothing here is a
 * prediction: no temperature, flow, or heat value is implied by the drawing.
 */
export function ScenarioVisual({ scenario }: { scenario: ScenarioCardData }) {
  const trait = traits[scenario.visual];
  const airLaneCount = trait.air === 0 ? 0 : trait.air > 0.7 ? 4 : trait.air > 0.35 ? 3 : 2;
  const airLength = 42 + trait.air * 62;

  return (
    <svg
      className={`scenario-visual field-${trait.field}`}
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`${scenario.id} configuration: ${scenario.ambient} degrees Celsius ambient, ${scenario.rpm} rpm, ${scenario.load} percent load, ${scenario.speedKmh} kilometres per hour, ${scenario.behavior}.`}
    >
      <defs>
        <linearGradient id={`field-${scenario.id}`} x1="0" x2="1" y1="0" y2="1">
          {trait.field === "cold" && <><stop offset="0%" stopColor="#eaf4fb" /><stop offset="100%" stopColor="#dbeaf6" /></>}
          {trait.field === "temperate" && <><stop offset="0%" stopColor="#eef7f5" /><stop offset="100%" stopColor="#e2f1ee" /></>}
          {trait.field === "hot" && <><stop offset="0%" stopColor="#fdf1e6" /><stop offset="100%" stopColor="#fae3d2" /></>}
        </linearGradient>
        <pattern id={`mesh-${scenario.id}`} width="16" height="16" patternUnits="userSpaceOnUse">
          <path d="M16,0 L0,0 L0,16" fill="none" stroke="#0d2438" strokeOpacity="0.05" strokeWidth="0.8" />
        </pattern>
      </defs>

      <rect width={W} height={H} fill={`url(#field-${scenario.id})`} />
      <rect width={W} height={H} fill={`url(#mesh-${scenario.id})`} />

      {/* Air side: lane count and length encode the configured ram and fan contribution. */}
      {Array.from({ length: airLaneCount }, (_, index) => {
        const y = 26 + index * (76 / Math.max(airLaneCount - 1, 1));
        return (
          <path
            className={`sv-air${trait.degraded === "airflow" ? " weak" : ""}`}
            d={`M${W - 12},${y.toFixed(1)} L${(W - 12 - airLength).toFixed(1)},${y.toFixed(1)}`}
            key={index}
            style={{ animationDelay: `${index * -0.4}s` }}
          />
        );
      })}
      {/* Engine thermal input. */}
      <rect className="sv-engine" x="18" y="34" width="72" height="60" rx="12" />
      {[0, 1, 2].map((index) => (
        <path
          className="sv-heat"
          d={`M${32 + index * 22},30 q5,-6 0,-11 t0,-11`}
          key={index}
          style={{ animationDelay: `${index * -0.7}s`, opacity: 0.25 + trait.input * 0.7 }}
        />
      ))}
      <rect className="sv-input-bar" x="18" y="100" width="72" height="6" rx="3" />
      <rect className="sv-input-fill" x="18" y="100" width={(72 * trait.input).toFixed(1)} height="6" rx="3" />

      {/* Thermostat gate. */}
      <g className={`sv-gate ${trait.thermostat}`}>
        <polygon points="128,64 146,50 164,64 146,78" />
        {trait.thermostat === "closed" ? (
          <path className="sv-gate-bar" d="M132,64 L160,64" />
        ) : (
          <path className="sv-gate-bar open" d="M146,54 L146,74" />
        )}
      </g>

      {/* Coolant branch to the radiator. */}
      <path className={`sv-branch ${trait.branch}`} d="M90,64 L126,64" />
      <path
        className={`sv-branch ${trait.branch}${trait.degraded === "pump" ? " throttled" : ""}`}
        d="M166,64 L204,64"
      />
      {trait.branch === "blocked" && <path className="sv-block" d="M176,52 L194,76 M194,52 L176,76" />}

      {/* Radiator. */}
      <rect className={`sv-radiator${trait.degraded === "radiator" ? " degraded" : ""}`} x="206" y="34" width="60" height="60" rx="10" />
      {Array.from({ length: 5 }, (_, index) => (
        <line className="sv-tube" key={index} x1={216 + index * 10} x2={216 + index * 10} y1="42" y2="86" />
      ))}
      {trait.degraded === "radiator" && (
        <g className="sv-derate">
          <path d="M236,44 L236,74" />
          <path d="M228,66 L236,76 L244,66" />
        </g>
      )}

      {/* Fan state. */}
      <g className={`sv-fan ${trait.fan}`}>
        {trait.fan !== "none" && (
          <>
            <circle cx="286" cy="104" r="15" />
            <g className="sv-fan-blades" style={{ transformOrigin: "286px 104px" }}>
              {[0, 1, 2, 3].map((index) => (
                <line
                  key={index}
                  x1="286"
                  y1="104"
                  x2={286 + Math.cos((index / 4) * Math.PI * 2) * 10}
                  y2={104 + Math.sin((index / 4) * Math.PI * 2) * 10}
                />
              ))}
            </g>
            {trait.fan === "failed" && <path className="sv-fan-cross" d="M276,94 L296,114 M296,94 L276,114" />}
          </>
        )}
      </g>
    </svg>
  );
}

export const scenarioTraits = traits;
