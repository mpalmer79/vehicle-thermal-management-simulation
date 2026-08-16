import Link from "next/link";
import type { ScenarioCardData } from "@/lib/scenarios";

export function ScenarioCard({ scenario }: { scenario: ScenarioCardData }) {
  return <article className="scenario-card"><div className="scenario-card-head"><span className="scenario-id">{scenario.id}</span><span className={`scenario-type ${scenario.category.toLowerCase()}`}>{scenario.category}</span></div><h3>{scenario.name}</h3><p>{scenario.purpose}</p><div className="scenario-facts"><span>{scenario.ambient} °C ambient</span><span>{scenario.rpm} rpm</span><span>{scenario.load}% load</span><span>{scenario.speedKmh} km/h</span></div>{scenario.basedOn && <small>Based on {scenario.basedOn}</small>}<div className="scenario-actions"><Link href={`/simulate?scenario=${scenario.id}`}>Load in Simulation Lab</Link>{scenario.id === "S-03" && <Link className="text-accent" href="/results/demo-s03">View fixture result</Link>}</div></article>;
}
