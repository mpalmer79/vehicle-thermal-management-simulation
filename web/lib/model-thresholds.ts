/**
 * Control thresholds already defined in the frozen VTMS-V1 parameter set
 * (`ModelParameters` in `src/vtms_v1/config.py`).
 *
 * These are model control points, not damage, boiling, or failure limits. The web
 * layer only uses them to label chart regions. Computed results returned by FastAPI
 * carry their own `parameter_snapshot`, which takes precedence when available.
 */
export type ControlThresholds = {
  thermostatOpenC: number;
  thermostatFullC: number;
  fanStartC: number;
  fanFullC: number;
};

export const defaultControlThresholds: ControlThresholds = {
  thermostatOpenC: 88,
  thermostatFullC: 98,
  fanStartC: 96,
  fanFullC: 104,
};

const numberOr = (snapshot: Record<string, number> | undefined, key: string, fallback: number) => {
  const value = snapshot?.[key];
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
};

export function thresholdsFromSnapshot(snapshot?: Record<string, number>): ControlThresholds {
  return {
    thermostatOpenC: numberOr(snapshot, "thermostat_open_c", defaultControlThresholds.thermostatOpenC),
    thermostatFullC: numberOr(snapshot, "thermostat_full_c", defaultControlThresholds.thermostatFullC),
    fanStartC: numberOr(snapshot, "fan_start_c", defaultControlThresholds.fanStartC),
    fanFullC: numberOr(snapshot, "fan_full_c", defaultControlThresholds.fanFullC),
  };
}
