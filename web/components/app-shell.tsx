"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const navigation = [
  ["Overview", "/"],
  ["Simulation Lab", "/simulate"],
  ["System Explorer", "/system"],
  ["Scenarios", "/scenarios"],
  ["Validation", "/validation"],
  ["Model", "/model"],
] as const;

const more = [
  ["Validation", "/validation"],
  ["Engineering Model", "/model"],
  ["Roadmap", "/roadmap"],
  ["GitHub repository", "https://github.com/mpalmer79/vehicle-thermal-management-simulation"],
] as const;

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/" aria-label="VTMS Overview">
          <span className="brand-mark">V</span>
          <span><strong>VTMS</strong><small>Vehicle Thermal Management</small></span>
        </Link>
        <nav className="side-nav" aria-label="Primary navigation">
          {navigation.map(([label, href]) => (
            <Link className={isActive(pathname, href) ? "nav-link active" : "nav-link"} href={href} key={href}>
              <span className="nav-dot" />{label}
            </Link>
          ))}
        </nav>
        <div className="sidebar-status">
          <span className="eyebrow">MODEL STATUS</span>
          <strong>VTMS-V1 / EM-V1</strong>
          <span className="status-line"><i className="status-dot verified" />Numerically verified</span>
          <span className="status-line"><i className="status-dot pending" />Controlled validation pending</span>
        </div>
      </aside>

      <div className="app-column">
        <header className="topbar">
          <div><span className="context-label">Physics-based simulation</span><span className="context-sep">/</span><span className="context-muted">Generic parameter set</span></div>
          <div className="topbar-actions"><Link href="/roadmap">Maturity roadmap</Link><a href="https://github.com/mpalmer79/vehicle-thermal-management-simulation">Repository ↗</a></div>
        </header>
        <main className="page-content">{children}</main>
      </div>

      <nav className="mobile-nav" aria-label="Mobile navigation">
        <Link className={pathname === "/" ? "active" : ""} href="/"><span className="mobile-nav-icon">⌂</span><span>Overview</span></Link>
        <Link className={pathname.startsWith("/simulate") ? "active" : ""} href="/simulate"><span className="mobile-nav-icon">▶</span><span>Simulate</span></Link>
        <Link className={pathname.startsWith("/system") ? "active" : ""} href="/system"><span className="mobile-nav-icon">◎</span><span>System</span></Link>
        <Link className={pathname.startsWith("/scenarios") ? "active" : ""} href="/scenarios"><span className="mobile-nav-icon">▦</span><span>Scenarios</span></Link>
        <button className={moreOpen ? "active" : ""} onClick={() => setMoreOpen((value) => !value)} type="button"><span className="mobile-nav-icon">•••</span><span>More</span></button>
      </nav>

      {moreOpen && (
        <div className="mobile-more" role="dialog" aria-label="More navigation">
          <button className="mobile-more-close" onClick={() => setMoreOpen(false)} type="button">Close</button>
          {more.map(([label, href]) => href.startsWith("http") ? <a href={href} key={href}>{label} ↗</a> : <Link href={href} key={href} onClick={() => setMoreOpen(false)}>{label}</Link>)}
        </div>
      )}
    </div>
  );
}
