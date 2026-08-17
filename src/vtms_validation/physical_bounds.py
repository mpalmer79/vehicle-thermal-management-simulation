from __future__ import annotations

from dataclasses import dataclass

from .calibration import CalibrationBounds, ParameterBound
from .manifest import ALLOWED_CALIBRATION_PARAMETERS


CAL_01_PARAMETER_NAMES = (
    "wall_heat_fraction",
    "engine_thermal_capacitance_j_per_k",
    "engine_coolant_ua_w_per_k",
)
CAL_RAD_01_PARAMETER_NAMES = ("radiator_ua_nominal_w_per_k",)


@dataclass(frozen=True)
class BoundRationale:
    name: str
    lower: float
    upper: float
    units: str
    basis: str
    source_basis: tuple[str, ...]
    caution: str


# These are VTMS engineering calibration bounds, not measurements of a specific
# Ford component. They are deliberately frozen before any Argonne model residual
# is inspected. The bounds are wider than the current generic values and are
# derived from physical interpretation, literature-supported thermal behavior,
# and the topology of the frozen VTMS-V1 lumped model.
_ARGONNE_RATIONALES = (
    BoundRationale(
        name="wall_heat_fraction",
        lower=0.20,
        upper=0.50,
        units="fraction of fuel lower-heating-value rate",
        basis=(
            "VTMS uses this parameter as the fraction of measured fuel-energy rate entering "
            "the lumped engine thermal state. Published SI-engine start-up studies report "
            "combustion-wall heat transfer on the order of 40 to 45 percent of burned fuel "
            "energy during start-up. The VTMS parameter is not identical to that measured "
            "quantity because the V1 state collapses multiple solids and omits oil/exhaust "
            "states, so a broader 0.20 to 0.50 engineering interval is used."
        ),
        source_basis=(
            "SAE 2009-01-0613",
            "SAE 2010-01-1270",
        ),
        caution="Do not interpret the fitted value as a directly measured cylinder-wall heat fraction.",
    ),
    BoundRationale(
        name="engine_thermal_capacitance_j_per_k",
        lower=25000.0,
        upper=100000.0,
        units="J/K",
        basis=(
            "This is an effective lumped thermal capacitance, not the total engine mass times "
            "one material heat capacity. Engine warm-up literature supports lumped-capacity "
            "representations of block/head structures and shows that effective heated mass is "
            "a key transient parameter. The interval brackets the current 50 kJ/K value by a "
            "factor of four and is intentionally broad enough to represent partial thermal "
            "participation of engine structure without allowing an effectively massless or "
            "thermally immovable engine state."
        ),
        source_basis=(
            "SAE 910302",
            "SAE 931153",
            "SAE 971852",
            "SAE 2016-01-0197",
        ),
        caution="Effective capacitance is topology-dependent and must not be reported as physical engine mass.",
    ),
    BoundRationale(
        name="engine_coolant_ua_w_per_k",
        lower=400.0,
        upper=2200.0,
        units="W/K",
        basis=(
            "VTMS collapses distributed metal-to-coolant convection and conduction into one UA. "
            "Engine thermal-management literature treats these paths with coolant-side heat "
            "transfer submodels or thermal resistances rather than one universal constant. "
            "The selected interval spans more than a fivefold conductance range around the "
            "generic 1000 W/K value so calibration can alter the engine/coolant coupling time "
            "scale materially while remaining finite and positive."
        ),
        source_basis=(
            "SAE 931157",
            "SAE 971852",
            "SAE 2011-01-0647",
        ),
        caution="This is an effective network conductance, not a local coolant heat-transfer coefficient.",
    ),
    BoundRationale(
        name="radiator_ua_nominal_w_per_k",
        lower=400.0,
        upper=2200.0,
        units="W/K",
        basis=(
            "The radiator is represented by an effectiveness-NTU heat exchanger, making UA the "
            "natural aggregate conductance parameter. Automotive radiator literature explicitly "
            "uses effectiveness/NTU methods and shows sensitivity to inlet-air distribution. "
            "The interval spans a broad range around the generic 1100 W/K value while remaining "
            "compatible with the finite coolant and air heat-capacity rates represented by V1."
        ),
        source_basis=(
            "SAE 940771",
            "SAE 2011-01-0647",
        ),
        caution="The fitted UA is specific to the V1 airflow and radiator topology and is not a bench-rated radiator constant.",
    ),
)


def argonne_physical_bound_rationales() -> tuple[BoundRationale, ...]:
    """Return the frozen pre-residual rationale set for controlled Argonne fitting."""

    return _ARGONNE_RATIONALES


def argonne_preregistered_bounds() -> CalibrationBounds:
    """Return the complete frozen Argonne bound set for the governed parameter universe.

    The four numerical intervals were selected before inspecting any VTMS-vs-Argonne
    residuals. The complete set is an audit record, not a declaration that all four
    parameters belong in the same optimizer stage.
    """

    rationales = argonne_physical_bound_rationales()
    names = tuple(item.name for item in rationales)
    if names != tuple(ALLOWED_CALIBRATION_PARAMETERS):
        raise RuntimeError("Argonne physical bounds must match the governed calibration universe")
    return CalibrationBounds(
        parameters=tuple(
            ParameterBound(item.name, item.lower, item.upper) for item in rationales
        )
    )


def _bounds_for(names: tuple[str, ...]) -> CalibrationBounds:
    by_name = {
        bound.name: bound for bound in argonne_preregistered_bounds().parameters
    }
    if len(names) != len(set(names)) or any(name not in by_name for name in names):
        raise RuntimeError("staged Argonne bounds reference an invalid parameter subset")
    return CalibrationBounds(parameters=tuple(by_name[name] for name in names))


def argonne_cal_01_bounds() -> CalibrationBounds:
    """Return frozen bounds for the cold-start warm-up calibration stage."""

    return _bounds_for(CAL_01_PARAMETER_NAMES)


def argonne_cal_rad_01_bounds() -> CalibrationBounds:
    """Return the frozen radiator-UA bound for the radiator-active calibration stage."""

    return _bounds_for(CAL_RAD_01_PARAMETER_NAMES)
