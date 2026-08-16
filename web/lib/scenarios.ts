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
  basedOn?: string;
};

export const scenarios: ScenarioCardData[] = [
  { id: "S-01", name: "Cold Start / Fast Idle", category: "Baseline", ambient: 20, rpm: 1200, load: 25, speedKmh: 0, duration: 1200, purpose: "Warm-up transient and thermostat opening" },
  { id: "S-02", name: "Warm Highway", category: "Baseline", ambient: 25, rpm: 2500, load: 45, speedKmh: 100.08, duration: 900, purpose: "Ram-air dominated heat rejection" },
  { id: "S-03", name: "Hot Ambient Idle", category: "Baseline", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Fan-assisted idle cooling in hot ambient" },
  { id: "S-04", name: "Sustained Higher Load", category: "Baseline", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "High thermal input with moving airflow" },
  { id: "S-05", name: "Fan Failure", category: "Fault", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Loss of forced airflow at idle", basedOn: "S-03" },
  { id: "S-06", name: "Thermostat Stuck Closed", category: "Fault", ambient: 40, rpm: 1000, load: 25, speedKmh: 0, duration: 1200, purpose: "Loss of radiator coolant flow", basedOn: "S-03" },
  { id: "S-07", name: "Pump Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Reduced coolant circulation", basedOn: "S-04" },
  { id: "S-08", name: "Radiator Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Reduced radiator UA", basedOn: "S-04" },
  { id: "S-09", name: "Airflow Degradation", category: "Degradation", ambient: 35, rpm: 3000, load: 55, speedKmh: 54, duration: 1200, purpose: "Restricted air-side heat rejection", basedOn: "S-04" }
];

export const scenarioById = (id: string) => scenarios.find((scenario) => scenario.id === id) ?? scenarios[2];
