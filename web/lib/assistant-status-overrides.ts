import type { KnowledgeTopic } from "./assistant-knowledge";

const STATUS_OVERRIDES: Record<string, Pick<KnowledgeTopic, "shortAnswer" | "detail">> = {
  "verification-and-validation": {
    shortAnswer:
      "The two remain deliberately separate. Numerical verification is complete. Argonne controlled calibration has been executed, and the primary independent physical holdout was then run once with frozen parameters. That holdout failed the preregistered acceptance criteria, so VTMS-V1 is not physically validated.",
    detail: [
      "Numerical verification remains complete: conservation, convergence, component, and regression checks pass.",
      "CAL-01 cold-start calibration met the project calibration-stage thresholds, but wall heat fraction and engine-to-coolant UA fitted within 1% of their frozen upper bounds.",
      "CAL-RAD-01 failed the core project criteria and drove radiator UA to within 1% of its frozen lower bound. The bound was not widened and earlier parameters were not reopened.",
      "VAL-HOT-01 test 71207063 was executed as the untouched primary physical holdout with the final staged parameter snapshot. It failed formal acceptance. No holdout-driven retuning is permitted.",
    ],
  },
  argonne: {
    shortAnswer:
      "Argonne supplied controlled 2012 Ford Focus D3 data. VTMS completed its preregistered staged calibration and then executed the untouched hot-start holdout 71207063. The holdout failed the project criteria: RMSE was about 8.59 °C, MAE 8.07 °C, mean bias -8.04 °C, and P90 absolute error 10.05 °C. VTMS-V1 therefore did not pass controlled physical validation.",
    detail: [
      "CAL-01 used cold-start test 71207062 and fitted only wall heat fraction, effective engine capacitance, and engine-to-coolant UA within bounds frozen before residual inspection.",
      "CAL-RAD-01 used highway test 71207057 for radiator UA only. It remained outside the core criteria and landed near the frozen lower UA bound.",
      "VAL-HOT-01 used hot-start test 71207063 with no parameter fitting. Final predicted coolant temperature was about 90.47 °C versus 99.0 °C measured, and 90 °C arrival was about 125.6 s late.",
      "The formal decision is formal_holdout_acceptance_fail. The failed comparison is preserved and does not authorize retuning against the holdout.",
    ],
  },
  "validation-status": {
    shortAnswer:
      "VTMS-V1 is numerically verified but not physically validated. The controlled Argonne calibration sequence has been executed and frozen, and the primary independent physical holdout failed the preregistered acceptance criteria.",
    detail: [
      "The earlier KIT plausibility comparison already showed that the untouched generic model warmed too quickly.",
      "Controlled Argonne calibration improved the cold-start fit, but multiple effective parameters pressed against their preregistered bounds and the radiator-only stage still failed its core criteria.",
      "The untouched hot-start holdout then produced RMSE 8.59 °C, MAE 8.07 °C, mean bias -8.04 °C, and P90 absolute error 10.05 °C.",
      "No parameter fitting was performed on the holdout and no retuning is permitted after observing it. The result points toward model-form limitations that require a future governed model revision rather than hidden parameter adjustment.",
    ],
  },
};

export function withCurrentProjectStatus(topic: KnowledgeTopic): KnowledgeTopic {
  const override = STATUS_OVERRIDES[topic.id];
  return override ? { ...topic, ...override } : topic;
}
