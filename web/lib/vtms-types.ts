export type ThermostatMode = "normal" | "stuck_closed" | "stuck_open";

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
    thermostat_mode: ThermostatMode;
    thermostat_health: number;
    pump_health: number;
    radiator_health: number;
    airflow_health: number;
  };
};

export type EnergyBalance = {
  input_energy_j: number;
  rejected_energy_j: number;
  stored_energy_change_j: number;
  residual_j: number;
  normalized_residual: number;
};

export type ModelMetadata = {
  model_id: string;
  model_version: string;
  equation_set: string;
  reference_vehicle: string;
  coolant_property_set: string;
  parameter_set: string;
  validation_status: string;
  classification: string;
  digital_twin_status: string;
};

export type SolverDiagnostics = {
  success: boolean;
  status: number;
  message: string;
  function_evaluations: number;
  jacobian_evaluations: number;
  lu_decompositions: number;
};

export type CoreSimulationResult = {
  model_metadata: ModelMetadata;
  scenario_metadata: ScenarioSnapshot;
  parameter_snapshot: Record<string, number>;
  provenance_snapshot: Record<string, string>;
  time_series: TimeSeriesPoint[];
  events: Array<Record<string, string | number>>;
  energy_balance: EnergyBalance;
  warnings: string[];
  solver_diagnostics: SolverDiagnostics;
};

export type SimulationApiResponse = {
  run_id: string;
  classification: "computed_simulation";
  result: CoreSimulationResult;
};

export type SimulationRequestInput = {
  scenario_id: string;
  name: string;
  duration_s: number;
  ambient_temp_c: number;
  engine_speed_rpm: number;
  effective_load_percent: number;
  vehicle_speed_kmh: number;
  initial_engine_temp_c: number;
  initial_coolant_temp_c: number;
  engine_heat_override_w: number | null;
  output_interval_s: number;
  faults: {
    fan_failed: boolean;
    thermostat_mode: ThermostatMode;
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
  energyBalance: EnergyBalance;
  warnings: string[];
  solver: {
    success: boolean;
    message: string;
    functionEvaluations: number;
  };
};
