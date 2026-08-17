import { PROFILE_LINKS } from "@/lib/about-content";

function ProfileGlyph({ id }: { id: "linkedin" | "github" }) {
  if (id === "linkedin") {
    return (
      <svg viewBox="0 0 24 24" role="presentation" aria-hidden="true">
        <path
          d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9.5h4v11H3v-11Zm6.5 0h3.8v1.5h.05a4.2 4.2 0 0 1 3.75-2c4 0 4.75 2.5 4.75 5.8v5.7h-4v-5c0-1.2 0-2.8-1.75-2.8s-2 1.35-2 2.7v5.1h-4v-11Z"
          fill="currentColor"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" role="presentation" aria-hidden="true">
      <path
        d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02a9.5 9.5 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.35 4.68-4.58 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"
        fill="currentColor"
      />
    </svg>
  );
}

/**
 * Profile badges. Rendered near the top of /about and again at the closing CTA, so the
 * two destinations are always one tap away.
 */
export function CreatorLinks({ tone = "solid" }: { tone?: "solid" | "quiet" }) {
  return (
    <div className={`creator-links ${tone}`}>
      {PROFILE_LINKS.map((link) => (
        <a
          className={`creator-link ${link.id}`}
          href={link.href}
          key={link.id}
          rel="noreferrer noopener"
          target="_blank"
        >
          <span className="creator-link-glyph">
            <ProfileGlyph id={link.id} />
          </span>
          <span className="creator-link-text">
            <strong>{link.label}</strong>
            <small>{link.handle}</small>
          </span>
          <i aria-hidden="true">↗</i>
        </a>
      ))}
    </div>
  );
}
