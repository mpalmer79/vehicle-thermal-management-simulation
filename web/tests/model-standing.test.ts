import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

import { MODEL_STANDING } from "../lib/model-standing";

type ValidationArtifact = {
  acceptance: {
    formal_validation_pass: boolean;
    overall_threshold_pass: boolean;
  };
  execution_identity: {
    run_id: string;
    source_test_id: string;
  };
};

function validationArtifact(name: string): ValidationArtifact {
  const path = resolve(process.cwd(), "..", "validation_outputs", name);
  return JSON.parse(readFileSync(path, "utf8")) as ValidationArtifact;
}

test("production standing reports the executed primary holdout failure", () => {
  const primary = validationArtifact("ARGONNE_VAL_HOT_01_FORMAL_RESULT.json");

  assert.equal(primary.execution_identity.run_id, MODEL_STANDING.controlledPhysicalValidation.primaryRunId);
  assert.equal(primary.execution_identity.source_test_id, MODEL_STANDING.controlledPhysicalValidation.primarySourceTestId);
  assert.equal(primary.acceptance.formal_validation_pass, false);
  assert.equal(primary.acceptance.overall_threshold_pass, false);
  assert.equal(MODEL_STANDING.controlledPhysicalValidation.primaryFormalValidationPass, false);
  assert.equal(MODEL_STANDING.controlledPhysicalValidation.status, "FAIL");
});

test("secondary confirmatory evidence does not replace the primary standing", () => {
  const secondary = validationArtifact("ARGONNE_VAL_SSS_01_CONFIRMATORY_RESULT.json");

  assert.equal(secondary.execution_identity.run_id, MODEL_STANDING.controlledPhysicalValidation.secondaryRunId);
  assert.equal(secondary.execution_identity.source_test_id, MODEL_STANDING.controlledPhysicalValidation.secondarySourceTestId);
  assert.equal(MODEL_STANDING.controlledPhysicalValidation.secondaryRole, "confirmatory");
  assert.equal(MODEL_STANDING.controlledPhysicalValidation.status, "FAIL");
});

test("calibration artifacts are not represented as production promotion", () => {
  assert.equal(MODEL_STANDING.calibrationPromotion.promotedToProduction, false);
  assert.equal(MODEL_STANDING.v2Development.status, "IN_PROGRESS");
});
