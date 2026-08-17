import { type BuildCategory, WHAT_I_BUILD } from "@/lib/about-content";

function BuildGlyph({ id }: { id: BuildCategory["id"] }) {
  return (
    <svg className={`build-glyph ${id}`} viewBox="0 0 72 48" role="presentation" aria-hidden="true">
      {id === "automotive-technology" && (
        <g>
          <path className="bg-car" d="M12,30 L17,20 Q19,16 24,16 L46,16 Q51,16 53,20 L58,30 Z" />
          <circle className="bg-wheel" cx="23" cy="32" r="4.6" />
          <circle className="bg-wheel" cx="47" cy="32" r="4.6" />
          <path className="bg-signal" d="M36,12 q0,-6 8,-6" />
          <circle className="bg-dot" cx="45" cy="6" r="2.6" />
        </g>
      )}

      {id === "software-ai" && (
        <g>
          <rect className="bg-panel" x="10" y="9" width="52" height="30" rx="5" />
          <path className="bg-code" d="M23,18 L18,24 L23,30" />
          <path className="bg-code" d="M40,18 L45,24 L40,30" />
          <line className="bg-slash" x1="34" x2="29" y1="17" y2="31" />
        </g>
      )}

      {id === "engineering-simulation" && (
        <g>
          <line className="bg-axis" x1="12" x2="12" y1="8" y2="38" />
          <line className="bg-axis" x1="12" x2="62" y1="38" y2="38" />
          <path className="bg-curve" d="M12,36 C24,34 30,18 42,14 S58,11 62,10" />
          {[20, 32, 44, 56].map((x, index) => (
            <circle className="bg-sample" cx={x} cy={[31, 20, 13, 11][index]} key={x} r="2.4" />
          ))}
        </g>
      )}
    </svg>
  );
}

/** "What I Build" — three illustrated blocks, kept deliberately short. */
export function BuildBlocks() {
  return (
    <div className="build-blocks">
      {WHAT_I_BUILD.map((category, index) => (
        <article className={`build-block ${category.id}`} key={category.id} style={{ transitionDelay: `${index * 70}ms` }}>
          <BuildGlyph id={category.id} />
          <h3>{category.title}</h3>
          <p>{category.copy}</p>
          <ul>
            {category.points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </article>
      ))}
    </div>
  );
}
