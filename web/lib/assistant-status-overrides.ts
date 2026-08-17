import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two are kept deliberately separate. Numerical verification and external KIT plausibility are complete. Controlled physical validation is not complete; Argonne bounds and staged calibration roles are frozen before residual inspection, but physical calibration has not started.",
    detail: [
      "Stage 1, numerical verification: complete (energy conservation, convergence, component and regression checks).",
      "Stage 2, external plausibility: complete, using an independent KIT OBD-II warm-up trace with no parameter tuning.",
      "Stage 3, controlled calibration preparation: active. CAL-01 test 71207062 is restricted to wall heat fraction, effective engine capacitance, and engine-to-coolant UA. CAL-RAD-01 test 71207057 is reserved for radiator UA only.",
      "Stage 4, blind holdout validation: future. Tests 71207063 and 71207052 remain reserved holdouts and are not calibration data.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne National Laboratory supplied the requested 2012 Ford Focus D3 files on August 17, 2026. Physical bounds and staged calibration roles are frozen before residual inspection. Cold-start 71207062 is the three-parameter warm-up stage and highway 71207057 is radiator-UA only. Physical calibration and holdout validation remain pending.",
    detail: [
      "CAL-01 may fit only wall_heat_fraction, engine_thermal_capacitance_j_per_k, and engine_coolant_ua_w_per_k within their frozen physical bounds.",
      "CAL-RAD-01 may fit only radiator_ua_nominal_w_per_k after the CAL-01 snapshot is frozen. Test 71207057 was selected from source ECT and speed conditions before any VTMS residual was inspected.",
      "Hot-start test 71207063 remains the primary clean holdout, and 55 mph warm-up test 71207052 remains a secondary holdout. Neither was repurposed for fitting.",
      "The received files include direct bench fuel flow, ECT, engine speed, dyno speed, and cell temperature. No Argonne calibration or validation result exists yet.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. Argonne bounds and calibration roles are preregistered, with CAL-01 split from a radiator-only CAL-RAD-01 stage. Neither physical calibration nor independent holdout validation has been executed.",
    detail: [
      "The KIT plausibility test remains the only completed real-world comparison and showed warm-up that is substantially too fast.",
      "The broad synthetic preflight checks numerical parameter separation, while the warm-up-stage diagnostic found radiator UA weakly excited by warm-up evidence and blocked a four-parameter CAL-01 fit.",
      "Argonne test 71207057 was preregistered as the radiator-active stage from source operating conditions before any VTMS residual inspection.",
      "The parameter set is still generic and uncalibrated. Exact preprocessing hashes and immutable manifests must be frozen before physical fitting, and no Argonne validation result exists yet.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
