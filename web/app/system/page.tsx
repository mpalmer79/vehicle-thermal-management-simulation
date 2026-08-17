import type { Metadata } from "next";

import { PlaybackWorkspace } from "@/components/playback-workspace";

export const metadata: Metadata = { title: "System Explorer" };

export default function SystemPage() {
  return (
    <>
      <header className="page-header split lean">
        <div>
          <span className="eyebrow">CONNECTED THERMAL CIRCUIT</span>
          <h1>System Explorer</h1>
          <p>Select any component to inspect its state at the chosen simulation time.</p>
        </div>
        <div className="fixture-badge">Example playback: S-03</div>
      </header>
      <PlaybackWorkspace mode="system" />
    </>
  );
}
