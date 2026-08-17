/**
 * Hero visual for /about.
 *
 * There is no portrait asset in this repository and none is invented. The identity mark
 * is a purpose-built composition instead: an MP monogram plated inside the same thermal
 * circuit language used across the product — a coolant loop, a radiator core, an engine
 * mass, and a code bracket standing in for the software side.
 */
export function CreatorMonogram() {
  return (
    <svg
      className="creator-monogram"
      viewBox="0 0 320 260"
      role="img"
      aria-label="Monogram composition: the initials MP inside a stylized coolant loop with a radiator core, engine mass, and code brackets"
    >
      <defs>
        <linearGradient id="mono-plate" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#e4f7f4" />
          <stop offset="55%" stopColor="#fffdfa" />
          <stop offset="100%" stopColor="#fdeede" />
        </linearGradient>
        <linearGradient id="mono-ink" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#0c7f8d" />
          <stop offset="100%" stopColor="#12333f" />
        </linearGradient>
      </defs>

      {/* Measurement field: engineering paper, not decoration. */}
      <g className="cm-grid" aria-hidden="true">
        {[40, 80, 120, 160, 200].map((y) => (
          <line key={y} x1="16" x2="304" y1={y} y2={y} />
        ))}
        {[60, 120, 180, 240].map((x) => (
          <line key={x} x1={x} x2={x} y1="24" y2="228" />
        ))}
      </g>

      {/* Coolant loop travelling around the mark. */}
      <path
        className="cm-loop"
        d="M62,196 L62,132 Q62,104 90,104 L230,104 Q258,104 258,132 L258,196"
      />
      <path className="cm-loop-flow" d="M62,196 L62,132 Q62,104 90,104 L230,104 Q258,104 258,132 L258,196" />

      {/* Engine mass on the left, radiator core on the right. */}
      <g className="cm-engine">
        <rect x="34" y="188" width="56" height="42" rx="10" />
        {[46, 58, 70].map((x) => (
          <line key={x} x1={x} x2={x} y1="196" y2="222" />
        ))}
      </g>
      <g className="cm-radiator">
        <rect x="230" y="188" width="56" height="42" rx="10" />
        {[196, 204, 212, 220].map((y) => (
          <line key={y} x1="236" x2="280" y1={y} y2={y} />
        ))}
      </g>

      {/* Monogram plate. */}
      <rect className="cm-plate" x="94" y="42" width="132" height="118" rx="26" />
      <text className="cm-initials" x="160" y="122" textAnchor="middle">
        MP
      </text>

      {/* Code brackets: the software half of the composition. */}
      <path className="cm-bracket" d="M78,66 L60,84 L78,102" />
      <path className="cm-bracket" d="M242,66 L260,84 L242,102" />

      {/* Heat rising from the engine mass. */}
      <g className="cm-heat" aria-hidden="true">
        {[48, 62, 76].map((x, index) => (
          <path key={x} d={`M${x},184 q4,-9 0,-18`} style={{ animationDelay: `${index * -1.1}s` }} />
        ))}
      </g>
    </svg>
  );
}
