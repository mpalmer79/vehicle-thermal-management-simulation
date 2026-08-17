export type GaugeMark = { label: string; valueC: number };

/**
 * Compact temperature readout.
 *
 * The scale domain is supplied by the caller from the authoritative result range, and
 * marks are limited to control thresholds that already exist in the engineering model.
 * No damage, boiling, or failure limit is implied.
 */
export function TemperatureGauge({
  label,
  valueC,
  minC,
  maxC,
  tone = "engine",
  marks = [],
  peakC,
}: {
  label: string;
  valueC: number;
  minC: number;
  maxC: number;
  tone?: "engine" | "coolant" | "radiator";
  marks?: GaugeMark[];
  peakC?: number;
}) {
  const span = maxC - minC || 1;
  const clampPct = (value: number) => Math.max(0, Math.min(100, ((value - minC) / span) * 100));
  const markSummary = marks.map((mark) => `${mark.label} ${mark.valueC.toFixed(0)}`).join(" · ");

  return (
    <div className={`gauge ${tone}`}>
      <div className="gauge-head">
        <span className="gauge-label">{label}</span>
        <strong>{valueC.toFixed(1)}<em>°C</em></strong>
      </div>

      <div
        aria-label={`${label} ${valueC.toFixed(1)} degrees Celsius on a scale from ${minC.toFixed(0)} to ${maxC.toFixed(0)} degrees Celsius`}
        className="gauge-track"
        role="img"
      >
        <div className="gauge-fill" style={{ width: `${clampPct(valueC)}%` }} />
        {marks.map((mark) => (
          <span className="gauge-mark" key={mark.label} style={{ left: `${clampPct(mark.valueC)}%` }} />
        ))}
        {peakC !== undefined && peakC > valueC && (
          <span className="gauge-peak" style={{ left: `${clampPct(peakC)}%` }} />
        )}
      </div>

      <div className="gauge-scale">
        <span>{minC.toFixed(0)}</span>
        {peakC !== undefined && <span className="gauge-peak-value">peak {peakC.toFixed(1)} °C</span>}
        <span>{maxC.toFixed(0)}</span>
      </div>

      {markSummary && <p className="gauge-marks-note">control points: {markSummary} °C</p>}
    </div>
  );
}
