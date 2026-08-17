"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Restrained section entrance. Content is always rendered; only opacity and a small
 * translation are animated. Reduced-motion visitors are handled in CSS, where `.reveal`
 * resolves to its final state with no transition.
 */
export function MotionReveal({
  children,
  as: Tag = "section",
  className,
  delayMs = 0,
  ...rest
}: {
  children: React.ReactNode;
  as?: "section" | "div" | "article" | "header";
  className?: string;
  delayMs?: number;
} & React.HTMLAttributes<HTMLElement>) {
  const ref = useRef<HTMLElement | null>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    if (typeof IntersectionObserver === "undefined") {
      const timer = window.setTimeout(() => setRevealed(true), 0);
      return () => window.clearTimeout(timer);
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setRevealed(true);
            observer.disconnect();
          }
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.04 },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const classes = ["reveal", revealed ? "revealed" : "", className].filter(Boolean).join(" ");

  return (
    <Tag
      className={classes}
      ref={ref as React.Ref<never>}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
      {...rest}
    >
      {children}
    </Tag>
  );
}
