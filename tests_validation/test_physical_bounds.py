from vtms_v1.config import ModelParameters
from vtms_validation.manifest import ALLOWED_CALIBRATION_PARAMETERS
from vtms_validation.physical_bounds import (
    argonne_physical_bound_rationales,
    argonne_preregistered_bounds,
)


def test_argonne_physical_bounds_match_preregistered_subset_and_contain_baseline():
    bounds = argonne_preregistered_bounds()
    baseline = ModelParameters()

    assert tuple(item.name for item in bounds.parameters) == tuple(ALLOWED_CALIBRATION_PARAMETERS)
    for item in bounds.parameters:
        value = float(getattr(baseline, item.name))
        assert item.lower < value < item.upper


def test_argonne_bounds_are_not_the_synthetic_fixture_bounds():
    bounds = argonne_preregistered_bounds()
    observed = {item.name: (item.lower, item.upper) for item in bounds.parameters}

    assert observed["wall_heat_fraction"] == (0.20, 0.50)
    assert observed["engine_thermal_capacitance_j_per_k"] == (25000.0, 100000.0)
    assert observed["engine_coolant_ua_w_per_k"] == (400.0, 2200.0)
    assert observed["radiator_ua_nominal_w_per_k"] == (400.0, 2200.0)


def test_every_physical_bound_has_source_basis_and_caution():
    for rationale in argonne_physical_bound_rationales():
        assert rationale.source_basis
        assert rationale.basis.strip()
        assert rationale.caution.strip()
