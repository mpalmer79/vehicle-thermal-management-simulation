import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two are kept deliberately separate. Numerical verification is complete and external KIT plausibility is complete. Controlled physical validation is not complete; Argonne D3 data are acquired and fingerprinted, and a synthetic pre-fit identifiability gate now requires staged calibration before any physical fit.",
    detail: [
      "Stage 1, numerical verification: complete (energy conservation, convergence, component and regression checks).",
      "Stage 2, external plausibility: complete, using an independent KIT OBD-II warm-up trace with no parameter tuning.",
      "Stage 3, controlled calibration preparation: active. The synthetic identifiability gate found radiator UA weakly excited by warm-up profiles, so a four-parameter simultaneous CAL-01 fit is not authorized.",
      "Stage 4, blind holdout validation: future, and only after the calibration subset and physical bounds are frozen.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne National Laboratory supplied the requested 2012 Ford Focus D3 files on August 17, 2026. Acquisition and source fingerprinting are complete; signal mapping and data qualification are in progress. A synthetic pre-fit identifiability gate is complete, but controlled calibration and physical holdout validation remain pending.",
    detail: [
      "Cold-start UDDS test 71207062 is the CAL-01 candidate after explicit ECT quality selection; hot-start UDDS test 71207063 is reserved as the primary clean holdout candidate.",
      "The received files include direct bench fuel flow, ECT, engine speed, dyno speed, and cell temperature. MAF is not used as formal heat-input evidence.",
      "The pre-fit synthetic sensitivity matrix is full-rank, but radiator UA contributes less than one percent of the strongest RMS coolant sensitivity across the combined warm-up profiles. A four-parameter simultaneous CAL-01 fit is therefore blocked.",
      "Physical calibration bounds remain unresolved. A manifest-declared warm-up-sensitive subset and any separate radiator-active calibration role must be frozen before physical fitting.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. Argonne controlled data are acquired and fingerprinted, and the pre-fit synthetic identifiability gate found weak radiator-UA excitation. Controlled calibration and independent holdout validation have not yet been executed.",
    detail: [
      "The KIT plausibility test remains the only completed real-world comparison and showed warm-up that is substantially too fast.",
      "Argonne signal mapping and source-data qualification are in progress, including explicit treatment of coolant-temperature acquisition artifacts.",
      "The synthetic identifiability result supports staged calibration rather than fitting all four governed parameters simultaneously in CAL-01.",
      "The parameter set is still generic and uncalibrated. Physical bounds and the final CAL-01 fitted subset must be frozen before any Argonne fit, and no Argonne validation result exists yet.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
