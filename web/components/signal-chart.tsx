import type { TimeSeriesPoint } from "@/lib/vtms-types";

type TemperatureField = "engine_structure_temp_c" | "coolant_temp_c" | "radiator_outlet_temp_c";

const plot = { left: 74, right: 975, top: 32, bottom: 286 };

function xFor(time: number, start: number, end: number) {
  if (end === start) return plot.left;
  return plot.left + ((time - start) / (end - start)) * (plot.right - plot.left);
}

function yFor(value: number, min: number, max: number) {
  if (max === min) return (plot.top + plot.bottom) / 2;
  return plot.bottom - ((value - min) / (max - min)) * (plot.bottom - plot.top);
}

function makePath(points: TimeSeriesPoint[], field: TemperatureField, min: number, max: number) {
  const start = points[0]?.time_s ?? 0;
  const end = points.at(-1)?.time_s ?? start;
  let drawing = false;
  return points.map((point) => {
    const value = point[field];
    if (value === null) {
      drawing = false;
      return "";
    }
    const command = drawing ? "L" : "M";
    drawing = true;
    return `${command}${xFor(point.time_s, start, end).toFixed(1)},${yFor(value, min, max).toFixed(1)}`;
  }).filter(Boolean).join(" ");
}

export function SignalChart({ points, selectedIndex }: { points: TimeSeriesPoint[]; selectedIndex?: number }) {
  const radiatorValues = points.flatMap((point) => point.radiator_outlet_temp_c === null ? [] : [point.radiator_outlet_temp_c]);
  const values = points.flatMap((point) => [point.engine_structure_temp_c, point.coolant_temp_c]).concat(radiatorValues);
  const min = Math.floor(Math.min(...values) / 10) * 10 - 5;
  const max = Math.ceil(Math.max(...values) / 10) * 10 + 5;
  const start = points[0]?.time_s ?? 0;
  const end = points.at(-1)?.time_s ?? start;
  const selected = selectedIndex === undefined ? null : points[selectedIndex];
  const cursorX = selected ? xFor(selected.time_s, start, end) : null;
  const yTicks = Array.from({ length: 5 }, (_, index) => max - ((max - min) / 4) * index);
  const xTicks = Array.from({ length: 5 }, (_, index) => start + ((end - start) / 4) * index);

  return (
    <div className="chart-shell">
      <div className="chart-title-row"><div><span className="eyebrow">KEY TEMPERATURES</span><strong>Transient thermal response</strong></div>{selected && <span className="fixture-badge">Selected: {selected.time_s.toFixed(0)} s</span>}</div>
      <svg viewBox="0 0 1000 360" role="img" aria-label="Engine, coolant, and radiator outlet temperature response over time">
        {yTicks.map((tick, index) => {
          const y = plot.top + index * ((plot.bottom - plot.top) / 4);
          return <g key={tick}><line className="chart-grid" x1={plot.left} x2={plot.right} y1={y} y2={y} /><text className="chart-tick" x={plot.left - 14} y={y + 6} textAnchor="end">{tick.toFixed(0)}</text></g>;
        })}
        {xTicks.map((tick) => {
          const x = xFor(tick, start, end);
          return <g key={tick}><line className="chart-grid" x1={x} x2={x} y1={plot.top} y2={plot.bottom} /><text className="chart-tick" x={x} y={plot.bottom + 28} textAnchor="middle">{tick.toFixed(0)}</text></g>;
        })}
        <line className="chart-axis" x1={plot.left} x2={plot.left} y1={plot.top} y2={plot.bottom} />
        <line className="chart-axis" x1={plot.left} x2={plot.right} y1={plot.bottom} y2={plot.bottom} />
        <text className="chart-axis-label" x="20" y={(plot.top + plot.bottom) / 2} textAnchor="middle" transform={`rotate(-90 20 ${(plot.top + plot.bottom) / 2})`}>Temperature (°C)</text>
        <text className="chart-axis-label" x={(plot.left + plot.right) / 2} y="348" textAnchor="middle">Time (s)</text>
        <path className="chart-line engine" d={makePath(points, "engine_structure_temp_c", min, max)} />
        <path className="chart-line coolant" d={makePath(points, "coolant_temp_c", min, max)} />
        <path className="chart-line radiator" d={makePath(points, "radiator_outlet_temp_c", min, max)} />
        {cursorX !== null && selected && <>
          <line className="chart-cursor" x1={cursorX} x2={cursorX} y1={plot.top} y2={plot.bottom} />
          <text className="chart-cursor-label" x={cursorX} y="22" textAnchor="middle">{selected.time_s.toFixed(0)} s</text>
          <circle className="chart-point engine" cx={cursorX} cy={yFor(selected.engine_structure_temp_c, min, max)} r="7" />
          <circle className="chart-point coolant" cx={cursorX} cy={yFor(selected.coolant_temp_c, min, max)} r="7" />
          {selected.radiator_outlet_temp_c !== null && <circle className="chart-point radiator" cx={cursorX} cy={yFor(selected.radiator_outlet_temp_c, min, max)} r="7" />}
        </>}
      </svg>
      <div className="chart-legend"><span><i className="legend-line engine" />Engine structure</span><span><i className="legend-line coolant" />Coolant</span><span><i className="legend-line radiator" />Radiator outlet</span><span className="chart-range">{min} to {max} °C</span></div>
    </div>
  );
}
