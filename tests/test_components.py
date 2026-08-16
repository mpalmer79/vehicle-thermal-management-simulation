import math

from vtms_v1.airflow import AirflowModel
from vtms_v1.config import ModelParameters
from vtms_v1.engine import ReferenceEngineModel
from vtms_v1.fan import FanController
from vtms_v1.pump import PumpModel
from vtms_v1.radiator import RadiatorModel
from vtms_v1.thermostat import ThermostatModel
from vtms_v1.types import ThermostatMode


def test_reference_parameter_derivations():
    p = ModelParameters()
    assert math.isclose(p.coolant_mass_kg, 6.63, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(p.coolant_thermal_capacitance_j_per_k, 24464.7, rel_tol=0, abs_tol=1e-9)


def test_engine_off_returns_zero_heat():
    engine = ReferenceEngineModel(ModelParameters())
    assert engine.engine_heat_w(0.0, 0.5) == 0.0


def test_engine_torque_curve_no_extrapolation():
    engine = ReferenceEngineModel(ModelParameters())
    assert math.isclose(engine.torque_shape(2500.0), 1.0)
    try:
        engine.torque_shape(6600.0)
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported RPM extrapolation must fail")


def test_pump_equation_and_health():
    pump = PumpModel(ModelParameters())
    assert pump.mass_flow_kg_s(0.0) == 0.0
    assert math.isclose(pump.mass_flow_kg_s(800.0), 0.18)
    assert math.isclose(pump.mass_flow_kg_s(800.0, 0.5), 0.09)


def test_thermostat_modes():
    p = ModelParameters()
    t = ThermostatModel(p)
    assert t.opening(p.thermostat_open_c - 0.1) == 0.0
    assert t.opening(p.thermostat_full_c) == 1.0
    assert t.opening(150.0, ThermostatMode.STUCK_CLOSED) == 0.0
    assert t.opening(20.0, ThermostatMode.STUCK_OPEN) == 1.0
    middle = t.opening((p.thermostat_open_c + p.thermostat_full_c) / 2.0)
    assert math.isclose(middle, 0.5)


def test_fan_failure_and_bounds():
    p = ModelParameters()
    fan = FanController(p)
    assert fan.command(150.0, failed=True) == 0.0
    assert fan.command(p.fan_start_c - 1.0) == 0.0
    assert fan.command(p.fan_full_c) == 1.0


def test_airflow_zero_without_speed_or_fan():
    air = AirflowModel(ModelParameters())
    assert air.mass_flow_kg_s(0.0, 20.0, 0.0) == 0.0
    assert air.mass_flow_kg_s(20.0, 20.0, 0.0) > 0.0


def test_radiator_invariants():
    r = RadiatorModel(ModelParameters())
    zero = r.evaluate(100.0, 20.0, 0.0, 1.0)
    assert zero.heat_w == 0.0
    assert zero.outlet_temp_c is None
    assert zero.effectiveness == 0.0

    equal = r.evaluate(90.0, 90.0, 0.5, 1.0)
    assert abs(equal.heat_w) < 1e-12

    hot = r.evaluate(100.0, 20.0, 0.5, 1.0)
    assert 0.0 <= hot.effectiveness <= 1.0
    assert hot.heat_w > 0.0
    assert hot.outlet_temp_c is not None
    assert hot.outlet_temp_c < 100.0

    reversed_delta = r.evaluate(20.0, 40.0, 0.5, 1.0)
    assert reversed_delta.heat_w < 0.0
