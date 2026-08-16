import type { Metadata } from "next";
import { PlaybackWorkspace } from "@/components/playback-workspace";

export const metadata: Metadata = { title: "System Explorer" };

export default function SystemPage() {
  return <><header className="page-header split"><div><span className="eyebrow">COMPONENT-CENTRIC PLAYBACK</span><h1>System Explorer</h1><p>Follow heat, coolant, controls, and air flow through the V1 system boundary at a selected simulation time.</p></div><div className="fixture-badge">Example playback: S-03</div></header><PlaybackWorkspace mode="system" /></>;
}
