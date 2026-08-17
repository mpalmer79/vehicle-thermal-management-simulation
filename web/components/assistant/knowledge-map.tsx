/**
 * Visual map of what the assistant knows.
 *
 * Replaces the two prose panels that previously sat beside the /assistant conversation.
 * The chain reads MODEL → THERMAL SYSTEM → SCENARIOS → EVIDENCE → ARCHITECTURE, which
 * is also the order the knowledge base is organized in, so the picture doubles as a
 * table of contents rather than another stack of cards.
 */

const LAYERS = [
  { id: "model", label: "MODEL", detail: "VTMS-V1 · EM-V1 · two transient states" },
  { id: "system", label: "THERMAL SYSTEM", detail: "Radiator, thermostat, bypass, pump, fan, air side" },
  { id: "scenarios", label: "SCENARIOS", detail: "S-01 to S-09 baselines, faults, degradations" },
  { id: "evidence", label: "EVIDENCE", detail: "Verification, KIT plausibility, controlled status" },
  { id: "architecture", label: "ARCHITECTURE", detail: "Next.js, FastAPI, Python engine, deployment" },
] as const;

function LayerGlyph({ id }: { id: (typeof LAYERS)[number]["id"] }) {
  return (
    <svg className={`km-glyph ${id}`} viewBox="0 0 28 28" role="presentation" aria-hidden="true">
      {id === "model" && (
        <g>
          <rect className="km-stroke" x="4" y="6" width="20" height="16" rx="3" />
          <line className="km-bar" x1="8" x2="20" y1="12" y2="12" />
          <line className="km-bar" x1="8" x2="15" y1="16" y2="16" />
        </g>
      )}
      {id === "system" && (
        <g>
          <rect className="km-stroke" x="3" y="10" width="8" height="8" rx="2" />
          <rect className="km-stroke" x="17" y="9" width="8" height="10" rx="2" />
          <path className="km-flow" d="M11,14 L17,14" />
          <path className="km-flow" d="M21,19 L21,23 L7,23 L7,18" />
        </g>
      )}
      {id === "scenarios" && (
        <g>
          <rect className="km-stroke" x="4" y="5" width="8" height="7" rx="2" />
          <rect className="km-stroke" x="16" y="5" width="8" height="7" rx="2" />
          <rect className="km-stroke" x="4" y="16" width="8" height="7" rx="2" />
          <rect className="km-fault" x="16" y="16" width="8" height="7" rx="2" />
        </g>
      )}
      {id === "evidence" && (
        <g>
          <line className="km-axis" x1="5" x2="5" y1="4" y2="23" />
          <line className="km-axis" x1="5" x2="24" y1="23" y2="23" />
          <path className="km-curve" d="M5,20 C11,18 14,10 18,7.5 S23,6 24,5.8" />
          <circle className="km-dot" cx="12" cy="14" r="2" />
        </g>
      )}
      {id === "architecture" && (
        <g>
          <rect className="km-stroke" x="4" y="4" width="20" height="6" rx="2" />
          <rect className="km-stroke" x="4" y="18" width="20" height="6" rx="2" />
          <path className="km-flow" d="M14,10 L14,18" />
        </g>
      )}
    </svg>
  );
}

export function KnowledgeMap() {
  return (
    <div className="knowledge-map">
      <span className="eyebrow">WHAT IT KNOWS</span>
      <ol>
        {LAYERS.map((layer) => (
          <li className={`km-layer ${layer.id}`} key={layer.id}>
            <span className="km-mark">
              <LayerGlyph id={layer.id} />
            </span>
            <span className="km-text">
              <strong>{layer.label}</strong>
              <small>{layer.detail}</small>
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
