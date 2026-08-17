export type PathGlyphKind = "configure" | "observe" | "evidence";

/**
 * Purpose-built step glyphs for the Overview product path. Each glyph describes a
 * different action, so the three steps do not read as one repeated icon card.
 */
export function PathGlyph({ kind }: { kind: PathGlyphKind }) {
  return (
    <svg className={`path-glyph ${kind}`} viewBox="0 0 120 76" role="presentation" aria-hidden="true">
      {kind === "configure" && (
        <g>
          {[18, 38, 58].map((y, index) => (
            <g key={y}>
              <line className="pg-track" x1="14" x2="106" y1={y} y2={y} />
              <line className="pg-fill" x1="14" x2={44 + index * 22} y1={y} y2={y} />
              <circle className="pg-knob" cx={44 + index * 22} cy={y} r="6" style={{ animationDelay: `${index * -0.9}s` }} />
            </g>
          ))}
        </g>
      )}

      {kind === "observe" && (
        <g>
          <rect className="pg-block" x="12" y="20" width="30" height="26" rx="7" />
          <rect className="pg-exchanger" x="80" y="18" width="28" height="30" rx="7" />
          <path className="pg-loop" d="M42,33 L80,33" />
          <path className="pg-loop" d="M94,48 L94,62 L26,62 L26,46" />
          <circle className="pg-travel" r="4">
            <animateMotion dur="3.6s" path="M42,33 L80,33 L94,33 L94,62 L26,62 L26,46" repeatCount="indefinite" />
          </circle>
        </g>
      )}

      {kind === "evidence" && (
        <g>
          <line className="pg-axis" x1="14" x2="14" y1="10" y2="62" />
          <line className="pg-axis" x1="14" x2="108" y1="62" y2="62" />
          <path className="pg-measured" d="M14,58 C40,52 52,34 70,26 S96,18 106,17" />
          <path className="pg-predicted" d="M14,58 C30,30 44,20 62,18 S96,16 106,16" />
          {[0, 1, 2, 3].map((index) => (
            <rect className={`pg-step ${index < 2 ? "done" : ""}`} key={index} x={22 + index * 22} y="66" width="14" height="5" rx="2.5" />
          ))}
        </g>
      )}
    </svg>
  );
}
