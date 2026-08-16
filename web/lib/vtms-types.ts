export type TimeSeriesPoint = {
  time_s: number;
  engine_structure_temp_c: number;
  coolant_temp_c: number;
  radiator_outlet_temp_c: number | null;
  engine_heat_w: number;
  engine_to_coolant_w: number;
  engine_to_ambient_w: number;
  radiator_heat_w: number;
  pump_flow_kg_s: number;
  radiator_flow_kg_s: number;
  bypass_flow_kg_s: number;
  air_flow_kg_s: number;
  thermostat_fraction: number;
  fan_fraction: number;
  radiator_effectiveness: number;
  radiator_ntu: number;
};

export type ScenarioSnapshot = {
  scenario_id: string;
  name: string;
  duration_s: number;
  ambient_temp_c: number;
  engine_speed_rpm: number;
  effective_load: number;
  vehicle_speed_m_s: number;
  initial_engine_temp_c: number;
  initial_coolant_temp_c: number;
  engine_heat_override_w: number | null;
  faults: {
    fan_failed: boolean;
    thermostat_mode: "normal" | "stuck_closed" | "stuck_open";
    thermostat_health: number;
    pump_health: number;
    radiator_health: number;
    airflow_health: number;
  };
};

export type SimulationFixture = {
  fixtureId: string;
  generatedBy: string;
  samplingNote: string;
  model: {
    modelId: string;
    equationSet: string;
    status: string;
  };
  scenario: ScenarioSnapshot;
  timeSeries: TimeSeriesPoint[];
  energyBalance: {
    input_energy_j: number;
    rejected_energy_j: number;
    stored_energy_change_j: number;
    residual_j: number;
    normalized_residual: number;
  };
  warnings: string[];
  solver: {
    success: boolean;
    message: string;
    functionEvaluations: number;
  };
};
