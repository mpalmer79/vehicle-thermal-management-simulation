import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two are kept deliberately separate. Numerical verification is complete and external KIT plausibility is complete. Controlled physical validation is not complete; Argonne D3 data are acquired and fingerprinted, and the pre-fit identifiability gate has split calibration into a three-parameter warm-up stage plus a separate radiator-UA stage.",
    detail: [
      "Stage 1, numerical verification: complete (energy conservation, convergence, component and regression checks).",
      "Stage 2, external plausibility: complete, using an independent KIT OBD-II warm-up trace with no parameter tuning.",
      "Stage 3, controlled calibration preparation: active. CAL-01 test 71207062 is restricted to wall heat fraction, effective engine capacitance, and engine-to-coolant UA. CAL-RAD-01 test 71207057 is reserved for radiator UA only.",
      "Stage 4, blind holdout validation: future. Tests 71207063 and 71207052 remain reserved holdouts and are not calibration data.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne National Laboratory supplied the requested 2012 Ford Focus D3 files on August 17, 2026. Acquisition and source fingerprinting are complete. Pre-fit analysis now reserves cold-start 71207062 for a three-parameter warm-up calibration and highway test 71207057 for radiator UA only. Physical calibration and holdout validation remain pending.",
    detail: [
      "CAL-01 uses test 71207062 and may fit only wall_heat_fraction, engine_thermal_capacitance_j_per_k, and engine_coolant_ua_w_per_k after their physical bounds are frozen.",
      "CAL-RAD-01 uses test 71207057 and may fit only radiator_ua_nominal_w_per_k after the CAL-01 snapshot and radiator-UA bound are frozen. The role was selected from source ECT and speed conditions before any VTMS residual was inspected.",
      "Hot-start test 71207063 remains the primary clean holdout, and 55 mph warm-up test 71207052 remains a secondary holdout. Neither was repurposed for fitting.",
      "The received files include direct bench fuel flow, ECT, engine speed, dyno speed, and cell temperature. Physical bounds remain unresolved and no Argonne calibration result exists yet.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. Argonne controlled data are acquired and fingerprinted. The calibration structure is now staged: CAL-01 is a three-parameter warm-up fit candidate and CAL-RAD-01 is radiator-UA only. Neither physical calibration nor independent holdout validation has been executed.",
    detail: [
      "The KIT plausibility test remains the only completed real-world comparison and showed warm-up that is substantially too fast.",
      "The synthetic identifiability gate found radiator UA weakly excited by warm-up profiles, so it was removed from the CAL-01 fitted subset before any Argonne residual was inspected.",
      "Argonne test 71207057 was preregistered as CAL-RAD-01 from source operating conditions because it has complete hot ECT and sustained highway speed. It is radiator-UA only.",
      "The parameter set is still generic and uncalibrated. Physical bounds, exact mapping hashes, and immutable manifests must be frozen before either Argonne fit, and no Argonne validation result exists yet.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
