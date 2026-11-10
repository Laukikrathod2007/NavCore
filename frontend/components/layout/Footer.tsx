import React from "react";
import Link from "next/link";
import { Badge } from "../ui/Badge";

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        backgroundColor: "#ffffff",
        borderTop: "1px solid #e5e5e0",
        padding: "70px 24px 40px",
        marginTop: "100px",
      }}
    >
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {/* Top grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "40px",
            marginBottom: "60px",
          }}
        >
          {/* Brand info */}
          <div style={{ gridColumn: "span 2" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <img src="/assets/brand/navcore-emblem-icon.png" alt="NavCore" width="32" height="32" />
              <span style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410" }}>
                Nav<span style={{ color: "#2d5016" }}>Core</span>
              </span>
              <span style={{ fontSize: "11px", fontWeight: 600, color: "#5c8a5c", backgroundColor: "#f0f7f2", padding: "2px 8px", borderRadius: "9999px" }}>
                v2.4
              </span>
            </div>
            <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#666666", maxWidth: "340px", margin: "0 0 20px" }}>
              Offline dual-memory spatial RAG engine for multilingual physical spaces. Zero internet dependency, zero junction hallucination.
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Badge variant="moss" pulse size="sm">
                Edge Offline Engine Active
              </Badge>
              <span style={{ fontSize: "12px", color: "#888888" }}>
                Sub-10ms Hot-Path
              </span>
            </div>
          </div>

          {/* Architecture Links */}
          <div>
            <h4 style={{ fontSize: "13px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px", color: "#0f1410", marginBottom: "16px" }}>
              Architecture
            </h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "14px", color: "#666666", display: "flex", flexDirection: "column", gap: "10px" }}>
              <li>Dual-Memory Matrix</li>
              <li>Qdrant Edge Vector DB</li>
              <li>NetworkX Topological Graph</li>
              <li>LangGraph 7-Node Agent</li>
              <li>Whisper Tiny (Offline ASR)</li>
              <li>Llama 3.2 3B (Local LLM)</li>
            </ul>
          </div>

          {/* Performance & Benchmarks */}
          <div>
            <h4 style={{ fontSize: "13px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px", color: "#0f1410", marginBottom: "16px" }}>
              Evaluation
            </h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "14px", color: "#666666", display: "flex", flexDirection: "column", gap: "10px" }}>
              <li>76% Destination Accuracy</li>
              <li>90% Junction Accuracy</li>
              <li>340ms Edge Latency</li>
              <li>200 Multilingual Queries</li>
              <li>0% Hallucination Guarantee</li>
              <li>A/B Baseline Comparison</li>
            </ul>
          </div>

          {/* Interface & Apps */}
          <div>
            <h4 style={{ fontSize: "13px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px", color: "#0f1410", marginBottom: "16px" }}>
              Apps & Interfaces
            </h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: "14px", color: "#666666", display: "flex", flexDirection: "column", gap: "10px" }}>
              <li><Link href="/navcore" style={{ color: "#2d5016", fontWeight: 600, textDecoration: "none" }}>Open NavCore ↗</Link></li>
              <li><Link href="/admin" style={{ color: "#0f1410", textDecoration: "none" }}>Hospital Admin Portal ↗</Link></li>
              <li><a href="#interactive-demo" style={{ color: "#666666", textDecoration: "none" }}>Interactive Playground</a></li>
              <li><a href="#floor-map" style={{ color: "#666666", textDecoration: "none" }}>Floor Map Navigator</a></li>
              <li><a href="#code-integration" style={{ color: "#666666", textDecoration: "none" }}>Python & REST SDK</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div
          style={{
            paddingTop: "30px",
            borderTop: "1px solid #f0f0ec",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "16px",
            fontSize: "13px",
            color: "#888888",
          }}
        >
          <div>
            © {new Date().getFullYear()} NavCore Spatial RAG. Built for high-traffic physical infrastructure.
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <span>Hindi • Marathi • English • Hinglish</span>
            <span>•</span>
            <span>100% Air-Gapped Capable</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

