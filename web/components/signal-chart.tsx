import { defaultControlThresholds, type ControlThresholds } from "@/lib/model-thresholds";
import type { TimeSeriesPoint } from "@/lib/vtms-types";

type TemperatureField = "engine_structure_temp_c" | "coolant_temp_c" | "radiator_outlet_temp_c";

type PlotBox = {
  viewW: number;
  viewH: number;
  left: number;
  right: number;
  top: number;
  bottom: number;
  axisY: number;
};

/* Two plot geometries. A single wide viewBox letterboxes badly on a phone, so the
   narrow variant is a genuinely taller plot rather than a scaled-down copy. */
const wideBox: PlotBox = { viewW: 1000, viewH: 360, left: 82, right: 962, top: 30, bottom: 288, axisY: 348 };
const narrowBox: PlotBox = { viewW: 560, viewH: 440, left: 66, right: 544, top: 30, bottom: 366, axisY: 426 };

function xFor(box: PlotBox, time: number, start: number, end: number) {
  if (end === start) return box.left;
  return box.left + ((time - start) / (end - start)) * (box.right - box.left);
}

function yFor(box: PlotBox, value: number, min: number, max: number) {
  if (max === min) return (box.top + box.bottom) / 2;
  return box.bottom - ((value - min) / (max - min)) * (box.bottom - box.top);
}

function makePath(box: PlotBox, points: TimeSeriesPoint[], field: TemperatureField, min: number, max: number) {
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
    return `${command}${xFor(box, point.time_s, start, end).toFixed(1)},${yFor(box, value, min, max).toFixed(1)}`;
  }).filter(Boolean).join(" ");
}

type PlotProps = {
  box: PlotBox;
  points: TimeSeriesPoint[];
  selected: TimeSeriesPoint | null;
  min: number;
  max: number;
  bands: Array<{ id: string; label: string; from: number; to: number }>;
  variant: "wide" | "narrow";
};

function Plot({ box, points, selected, min, max, bands, variant }: PlotProps) {
  const start = points[0]?.time_s ?? 0;
  const end = points.at(-1)?.time_s ?? start;
  const tickCount = variant === "wide" ? 5 : 4;
  const yTicks = Array.from({ length: tickCount }, (_, index) => max - ((max - min) / (tickCount - 1)) * index);
  const xTicks = Array.from({ length: tickCount }, (_, index) => start + ((end - start) / (tickCount - 1)) * index);
  const cursorX = selected ? xFor(box, selected.time_s, start, end) : null;
  const areaPath = `${makePath(box, points, "coolant_temp_c", min, max)} L${box.right},${box.bottom} L${box.left},${box.bottom} Z`;

  return (
    <svg
      className={`chart-plot chart-${variant}`}
      viewBox={`0 0 ${box.viewW} ${box.viewH}`}
      role="img"
      aria-label="Engine, coolant, and radiator outlet temperature response over time"
    >
      {bands.map((band) => {
        const top = yFor(box, Math.min(band.to, max), min, max);
        const height = yFor(box, Math.max(band.from, min), min, max) - top;
        return (
          <g key={band.id}>
            <rect className={`chart-band band-${band.id}`} x={box.left} y={top} width={box.right - box.left} height={Math.max(height, 0)} />
            <text className="chart-band-label" x={box.right - 8} y={top - 6} textAnchor="end">{band.label}</text>
          </g>
        );
      })}

      {yTicks.map((tick, index) => {
        const y = box.top + index * ((box.bottom - box.top) / (tickCount - 1));
        return (
          <g key={tick}>
            <line className="chart-grid" x1={box.left} x2={box.right} y1={y} y2={y} />
            <text className="chart-tick" x={box.left - 12} y={y + 6} textAnchor="end">{tick.toFixed(0)}</text>
          </g>
        );
      })}
      {xTicks.map((tick) => {
        const x = xFor(box, tick, start, end);
        return (
          <g key={tick}>
            <line className="chart-grid" x1={x} x2={x} y1={box.top} y2={box.bottom} />
            <text className="chart-tick" x={x} y={box.bottom + 28} textAnchor="middle">{tick.toFixed(0)}</text>
          </g>
        );
      })}

      <line className="chart-axis" x1={box.left} x2={box.left} y1={box.top} y2={box.bottom} />
      <line className="chart-axis" x1={box.left} x2={box.right} y1={box.bottom} y2={box.bottom} />
      <text
        className="chart-axis-label"
        x="20"
        y={(box.top + box.bottom) / 2}
        textAnchor="middle"
        transform={`rotate(-90 20 ${(box.top + box.bottom) / 2})`}
      >
        Temperature (°C)
      </text>
      <text className="chart-axis-label" x={(box.left + box.right) / 2} y={box.axisY} textAnchor="middle">Time (s)</text>

      <path className="chart-area coolant" d={areaPath} />
      <path className="chart-line radiator" d={makePath(box, points, "radiator_outlet_temp_c", min, max)} />
      <path className="chart-line coolant" d={makePath(box, points, "coolant_temp_c", min, max)} />
      <path className="chart-line engine" d={makePath(box, points, "engine_structure_temp_c", min, max)} />

      {cursorX !== null && selected && (
        <>
          <line className="chart-cursor" x1={cursorX} x2={cursorX} y1={box.top} y2={box.bottom} />
          <text className="chart-cursor-label" x={cursorX} y={box.top - 10} textAnchor="middle">{selected.time_s.toFixed(0)} s</text>
          <circle className="chart-point engine" cx={cursorX} cy={yFor(box, selected.engine_structure_temp_c, min, max)} r="8" />
          <circle className="chart-point coolant" cx={cursorX} cy={yFor(box, selected.coolant_temp_c, min, max)} r="8" />
          {selected.radiator_outlet_temp_c !== null && (
            <circle className="chart-point radiator" cx={cursorX} cy={yFor(box, selected.radiator_outlet_temp_c, min, max)} r="8" />
          )}
        </>
      )}
    </svg>
  );
}

export function SignalChart({
  points,
  selectedIndex,
  thresholds = defaultControlThresholds,
  title = "Transient thermal response",
}: {
  points: TimeSeriesPoint[];
  selectedIndex?: number;
  thresholds?: ControlThresholds;
  title?: string;
}) {
  const radiatorValues = points.flatMap((point) => point.radiator_outlet_temp_c === null ? [] : [point.radiator_outlet_temp_c]);
  const values = points.flatMap((point) => [point.engine_structure_temp_c, point.coolant_temp_c]).concat(radiatorValues);
  const min = Math.floor(Math.min(...values) / 10) * 10 - 5;
  const max = Math.ceil(Math.max(...values) / 10) * 10 + 5;
  const selected = selectedIndex === undefined ? null : points[selectedIndex];

  /* Control bands come from the frozen parameter set. They mark control transitions,
     not damage or failure limits, and are drawn only where they fall inside the data range. */
  const bands = [
    { id: "thermostat", label: "thermostat opening", from: thresholds.thermostatOpenC, to: thresholds.thermostatFullC },
    { id: "fan", label: "fan ramp", from: thresholds.fanStartC, to: thresholds.fanFullC },
  ].filter((band) => band.to > min && band.from < max);

  const shared = { points, selected, min, max, bands };

  return (
    <div className="chart-shell">
      <div className="chart-title-row">
        <div>
          <span className="eyebrow">KEY TEMPERATURES</span>
          <strong>{title}</strong>
        </div>
        {selected && <span className="fixture-badge">Selected: {selected.time_s.toFixed(0)} s</span>}
      </div>

      <div className="wide-only"><Plot box={wideBox} variant="wide" {...shared} /></div>
      <div className="narrow-only"><Plot box={narrowBox} variant="narrow" {...shared} /></div>

      <div className="chart-legend">
        <span><i className="legend-line engine" />Engine structure</span>
        <span><i className="legend-line coolant" />Coolant</span>
        <span><i className="legend-line radiator" />Radiator outlet</span>
        <span className="chart-range">{min} to {max} °C</span>
      </div>
    </div>
  );
}
