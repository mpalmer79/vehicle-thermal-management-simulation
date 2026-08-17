import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two are kept deliberately separate. Numerical verification is complete and external KIT plausibility is complete. Controlled physical validation is not complete; Argonne D3 data are now acquired and fingerprinted, with signal qualification in progress before calibration.",
    detail: [
      "Stage 1, numerical verification: complete (energy conservation, convergence, component and regression checks).",
      "Stage 2, external plausibility: complete, using an independent KIT OBD-II warm-up trace with no parameter tuning.",
      "Stage 3, controlled calibration preparation: active. Argonne source data are received; mapping, ECT quality controls, and physical calibration bounds must be frozen before fitting.",
      "Stage 4, blind holdout validation: future, and only after calibration is frozen.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne National Laboratory supplied the requested 2012 Ford Focus D3 files on August 17, 2026. Acquisition and source fingerprinting are complete; signal mapping and data qualification are in progress. Calibration has not started and no Argonne results exist yet.",
    detail: [
      "The controlled workflow is Acquire → Hash → Map → Calibrate → Freeze → Holdout → Report; Acquire and Hash are complete and Map is active.",
      "Cold-start UDDS test 71207062 is the CAL-01 candidate after explicit ECT quality selection; hot-start UDDS test 71207063 is reserved as the primary clean holdout candidate.",
      "The received files include direct bench fuel flow, ECT, engine speed, dyno speed, and cell temperature. MAF is not used as formal heat-input evidence.",
      "Physical calibration bounds remain unresolved and must be justified and frozen before the first fit. Calibration and holdout results are still pending.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. Argonne controlled data have now been acquired and fingerprinted, but controlled calibration and independent holdout validation have not yet been executed.",
    detail: [
      "The KIT plausibility test remains the only completed real-world comparison and showed warm-up that is substantially too fast.",
      "Argonne signal mapping and source-data qualification are in progress, including explicit treatment of coolant-temperature acquisition artifacts.",
      "The parameter set is still generic and uncalibrated, so there is no vehicle-specific accuracy claim to make.",
      "Physical calibration bounds must be frozen before any Argonne fit; no Argonne validation result exists yet.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
