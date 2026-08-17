from vtms_v1.config import ModelParameters
from vtms_validation.manifest import ALLOWED_CALIBRATION_PARAMETERS
from vtms_validation.physical_bounds import (
    CAL_01_PARAMETER_NAMES,
    CAL_RAD_01_PARAMETER_NAMES,
    argonne_cal_01_bounds,
    argonne_cal_rad_01_bounds,
    argonne_physical_bound_rationales,
    argonne_preregistered_bounds,
)


def test_argonne_physical_bounds_match_governed_universe_and_contain_baseline():
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


def test_staged_bound_sets_are_exact_nonoverlapping_partitions_of_governed_universe():
    cal_01 = argonne_cal_01_bounds()
    cal_rad = argonne_cal_rad_01_bounds()

    assert tuple(item.name for item in cal_01.parameters) == CAL_01_PARAMETER_NAMES
    assert tuple(item.name for item in cal_rad.parameters) == CAL_RAD_01_PARAMETER_NAMES
    assert set(CAL_01_PARAMETER_NAMES).isdisjoint(CAL_RAD_01_PARAMETER_NAMES)
    assert set(CAL_01_PARAMETER_NAMES + CAL_RAD_01_PARAMETER_NAMES) == set(
        ALLOWED_CALIBRATION_PARAMETERS
    )
