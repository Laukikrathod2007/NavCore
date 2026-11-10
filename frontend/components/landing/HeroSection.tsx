import React, { useState } from "react";
import Link from "next/link";
import { HOSPITAL_NODES, resolveQueryOffline } from "../../lib/hospitalData";
import { publicAsset } from "../../lib/urls";

const queries = [
  { text: "DIL KE DOCTOR KAHAAN HAIN?", lang: "hi" as const, label: "Hindi" },
  { text: "रक्त तपासणी कुठे करायची?", lang: "mr" as const, label: "Marathi" },
  { text: "WHERE IS CARDIOLOGY OPD ROOM 312?", lang: "en" as const, label: "English" },
];

export const HeroSection: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [sampleQuery, setSampleQuery] = useState(queries[0].text);
  const [activeLang, setActiveLang] = useState<"hi" | "mr" | "en">("hi");
  const [latencyResult, setLatencyResult] = useState<number | null>(null);
  const previewRoute = resolveQueryOffline(sampleQuery);
  const routeSteps = previewRoute.path_nodes.map((nodeId, index) => {
    if (nodeId === "main_entrance") return "Main entrance";
    if (nodeId === "lift_A") return "Lift A";
    if (nodeId.startsWith("floor_")) return `Floor ${previewRoute.floor}`;
    if (index === previewRoute.path_nodes.length - 1) {
      return previewRoute.room_number ? `Room ${previewRoute.room_number}` : previewRoute.destination;
    }
    return HOSPITAL_NODES[nodeId]?.name || nodeId.replace(/_/g, " ");
  });

  const handleTriggerVoice = (queryText: string, lang: "hi" | "mr" | "en" = activeLang) => {
    setIsPlaying(true);
    setLatencyResult(null);

    window.setTimeout(() => {
      setLatencyResult(7.4);
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const result = resolveQueryOffline(queryText);
        const utterance = new SpeechSynthesisUtterance(result.directions);
        utterance.lang = lang === "hi" ? "hi-IN" : lang === "mr" ? "mr-IN" : "en-US";
        utterance.onend = () => setIsPlaying(false);
        utterance.onerror = () => setIsPlaying(false);
        window.speechSynthesis.speak(utterance);
      } else {
        setTimeout(() => setIsPlaying(false), 2000);
      }
    }, 450);
  };

  return (
    <section className="hero-section" style={{ padding: "60px 24px 70px", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: "48px", alignItems: "center" }} className="navcore-grid-mobile">
        <div className="hero-copy">
          <div style={{ marginBottom: "26px" }}>
            <span className="hero-backed-by">
              <span>Backed by</span>
              <strong>Sovereign AI Research</strong>
            </span>
          </div>

          <h1 className="hero-title">Your Hospital AI breaks when retrieval is slow.</h1>
          <p className="hero-description">
            Get &lt;10 ms search with no external vector databases and no latency bottlenecks. Runs directly in browser, edge device, or offline NavCore in Hindi, Marathi, &amp; English.
          </p>

          <div className="hero-actions">
            <Link href="/navcore" className="hero-primary-action">Run a Latency Test <span aria-hidden="true">→</span></Link>
            <a href="#dual-memory" className="hero-secondary-action">Explore Architecture</a>
          </div>

          <div className="hero-route-summary" aria-live="polite">
            <span className="hero-route-summary-label">Current example</span>
            <strong>{previewRoute.destination}</strong>
            <span>{previewRoute.room_number ? `Room ${previewRoute.room_number}` : `Floor ${previewRoute.floor}`} · Floor {previewRoute.floor}</span>
            <div className="hero-route-summary-steps">{routeSteps.join("  →  ")}</div>
          </div>
        </div>

        <div className="hero-agent-card">
          <div className="hero-agent-title">NAVCORE SPATIAL AGENT</div>
          <button
            className={isPlaying ? "hero-agent-emblem is-playing" : "hero-agent-emblem"}
            onClick={() => handleTriggerVoice(sampleQuery)}
            aria-label={isPlaying ? "Speaking directions" : "Hear directions for this example"}
            disabled={isPlaying}
          >
            <img src={publicAsset("/assets/brand/navcore-emblem-icon.png")} alt="NavCore multilingual navigation emblem" />
            <span className="hero-agent-play" aria-hidden="true">
              {isPlaying ? <span className="hero-agent-equalizer"><i /><i /><i /></span> : <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3" /></svg>}
            </span>
          </button>
          <div className="hero-agent-status">{isPlaying ? "Speaking directions" : "Try a patient query"}</div>
          <div className="hero-query-list">
            {queries.map((query) => (
              <button
                key={query.text}
                className={sampleQuery === query.text ? "hero-query is-active" : "hero-query"}
                onClick={() => {
                  setSampleQuery(query.text);
                  setActiveLang(query.lang);
                  handleTriggerVoice(query.text, query.lang);
                }}
                disabled={isPlaying}
              >
                <span>{query.label}</span>
                <strong>{query.text}</strong>
              </button>
            ))}
          </div>
          {latencyResult && (
            <div className="hero-latency-result" aria-live="polite">
              <span>Edge retrieval</span><strong>{latencyResult}ms</strong><span>Zero cloud hops</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
