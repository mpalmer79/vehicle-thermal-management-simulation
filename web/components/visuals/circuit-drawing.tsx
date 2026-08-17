import type { SchematicLayout, SchematicNodeId, SchematicShape } from "@/lib/schematic-geometry";

export type FlowWeights = Partial<Record<SchematicLayout["paths"][number]["driver"], number>>;

const rect = (shape: SchematicShape) => shape as Extract<SchematicShape, { kind: "rect" }>;
const circle = (shape: SchematicShape) => shape as Extract<SchematicShape, { kind: "circle" }>;
const diamond = (shape: SchematicShape) => shape as Extract<SchematicShape, { kind: "diamond" }>;

const shapeOf = (layout: SchematicLayout, id: SchematicNodeId) =>
  layout.nodes.find((node) => node.id === id)!.shape;

const diamondPoints = (cx: number, cy: number, half: number) =>
  `${cx},${cy - half} ${cx + half},${cy} ${cx},${cy + half} ${cx - half},${cy}`;

const bladePaths = (cx: number, cy: number, r: number) =>
  Array.from({ length: 5 }, (_, index) => {
    const angle = (index / 5) * Math.PI * 2;
    const inner = r * 0.28;
    const outer = r * 0.86;
    const spread = 0.55;
    return [
      `M${(cx + Math.cos(angle) * inner).toFixed(1)},${(cy + Math.sin(angle) * inner).toFixed(1)}`,
      `Q${(cx + Math.cos(angle + spread * 0.5) * outer * 0.86).toFixed(1)},${(cy + Math.sin(angle + spread * 0.5) * outer * 0.86).toFixed(1)}`,
      `${(cx + Math.cos(angle + spread) * outer).toFixed(1)},${(cy + Math.sin(angle + spread) * outer).toFixed(1)}`,
    ].join(" ");
  });

/**
 * Weight 0 to 1 maps to stroke width and dash speed so that relative flow magnitude is
 * visible without asserting an absolute scale. Weights are supplied by the caller from
 * authoritative result values; the anatomy view passes none and renders a nominal circuit.
 */
function flowStyle(weight: number | undefined): React.CSSProperties | undefined {
  if (weight === undefined) return undefined;
  const clamped = Math.max(0, Math.min(1, weight));
  if (clamped <= 0.001) return { opacity: 0.16, animationPlayState: "paused", strokeWidth: 2.5 };
  return {
    strokeWidth: 2.6 + clamped * 4.2,
    opacity: 0.45 + clamped * 0.55,
    animationDuration: `${(2.6 - clamped * 1.6).toFixed(2)}s`,
  };
}

/**
 * The VTMS-V1 circuit as an SVG drawing. Shared by the Overview anatomy hero and the
 * System Explorer schematic so the same diagram is learned once and reused.
 */
export function CircuitDrawing({
  layout,
  idPrefix,
  weights,
  selectedId,
  fanActive = true,
  className,
  ariaLabel,
}: {
  layout: SchematicLayout;
  idPrefix: string;
  weights?: FlowWeights;
  selectedId?: SchematicNodeId | null;
  fanActive?: boolean;
  className?: string;
  ariaLabel: string;
}) {
  const engine = rect(shapeOf(layout, "engine"));
  const coolant = rect(shapeOf(layout, "coolant"));
  const radiator = rect(shapeOf(layout, "radiator"));
  const thermostat = diamond(shapeOf(layout, "thermostat"));
  const fan = circle(shapeOf(layout, "fan"));
  const pump = circle(shapeOf(layout, "pump"));

  const finCount = Math.max(3, Math.round(engine.width / 46));
  const finWidth = engine.width * 0.13;
  const finGap = (engine.width - 32 - finCount * finWidth) / Math.max(finCount - 1, 1);
  const tubeCount = Math.max(5, Math.round(radiator.width / 17));

  const outline = (id: SchematicNodeId) => (selectedId === id ? " node-selected" : "");

  return (
    <svg
      className={["circuit-svg", className].filter(Boolean).join(" ")}
      viewBox={layout.viewBox}
      role="img"
      aria-label={ariaLabel}
    >
      <defs>
        <linearGradient id={`${idPrefix}-engine`} x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#fff1ea" />
          <stop offset="100%" stopColor="#ffe2d3" />
        </linearGradient>
        <linearGradient id={`${idPrefix}-coolant`} x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#e9fafb" />
          <stop offset="100%" stopColor="#d3f1f4" />
        </linearGradient>
        <linearGradient id={`${idPrefix}-radiator`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#e8f8f0" />
          <stop offset="100%" stopColor="#d2f0e2" />
        </linearGradient>
        <radialGradient id={`${idPrefix}-glow`}>
          <stop offset="0%" stopColor="#ef8a2f" stopOpacity="0.36" />
          <stop offset="100%" stopColor="#ef8a2f" stopOpacity="0" />
        </radialGradient>
        <pattern id={`${idPrefix}-grid`} width="26" height="26" patternUnits="userSpaceOnUse">
          <path d="M26,0 L0,0 L0,26" fill="none" stroke="#0d2438" strokeOpacity="0.055" strokeWidth="1" />
        </pattern>
      </defs>

      <rect className="circuit-grid" width={layout.width} height={layout.height} fill={`url(#${idPrefix}-grid)`} />

      <ellipse
        className="heat-glow"
        cx={engine.x + engine.width / 2}
        cy={engine.y + engine.height / 2}
        rx={engine.width * 0.95}
        ry={engine.height * 0.95}
        fill={`url(#${idPrefix}-glow)`}
      />

      {layout.airLanes.map((d, index) => (
        <path className="air-lane" d={d} key={`air-${index}`} style={{ animationDelay: `${index * -0.5}s` }} />
      ))}
      {layout.ambientLanes.map((d, index) => (
        <path className="air-lane exhaust" d={d} key={`amb-${index}`} style={{ animationDelay: `${index * -0.35}s` }} />
      ))}

      {layout.paths.map((item) => (
        <path className={`pipe pipe-${item.driver}`} d={item.d} key={`pipe-${item.id}`} />
      ))}
      {layout.paths.map((item, index) => (
        <path
          className={`flow flow-${item.driver}`}
          d={item.d}
          key={`flow-${item.id}`}
          style={{ animationDelay: `${index * -0.4}s`, ...flowStyle(weights?.[item.driver]) }}
        />
      ))}

      <g className="circuit-hardware">
        <rect
          className={`block engine-block${outline("engine")}`}
          x={engine.x}
          y={engine.y}
          width={engine.width}
          height={engine.height}
          rx={engine.radius}
          fill={`url(#${idPrefix}-engine)`}
        />
        {Array.from({ length: finCount }, (_, index) => (
          <rect
            className="engine-fin"
            key={index}
            x={engine.x + 16 + index * (finWidth + finGap)}
            y={engine.y + engine.height * 0.18}
            width={finWidth}
            height={engine.height * 0.64}
            rx={finWidth / 3}
          />
        ))}

        <rect
          className={`block coolant-block${outline("coolant")}`}
          x={coolant.x}
          y={coolant.y}
          width={coolant.width}
          height={coolant.height}
          rx={coolant.radius}
          fill={`url(#${idPrefix}-coolant)`}
        />
        {[0, 1, 2].map((index) => (
          <path
            className="coolant-wave"
            d={`M${coolant.x + coolant.width * 0.14},${coolant.y + coolant.height * (0.34 + index * 0.19)} q${(coolant.width * 0.18).toFixed(1)},-9 ${(coolant.width * 0.36).toFixed(1)},0 t${(coolant.width * 0.36).toFixed(1)},0`}
            key={index}
            style={{ animationDelay: `${index * -0.6}s` }}
          />
        ))}

        <polygon
          className={`block thermostat-block${outline("thermostat")}`}
          points={diamondPoints(thermostat.cx, thermostat.cy, thermostat.half)}
        />
        <path
          className="thermostat-gate"
          d={`M${thermostat.cx - thermostat.half * 0.42},${thermostat.cy} L${thermostat.cx + thermostat.half * 0.42},${thermostat.cy}`}
        />

        <rect
          className={`block radiator-block${outline("radiator")}`}
          x={radiator.x}
          y={radiator.y}
          width={radiator.width}
          height={radiator.height}
          rx={radiator.radius}
          fill={`url(#${idPrefix}-radiator)`}
        />
        {Array.from({ length: tubeCount }, (_, index) => {
          const x = radiator.x + 12 + index * ((radiator.width - 24) / (tubeCount - 1));
          return <line className="radiator-tube" key={index} x1={x} x2={x} y1={radiator.y + 10} y2={radiator.y + radiator.height - 10} />;
        })}

        <g className={`fan-group${outline("fan")}${fanActive ? "" : " idle"}`}>
          <circle className="fan-shroud" cx={fan.cx} cy={fan.cy} r={fan.r} />
          <g className="fan-blades" style={{ transformOrigin: `${fan.cx}px ${fan.cy}px` }}>
            {bladePaths(fan.cx, fan.cy, fan.r).map((d, index) => (
              <path className="fan-blade" d={d} key={index} />
            ))}
          </g>
          <circle className="fan-hub" cx={fan.cx} cy={fan.cy} r={Math.max(4, fan.r * 0.16)} />
        </g>

        <g className={`pump-group${outline("pump")}`}>
          <circle className="pump-body" cx={pump.cx} cy={pump.cy} r={pump.r} />
          <g className="pump-impeller" style={{ transformOrigin: `${pump.cx}px ${pump.cy}px` }}>
            {[0, 1, 2].map((index) => (
              <line
                key={index}
                x1={pump.cx}
                y1={pump.cy}
                x2={pump.cx + Math.cos((index / 3) * Math.PI * 2) * (pump.r - 7)}
                y2={pump.cy + Math.sin((index / 3) * Math.PI * 2) * (pump.r - 7)}
              />
            ))}
          </g>
        </g>
      </g>
    </svg>
  );
}
