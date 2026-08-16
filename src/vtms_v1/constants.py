MODEL_ID = "VTMS-V1"
MODEL_VERSION = "1.0.0"
EQUATION_SET = "EM-V1"
REFERENCE_VEHICLE = "GRV-V1"
COOLANT_PROPERTY_SET = "EG50-CONST-V1"
PARAMETER_SET = "GRV-V1-PARAMS-1"
VALIDATION_STATUS = "numerical_verified_generic_uncalibrated"

FLOW_EPS = 1.0e-10
ABSOLUTE_ZERO_C = -273.15

# Implementation warning boundary only. This is not a boiling point, damage
# threshold, or OEM limit. VTMS-V1 does not model pressure or phase change.
LIQUID_MODEL_CAUTION_C = 120.0
