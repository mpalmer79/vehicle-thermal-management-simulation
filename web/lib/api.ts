import type {
  SimulationApiResponse,
  SimulationRequestInput,
  SimulationFixture,
} from "@/lib/vtms-types";

const DEFAULT_API_URL = "http://localhost:8000";

export const apiBaseUrl = () =>
  (process.env.NEXT_PUBLIC_VTMS_API_URL ?? DEFAULT_API_URL).replace(/\/$/, "");

export async function runSimulation(
  payload: SimulationRequestInput,
): Promise<SimulationApiResponse> {
  const response = await fetch(`${apiBaseUrl()}/api/v1/simulations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = `Simulation request failed with HTTP ${response.status}`;
    try {
      const error = (await response.json()) as { detail?: unknown };
      if (typeof error.detail === "string") message = error.detail;
      else if (error.detail) message = JSON.stringify(error.detail);
    } catch {
      // Keep the HTTP status message if the body is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as SimulationApiResponse;
}

export function apiResponseToFixture(response: SimulationApiResponse): SimulationFixture {
  const { result } = response;
  const spacing = result.time_series.length > 1
    ? result.time_series[1].time_s - result.time_series[0].time_s
    : result.scenario_metadata.duration_s;

  return {
    fixtureId: response.run_id,
    generatedBy: "FastAPI → authoritative VTMS-V1 Python engine",
    samplingNote: `${spacing.toFixed(2)} s result output interval`,
    model: {
      modelId: result.model_metadata.model_id,
      equationSet: result.model_metadata.equation_set,
      status: result.model_metadata.validation_status,
    },
    scenario: result.scenario_metadata,
    timeSeries: result.time_series,
    energyBalance: result.energy_balance,
    warnings: result.warnings,
    solver: {
      success: result.solver_diagnostics.success,
      message: result.solver_diagnostics.message,
      functionEvaluations: result.solver_diagnostics.function_evaluations,
    },
  };
}
