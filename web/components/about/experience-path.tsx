import { EXPERIENCE_PATH, type ExperienceStage } from "@/lib/about-content";

/** One distinct glyph per stage, so the progression does not read as four repeated cards. */
function StageGlyph({ id }: { id: ExperienceStage["id"] }) {
  return (
    <svg className={`stage-glyph ${id}`} viewBox="0 0 64 44" role="presentation" aria-hidden="true">
      {id === "automotive" && (
        <g>
          <path className="sg-body" d="M8,30 L13,19 Q15,15 20,15 L44,15 Q49,15 51,19 L56,30 Z" />
          <circle className="sg-wheel" cx="19" cy="32" r="5" />
          <circle className="sg-wheel" cx="45" cy="32" r="5" />
          <line className="sg-road" x1="4" x2="60" y1="39" y2="39" />
        </g>
      )}

      {id === "dealer-tech" && (
        <g>
          <rect className="sg-screen" x="10" y="9" width="44" height="26" rx="4" />
          {[16, 21, 26].map((y, index) => (
            <line className="sg-row" key={y} x1="16" x2={index === 2 ? 34 : 48} y1={y} y2={y} />
          ))}
          <circle className="sg-node" cx="44" cy="28" r="3.4" />
        </g>
      )}

      {id === "software-ai" && (
        <g>
          <path className="sg-bracket" d="M22,12 L12,22 L22,32" />
          <path className="sg-bracket" d="M42,12 L52,22 L42,32" />
          <circle className="sg-node" cx="32" cy="22" r="4" />
          <circle className="sg-orbit" cx="32" cy="22" r="9" />
        </g>
      )}

      {id === "vtms" && (
        <g>
          <rect className="sg-block" x="9" y="15" width="18" height="16" rx="4" />
          <rect className="sg-core" x="39" y="13" width="16" height="20" rx="4" />
          <path className="sg-pipe" d="M27,20 L39,20" />
          <path className="sg-pipe" d="M47,33 L47,38 L18,38 L18,31" />
          <circle className="sg-flow" r="2.6">
            <animateMotion dur="3.4s" path="M27,20 L39,20 L47,20 L47,38 L18,38 L18,31" repeatCount="indefinite" />
          </circle>
        </g>
      )}
    </svg>
  );
}

/**
 * The career progression as a connected visual path rather than four paragraphs.
 * Horizontal on desktop, a compact vertical stepper on mobile.
 */
export function ExperiencePath() {
  return (
    <ol className="experience-path">
      {EXPERIENCE_PATH.map((stage, index) => (
        <li className={`experience-stage ${stage.id}`} key={stage.id} style={{ transitionDelay: `${index * 70}ms` }}>
          <div className="experience-visual">
            <StageGlyph id={stage.id} />
            <span className="experience-metric">{stage.metric}</span>
          </div>
          <span className="eyebrow">{stage.eyebrow}</span>
          <h3>{stage.title}</h3>
          <p>{stage.detail}</p>
        </li>
      ))}
    </ol>
  );
}
