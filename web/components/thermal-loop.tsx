import type { TimeSeriesPoint } from "@/lib/vtms-types";
import { c, flow, kw, pct } from "@/lib/format";

export function ThermalLoop({ point, compact = false }: { point: TimeSeriesPoint; compact?: boolean }) {
  return (
    <div className={compact ? "thermal-loop compact" : "thermal-loop"}>
      <div className="thermal-node engine-node">
        <span>ENGINE STRUCTURE</span><strong>{c(point.engine_structure_temp_c)}</strong><small>{kw(point.engine_heat_w)} generated</small>
      </div>
      <div className="flow-arrow vertical"><span>{kw(point.engine_to_coolant_w)}</span></div>
      <div className="thermal-node coolant-node">
        <span>ENGINE-SIDE COOLANT</span><strong>{c(point.coolant_temp_c)}</strong><small>{flow(point.pump_flow_kg_s)} pump flow</small>
      </div>
      <div className="branch-row">
        <div className="thermal-node control-node"><span>THERMOSTAT</span><strong>{pct(point.thermostat_fraction)}</strong><small>{flow(point.radiator_flow_kg_s)} to radiator</small></div>
        <div className="thermal-node bypass-node"><span>BYPASS</span><strong>{pct(1 - point.thermostat_fraction)}</strong><small>{flow(point.bypass_flow_kg_s)}</small></div>
      </div>
      <div className="flow-arrow vertical"><span>coolant circuit</span></div>
      <div className="radiator-row">
        <div className="thermal-node radiator-node"><span>RADIATOR</span><strong>{kw(point.radiator_heat_w)}</strong><small>ε {point.radiator_effectiveness.toFixed(2)} · NTU {point.radiator_ntu.toFixed(2)}</small></div>
        <div className="air-arrow">AIR →<small>{flow(point.air_flow_kg_s)} · fan {pct(point.fan_fraction)}</small></div>
      </div>
    </div>
  );
}
