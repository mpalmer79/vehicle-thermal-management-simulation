import type { TimeSeriesPoint } from "@/lib/vtms-types";

function makePath(points: TimeSeriesPoint[], field: "engine_structure_temp_c" | "coolant_temp_c", min: number, max: number) {
  return points.map((point, index) => {
    const x = points.length === 1 ? 0 : (index / (points.length - 1)) * 1000;
    const y = 260 - ((point[field] - min) / (max - min)) * 220;
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

export function SignalChart({ points, selectedIndex }: { points: TimeSeriesPoint[]; selectedIndex?: number }) {
  const values = points.flatMap((p) => [p.engine_structure_temp_c, p.coolant_temp_c]);
  const min = Math.floor(Math.min(...values) / 10) * 10 - 5;
  const max = Math.ceil(Math.max(...values) / 10) * 10 + 5;
  const cursorX = selectedIndex === undefined ? null : (selectedIndex / (points.length - 1)) * 1000;
  return (
    <div className="chart-shell">
      <svg viewBox="0 0 1000 300" role="img" aria-label="Engine and coolant temperature response">
        {[0, 1, 2, 3, 4].map((i) => <line className="chart-grid" key={i} x1="0" x2="1000" y1={40 + i * 55} y2={40 + i * 55} />)}
        <path className="chart-line engine" d={makePath(points, "engine_structure_temp_c", min, max)} />
        <path className="chart-line coolant" d={makePath(points, "coolant_temp_c", min, max)} />
        {cursorX !== null && <line className="chart-cursor" x1={cursorX} x2={cursorX} y1="24" y2="270" />}
      </svg>
      <div className="chart-legend"><span><i className="legend-line engine" />Engine structure</span><span><i className="legend-line coolant" />Coolant</span><span className="chart-range">{min} to {max} °C</span></div>
    </div>
  );
}
