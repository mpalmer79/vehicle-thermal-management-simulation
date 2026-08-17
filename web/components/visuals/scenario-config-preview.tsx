import type { ThermostatMode } from "@/lib/vtms-types";

export type ConfigPreviewInput = {
  ambientC: number;
  rpm: number;
  loadPercent: number;
  speedKmh: number;
  fanFailed: boolean;
  thermostatMode: ThermostatMode;
  pumpHealthPct: number;
  radiatorHealthPct: number;
  airflowHealthPct: number;
};

const W = 320;
const H = 176;

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

function ambientClass(ambientC: number) {
  if (ambientC <= 10) return "cp-ambient-cold";
  if (ambientC <= 25) return "cp-ambient-mild";
  if (ambientC <= 34) return "cp-ambient-warm";
  return "cp-ambient-hot";
}

/**
 * Visualises the configuration a run will be submitted with. It renders only what the
 * user has entered plus the declared fault state.
 *
 * It performs no thermal calculation and predicts no temperature, flow, or heat value.
 * Those come back from the FastAPI/Python engine after the run.
 */
export function ScenarioConfigPreview({ config }: { config: ConfigPreviewInput }) {
  const ram = clamp01(config.speedKmh / 120);
  const airflowHealth = clamp01(config.airflowHealthPct / 100);
  const pumpHealth = clamp01(config.pumpHealthPct / 100);
  const radiatorHealth = clamp01(config.radiatorHealthPct / 100);
  const input = clamp01((config.rpm / 6000) * 0.5 + (config.loadPercent / 100) * 0.5);

  /* Air-side intensity is a symbolic blend of configured road speed, fan availability,
     and airflow health. It is an indication of configuration, not a computed mass flow. */
  const airIntensity = clamp01((ram * 0.65 + (config.fanFailed ? 0 : 0.35)) * airflowHealth);
  const airLanes = airIntensity <= 0.01 ? 0 : airIntensity > 0.55 ? 3 : 2;
  const airReduced = airIntensity < 0.5;
  const branch = config.thermostatMode === "stuck_closed" ? "blocked" : pumpHealth < 1 ? "reduced" : "";

  return (
    <svg
      className="config-preview"
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`Configuration preview: ${config.ambientC} degrees Celsius ambient, ${config.rpm} rpm, ${config.loadPercent} percent load, ${config.speedKmh} kilometres per hour, fan ${config.fanFailed ? "failed" : "available"}, thermostat ${config.thermostatMode.replace("_", " ")}.`}
    >
      <rect className={ambientClass(config.ambientC)} width={W} height={H} />

      {Array.from({ length: airLanes }, (_, index) => {
        const y = 44 + index * (50 / Math.max(airLanes - 1, 1));
        return (
          <path
            className={`cp-air${airReduced ? " reduced" : ""}`}
            d={`M${W - 8},${y.toFixed(1)} L262,${y.toFixed(1)}`}
            key={index}
            style={{ animationDelay: `${index * -0.4}s` }}
          />
        );
      })}

      {/* Engine thermal input from rpm and load, drawn as a filled bar, not a temperature. */}
      <rect className="cp-engine" x="16" y="40" width="70" height="58" rx="12" />
      <rect className="cp-engine-fill" x="24" y={92 - 40 * input} width="54" height={Math.max(4, 40 * input)} rx="6" />
      <text className="cp-label" x="16" y="116">ENGINE INPUT</text>

      <path className={`cp-loop ${branch}`} d="M86,68 L126,68" />
      <polygon className={`cp-thermostat${config.thermostatMode === "normal" ? "" : " fault"}`} points="146,52 164,68 146,84 128,68" />
      <path className={`cp-loop ${branch}`} d="M166,68 L200,68" />
      {config.thermostatMode === "stuck_closed" && <path className="cp-cross" d="M174,58 L192,78 M192,58 L174,78" />}

      <rect className={`cp-rad${radiatorHealth < 1 ? " degraded" : ""}`} x="202" y="40" width="58" height="58" rx="10" />
      {Array.from({ length: 5 }, (_, index) => (
        <line className="cp-tube" key={index} x1={212 + index * 9.5} x2={212 + index * 9.5} y1="48" y2="90" />
      ))}
      <text className="cp-label" x="202" y="116">RADIATOR</text>

      <g className={`cp-fan${config.fanFailed ? " failed" : ""}`}>
        <circle cx="282" cy="69" r="18" />
        <g className="cp-fan-blades" style={{ transformOrigin: "282px 69px" }}>
          {[0, 1, 2, 3].map((index) => (
            <line
              key={index}
              x1="282"
              y1="69"
              x2={282 + Math.cos((index / 4) * Math.PI * 2) * 12}
              y2={69 + Math.sin((index / 4) * Math.PI * 2) * 12}
            />
          ))}
        </g>
        {config.fanFailed && <path className="cp-cross" d="M271,58 L293,80 M293,58 L271,80" />}
      </g>
      <text className="cp-label" x="282" y="102" textAnchor="middle">{config.fanFailed ? "FAN FAILED" : "FAN"}</text>

      <text className="cp-label" x="16" y="146">{config.ambientC} °C AMBIENT</text>
      <text className="cp-label" x="16" y="162">{config.speedKmh} KM/H · {config.rpm} RPM · {config.loadPercent}% LOAD</text>
    </svg>
  );
}
