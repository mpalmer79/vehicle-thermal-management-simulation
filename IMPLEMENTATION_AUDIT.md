# VTMS-V1 Implementation Audit

## Scope

This audit records implementation decisions made while translating Engineering Model Specification 1.0.0 into executable Python.

## Equation compliance

The implementation preserves the frozen two-state ODE structure and the equations defined by E-06 through E-44. No additional thermal state was introduced. Radiator outlet temperature remains algebraic.

## Specification gap identified

The specification requires an out-of-liquid-model warning but does not freeze a numerical warning boundary. The implementation uses `LIQUID_MODEL_CAUTION_C = 120.0` solely as a conservative software warning trigger.

The setting is explicitly not a physical boiling threshold, damage threshold, or OEM calibration. It is not used in any governing equation and does not clip or modify the temperature states.

A future specification revision should either:

1. freeze a formally justified model-domain boundary, or
2. remove the fixed threshold and base model-domain warnings on pressure-aware coolant thermodynamics.

## Deliberate non-features

The implementation does not add:

- pressure or boiling physics
- oil or heater-core nodes
- dynamic radiator thermal mass
- pump pressure networks
- A/C condenser coupling
- CFD
- production-vehicle calibration
- AI calculations
- FastAPI or React

## Verification status

The package includes automated tests for numerical conservation, solver convergence, component invariants, fault-direction behavior, and canonical regression behavior. Physical validation remains a separate future milestone.
