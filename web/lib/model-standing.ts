export const MODEL_STANDING = {
  productionModelId: "VTMS-V1",
  equationSet: "EM-V1",
  numericalVerification: {
    status: "PASS",
    label: "Numerical verification suite",
  },
  controlledPhysicalValidation: {
    status: "FAIL",
    label: "Controlled physical validation",
    primaryRunId: "VAL-HOT-01",
    primarySourceTestId: "71207063",
    primaryFormalValidationPass: false,
    secondaryRunId: "VAL-SSS-01",
    secondarySourceTestId: "71207052",
    secondaryRole: "confirmatory",
  },
  v2Development: {
    status: "IN_PROGRESS",
    label: "VTMS-V2 model-form revision",
  },
  calibrationPromotion: {
    promotedToProduction: false,
  },
} as const;

export type StandingStatus = "PASS" | "FAIL" | "IN_PROGRESS";

export function standingClass(status: StandingStatus) {
  if (status === "PASS") return "verified";
  if (status === "FAIL") return "failed";
  return "pending";
}
