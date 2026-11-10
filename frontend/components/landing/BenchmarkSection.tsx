import React from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { BENCHMARK_COMPARISONS, LANGUAGE_PERFORMANCE } from "../../lib/benchmarkData";

export const BenchmarkSection: React.FC = () => {
  return (
    <section id="benchmark" style={{ padding: "90px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="EMPIRICAL BENCHMARKS"
        title={
          <>
            Your bottleneck isn&apos;t the LLM. It&apos;s <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>spatial hallucination.</span>
          </>
        }
        description="Tested across 200 real Indian hospital queries in Hindi, Marathi, Hinglish, and English. NavCore eliminates the 59% junction failure rate found in standalone LLMs."
      />

      {/* 4 Core Animated Metrics Cards with Count-up on scroll */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "20px",
          marginBottom: "48px",
        }}
      >
        <div
          style={{
            padding: "28px 24px",
            borderRadius: "16px",
            backgroundColor: "#f0f7f2",
            border: "1px solid #abe6c7",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.03)",
          }}
        >
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#2d5016", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
            Destination Accuracy
          </div>
          <div style={{ fontSize: "44px", fontWeight: 700, letterSpacing: "-0.04em", color: "#0f1410", marginBottom: "6px" }}>
            <AnimatedNumber target={76} suffix="%" duration={1400} />
          </div>
          <div style={{ fontSize: "13px", color: "#223d11", lineHeight: "1.4" }}>
            Across 200 real patient queries in 4 languages
          </div>
        </div>

        <div
          style={{
            padding: "28px 24px",
            borderRadius: "16px",
            backgroundColor: "#f0f7f2",
            border: "1px solid #abe6c7",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.03)",
          }}
        >
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#2d5016", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
            Junction Accuracy
          </div>
          <div style={{ fontSize: "44px", fontWeight: 700, letterSpacing: "-0.04em", color: "#0f1410", marginBottom: "6px" }}>
            <AnimatedNumber target={90} suffix="%" duration={1600} />
          </div>
          <div style={{ fontSize: "13px", color: "#223d11", lineHeight: "1.4" }}>
            Zero topological graph hallucinations
          </div>
        </div>

        <div
          style={{
            padding: "28px 24px",
            borderRadius: "16px",
            backgroundColor: "#ffffff",
            border: "1px solid #e5e5e0",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.03)",
          }}
        >
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#737373", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
            Hot-Path Latency
          </div>
          <div style={{ fontSize: "44px", fontWeight: 700, letterSpacing: "-0.04em", color: "#0f1410", marginBottom: "6px" }}>
            &lt;<AnimatedNumber target={10} duration={1200} />ms
          </div>
          <div style={{ fontSize: "13px", color: "#525252", lineHeight: "1.4" }}>
            Sub-10ms vector retrieval via Qdrant Edge
          </div>
        </div>

        <div
          style={{
            padding: "28px 24px",
            borderRadius: "16px",
            backgroundColor: "#ffffff",
            border: "1px solid #e5e5e0",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.03)",
          }}
        >
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#737373", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
            Cloud API Bill
          </div>
          <div style={{ fontSize: "44px", fontWeight: 700, letterSpacing: "-0.04em", color: "#0f1410", marginBottom: "6px" }}>
            $0
          </div>
          <div style={{ fontSize: "13px", color: "#525252", lineHeight: "1.4" }}>
            Runs completely offline on consumer laptops &amp; NavCore devices
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <Card variant="default" style={{ padding: "0", overflow: "hidden", marginBottom: "40px" }}>
        <div style={{ padding: "24px 28px", borderBottom: "1px solid #e5e5e0", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410", margin: "0 0 4px" }}>
              Benchmark: NavCore vs Baseline Architectures
            </h3>
            <p style={{ fontSize: "13px", color: "#737373", margin: 0 }}>
              Evaluated on 200 real patient navigation queries across 4 language distributions.
            </p>
          </div>
          <Badge variant="moss" size="sm">
            200 Query Evaluation Set
          </Badge>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#fafafa", borderBottom: "1px solid #e5e5e0", color: "#737373", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                <th style={{ padding: "14px 24px" }}>Architecture</th>
                <th style={{ padding: "14px 20px" }}>Destination Accuracy</th>
                <th style={{ padding: "14px 20px" }}>Junction Accuracy</th>
                <th style={{ padding: "14px 20px" }}>Hot-Path Latency</th>
                <th style={{ padding: "14px 20px" }}>Offline Edge Ready</th>
                <th style={{ padding: "14px 20px" }}>Junction Errors</th>
              </tr>
            </thead>
            <tbody>
              {BENCHMARK_COMPARISONS.map((row) => {
                const isNavCore = row.name.includes("NavCore");
                return (
                  <tr
                    key={row.name}
                    style={{
                      borderBottom: "1px solid #f0f0ec",
                      backgroundColor: isNavCore ? "#fbfdfa" : "transparent",
                      fontWeight: isNavCore ? 600 : 400,
                    }}
                  >
                    <td style={{ padding: "18px 24px", color: "#0f1410" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        {isNavCore && (
                          <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#05df72", display: "inline-block" }} />
                        )}
                        <span>{row.name}</span>
                      </div>
                      <span style={{ fontSize: "11px", color: "#888888", display: "block" }}>{row.hardware}</span>
                    </td>
                    <td style={{ padding: "18px 20px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "4px 10px",
                          borderRadius: "6px",
                          backgroundColor: isNavCore ? "#f0f7f2" : "#f5f5f4",
                          color: isNavCore ? "#2d5016" : "#0f1410",
                          fontWeight: 700,
                        }}
                      >
                        {row.destinationAccuracy}%
                      </span>
                    </td>
                    <td style={{ padding: "18px 20px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "4px 10px",
                          borderRadius: "6px",
                          backgroundColor: isNavCore ? "#f0f7f2" : "#f5f5f4",
                          color: isNavCore ? "#2d5016" : "#0f1410",
                          fontWeight: 700,
                        }}
                      >
                        {row.junctionAccuracy}%
                      </span>
                    </td>
                    <td style={{ padding: "18px 20px", color: isNavCore ? "#2d5016" : "#525252", fontFamily: "monospace" }}>
                      {row.avgLatencyMs}ms
                    </td>
                    <td style={{ padding: "18px 20px" }}>
                      {row.offlineCapable ? (
                        <span style={{ color: "#00a544", fontWeight: 600 }}>✓ Yes (100% Offline)</span>
                      ) : (
                        <span style={{ color: "#e40014" }}>✗ Requires Cloud Wi-Fi</span>
                      )}
                    </td>
                    <td style={{ padding: "18px 20px" }}>
                      {row.junctionHallucinations === 0 ? (
                        <span style={{ color: "#00a544", fontWeight: 700 }}>0 (Zero)</span>
                      ) : (
                        <span style={{ color: "#e40014", fontWeight: 600 }}>{row.junctionHallucinations} failures</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Multilingual breakdown */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "16px",
        }}
      >
        {LANGUAGE_PERFORMANCE.map((item) => (
          <div
            key={item.language}
            style={{
              padding: "20px",
              borderRadius: "14px",
              backgroundColor: "#ffffff",
              border: "1px solid #e5e5e0",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <span style={{ fontWeight: 600, color: "#0f1410", fontSize: "14px" }}>{item.language}</span>
              <span style={{ fontSize: "12px", color: "#888888" }}>{item.queryCount} queries</span>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
              <span style={{ fontSize: "24px", fontWeight: 700, color: "#2d5016" }}>
                <AnimatedNumber target={item.accuracy} suffix="%" duration={1200} />
              </span>
              <span style={{ fontSize: "12px", color: "#525252" }}>
                Destination Acc.
              </span>
            </div>
            <div style={{ marginTop: "8px", height: "6px", backgroundColor: "#f0f0ec", borderRadius: "9999px", overflow: "hidden" }}>
              <div style={{ width: `${item.accuracy}%`, height: "100%", backgroundColor: "#5c8a5c", borderRadius: "9999px" }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
