export type ScenarioVisualKey =
  | "cold-start"
  | "ram-air"
  | "fan-idle"
  | "high-load"
  | "fan-failed"
  | "thermostat-closed"
  | "pump-degraded"
  | "radiator-degraded"
  | "airflow-degraded";

export type ScenarioCardData = {
  id: string;
  name: string;
  category: "Baseline" | "Fault" | "Degradation";
  ambient: number;
  rpm: number;
  load: number;
  speedKmh: number;
  duration: number;
  purpose: string;
  /** Short behavior label used as the visual headline on scenario previews. */
  behavior: string;
  visual: ScenarioVisualKey;
  basedOn?: string;
};

export const scenarios: ScenarioCardData[] = [
  { id: "S-01", name: "Cold Start / Fast Idle", category: "Baseline", ambient: 20, rpm: 1200, load: 25, speedKmh: 0, duration: 1200, purpose: "Warm-up transient and thermostat opening", behavior: "Warm-up transient", visual: "cold-start" },
  { id: "S-02", name: "Warm Highway", category: "Baseline", ambient: 25, rpm: 2500, load: 45, speedKmh: 100.08, duration: 900, purpose: "Ram-air dominated heat rejection", behavior: "Ram-air dominated", visual: "ram-air" },
  { id: "S-03", name: "Hot Ambient Idle", category: "Baseline", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Fan-assisted idle cooling in hot ambient", behavior: "Fan-assisted idle", visual: "fan-idle" },
  { id: "S-04", name: "Sustained Higher Load", category: "Baseline", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "High thermal input with moving airflow", behavior: "High thermal input", visual: "high-load" },
  { id: "S-05", name: "Fan Failure", category: "Fault", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Loss of forced airflow at idle", behavior: "Loss of forced airflow", visual: "fan-failed", basedOn: "S-03" },
  { id: "S-06", name: "Thermostat Stuck Closed", category: "Fault", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Loss of radiator coolant flow", behavior: "Radiator branch blocked", visual: "thermostat-closed", basedOn: "S-03" },
  { id: "S-07", name: "Pump Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Reduced coolant circulation", behavior: "Reduced coolant flow", visual: "pump-degraded", basedOn: "S-04" },
  { id: "S-08", name: "Radiator Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Reduced radiator UA", behavior: "Reduced heat rejection", visual: "radiator-degraded", basedOn: "S-04" },
  { id: "S-09", name: "Airflow Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Restricted air-side heat rejection", behavior: "Restricted air side", visual: "airflow-degraded", basedOn: "S-04" }
];

export const scenarioById = (id: string) => scenarios.find((scenario) => scenario.id === id) ?? scenarios[2];
