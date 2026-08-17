import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two remain deliberately separate. Numerical verification is complete. Argonne controlled calibration is frozen, the primary independent physical holdout failed formal acceptance, and a separately preregistered secondary holdout also failed the core project criteria. VTMS-V1 is not physically validated.",
    detail: [
      "Numerical verification remains complete: conservation, convergence, component, and regression checks pass.",
      "CAL-01 cold-start calibration met the project calibration-stage thresholds, but wall heat fraction and engine-to-coolant UA fitted within 1% of their frozen upper bounds.",
      "CAL-RAD-01 failed the core project criteria and drove radiator UA to within 1% of its frozen lower bound. The bound was not widened and earlier parameters were not reopened.",
      "VAL-HOT-01 test 71207063 failed formal acceptance. VAL-SSS-01 test 71207052 then provided confirmatory evidence and also failed RMSE, MAE, bias, and P90 criteria with the same frozen parameters. No holdout-driven retuning is permitted.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne supplied controlled 2012 Ford Focus D3 data. Results now exist, so the earlier status 'no Argonne results exist yet' is superseded. The primary hot-start holdout 71207063 failed formal acceptance, and the separately reserved 55 mph holdout 71207052 also failed the core error criteria. VTMS-V1 did not pass controlled physical validation.",
    detail: [
      "CAL-01 used cold-start test 71207062 and fitted only wall heat fraction, effective engine capacitance, and engine-to-coolant UA within bounds frozen before residual inspection.",
      "CAL-RAD-01 used highway test 71207057 for radiator UA only. It remained outside the core criteria and landed near the frozen lower UA bound.",
      "VAL-HOT-01 produced RMSE about 8.59 °C, MAE 8.07 °C, mean bias -8.04 °C, P90 absolute error 10.05 °C, and a final prediction about 8.53 °C low.",
      "VAL-SSS-01 produced RMSE about 5.13 °C, MAE 4.11 °C, mean bias -4.01 °C, and P90 absolute error 8.40 °C. Its 80 °C and 90 °C arrival timing checks passed, but the core error criteria did not.",
      "Both comparisons used the same frozen final staged parameter snapshot with no fitting. The formal primary decision remains formal_holdout_acceptance_fail, and neither result authorizes retuning.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. The controlled Argonne calibration sequence is frozen, the primary independent physical holdout failed the preregistered acceptance criteria, and a second confirmatory holdout also failed the core error criteria.",
    detail: [
      "The earlier KIT plausibility comparison showed that the untouched generic model warmed too quickly.",
      "Controlled Argonne calibration improved the cold-start fit, but multiple effective parameters pressed against their preregistered bounds and the radiator-only stage still failed its core criteria.",
      "The primary hot-start holdout underpredicted final coolant temperature by about 8.53 °C. The secondary 55 mph holdout independently underpredicted the final value by about 8.42 °C.",
      "No parameter fitting was performed on either holdout and no retuning is permitted after observing them. Two failed independent profiles strengthen the case for a governed model-form revision rather than hidden parameter adjustment.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
