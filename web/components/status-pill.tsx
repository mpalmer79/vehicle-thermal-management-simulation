export function StatusPill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "verified" | "pending" | "warning" }) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}
