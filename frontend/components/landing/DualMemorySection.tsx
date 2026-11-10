import React from "react";
import { publicAsset } from "../../lib/urls";

const principles = [
  {
    label: "Semantic memory",
    image: publicAsset("/assets/moss/cube-planes.svg"),
    title: "Replace cloud vector databases",
    description: "No external retrieval layer. No network hops. Dual-memory architecture resolves colloquial patient speech and eliminates latency at the source.",
  },
  {
    label: "Offline deployment",
    image: publicAsset("/assets/moss/concentric-orbits.svg"),
    title: "Run navigation where your patients are",
    description: "NavCore. Edge laptop. Tablet. Touchscreen. Deploy in concrete basements, emergency triage, and Wi-Fi dead zones where reliability matters most.",
  },
  {
    label: "Topological memory",
    image: publicAsset("/assets/moss/speedometer-dial.svg"),
    title: "Retrieve and route in <10 ms",
    description: "Enable real-time turn-by-turn conversational guidance. 0% junction hallucination guaranteed by deterministic topological graph pathfinding.",
  },
];

export const DualMemorySection: React.FC = () => (
  <section id="dual-memory" className="method-section" style={{ padding: "80px 24px 90px", maxWidth: "1200px", margin: "0 auto" }}>
    <div className="method-inner">
      <div className="method-heading">
        <div className="method-eyebrow">RETHINKING INDOOR NAVIGATION</div>
        <h2>Why NavCore is fundamentally different</h2>
      </div>
      <div className="method-cards">
        {principles.map((principle) => (
          <article className="method-card" key={principle.title}>
            <div className="method-card-label">{principle.label}</div>
            <div className="method-artwork"><img src={principle.image} alt="" /></div>
            <h3>{principle.title}</h3>
            <p>{principle.description}</p>
          </article>
        ))}
      </div>
    </div>
  </section>
);
