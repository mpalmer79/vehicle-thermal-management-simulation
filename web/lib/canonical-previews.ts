import previewJson from "@/lib/fixtures/canonical-previews.json";

export type PreviewTracePoint = { t: number; engineC: number; coolantC: number };

export type CanonicalPreview = {
  scenarioId: string;
  name: string;
  durationS: number;
  trace: PreviewTracePoint[];
  endState: {
    engineC: number;
    coolantC: number;
    thermostatFraction: number;
    fanFraction: number;
    radiatorHeatW: number;
    airFlowKgS: number;
    pumpFlowKgS: number;
  };
  peak: { engineC: number; coolantC: number };
  energyBalance: { normalizedResidual: number };
  warnings: string[];
};

export type CanonicalPreviewFile = {
  fixtureId: string;
  generatedBy: string;
  samplingNote: string;
  model: { modelId: string; equationSet: string; status: string };
  scenarios: CanonicalPreview[];
};

/**
 * Sampled canonical scenario results produced by the authoritative VTMS-V1 Python
 * engine via `generate_ui_previews.py`. These are computed simulation outputs, not
 * telemetry, and not values authored in the browser.
 */
export const canonicalPreviewFile = previewJson as CanonicalPreviewFile;

const byId = new Map(canonicalPreviewFile.scenarios.map((preview) => [preview.scenarioId, preview]));

export const previewFor = (scenarioId: string): CanonicalPreview | undefined => byId.get(scenarioId);
