/**
 * Shape-only summary of the KIT comparison.
 *
 * The curves are schematic and deliberately unlabelled on the value axes: the actual
 * measured-versus-predicted evidence is the rendered chart next to this panel, and the
 * reported metrics are shown verbatim. This panel exists to state the shape of the
 * mismatch, not to restate the data.
 */
export function ValidationTakeaway({
  headline,
  children,
}: {
  headline: string;
  children: React.ReactNode;
}) {
  return (
    <div className="takeaway">
      <span className="eyebrow">TAKEAWAY</span>
      <p className="takeaway-headline">{headline}</p>

      <div className="takeaway-shape">
        <svg viewBox="0 0 240 92" role="img" aria-label="Schematic comparison: the predicted curve rises faster than the measured curve early in the run, and the two converge near the end.">
          <path className="tk-gap" d="M10,80 C40,26 66,14 110,12 L110,12 C66,20 40,44 10,80 Z" />
          <path className="tk-measured" d="M10,80 C48,74 78,44 118,28 S196,14 230,12" />
          <path className="tk-predicted" d="M10,80 C34,30 58,16 96,13 S196,10 230,11" />
        </svg>
        <div className="tk-key">
          <span><i className="measured" />Measured</span>
          <span><i className="predicted" />VTMS-V1</span>
        </div>
      </div>

      {children}
    </div>
  );
}
