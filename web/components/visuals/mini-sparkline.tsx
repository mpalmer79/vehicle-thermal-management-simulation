export type SparkSeries = {
  id: string;
  tone: "engine" | "coolant" | "radiator";
  values: number[];
};

export type MiniSparklineProps = {
  series: SparkSeries[];
  width?: number;
  height?: number;
  /** Draws a soft area under the first series. */
  fill?: boolean;
  className?: string;
  title: string;
};

/**
 * Compact trend renderer for values that already exist in an authoritative result.
 * It never generates, smooths, or extrapolates data; it only scales what it is given.
 */
export function MiniSparkline({
  series,
  width = 300,
  height = 72,
  fill = true,
  className,
  title,
}: MiniSparklineProps) {
  const all = series.flatMap((item) => item.values).filter((value) => Number.isFinite(value));
  if (all.length === 0) return null;

  const min = Math.min(...all);
  const max = Math.max(...all);
  const span = max - min || 1;
  const pad = 6;

  const project = (values: number[]) =>
    values.map((value, index) => {
      const x = values.length === 1 ? 0 : (index / (values.length - 1)) * width;
      const y = height - pad - ((value - min) / span) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

  const [primary] = series;
  const primaryPoints = project(primary.values);

  return (
    <svg
      className={["spark", className].filter(Boolean).join(" ")}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={title}
    >
      {fill && (
        <polygon
          className={`spark-area ${primary.tone}`}
          points={`0,${height} ${primaryPoints.join(" ")} ${width},${height}`}
        />
      )}
      {series.map((item) => (
        <polyline className={`spark-line ${item.tone}`} key={item.id} points={project(item.values).join(" ")} />
      ))}
      {series.map((item) => {
        const points = project(item.values);
        const last = points.at(-1)?.split(",").map(Number) ?? [0, 0];
        return <circle className={`spark-dot ${item.tone}`} cx={last[0]} cy={last[1]} key={`dot-${item.id}`} r="3.4" />;
      })}
    </svg>
  );
}
