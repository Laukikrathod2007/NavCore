import React from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";

export const HardwareSpecs: React.FC = () => {
  const hardwareProfiles = [
    {
      title: "Commodity Laptop",
      subtitle: "Standard Office / Clinic Machine",
      specs: "Intel i5 / AMD Ryzen 5, 8GB RAM, 10GB Disk",
      price: "$0 (Use existing hardware)",
      recommendedFor: "Small OPDs, diagnostic centers, reception desks",
      latency: "~380ms total latency",
    },
    {
      title: "Mini-PC / Intel NUC",
      subtitle: "Dedicated NavCore Touch Enclosure",
      specs: "Intel N100 / Core i3, 16GB RAM, Fanless",
      price: "~$180 - $280 hardware cost",
      recommendedFor: "Public hospital waiting lobbies, pillar mounts",
      latency: "~320ms total latency",
      featured: true,
    },
    {
      title: "Edge Accelerator (Jetson / Mac Mini)",
      subtitle: "High-Throughput Concurrency",
      specs: "NVIDIA Jetson Orin Nano / Apple M2 (16GB)",
      price: "~$499 hardware cost",
      recommendedFor: "Metro hospitals, airport terminals, 50+ concurrent queries/min",
      latency: "<180ms total latency",
    },
  ];

  return (
    <section style={{ padding: "80px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="EDGE HARDWARE MATRIX"
        title={
          <>
            Runs on <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>everyday hardware</span>
          </>
        }
        description="No specialized cloud TPUs or GPU clusters required. NavCore was explicitly designed to operate on inexpensive, offline edge machines found in Indian public institutions."
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "24px",
        }}
      >
        {hardwareProfiles.map((hw) => (
          <Card
            key={hw.title}
            variant={hw.featured ? "moss" : "default"}
            style={{
              padding: "32px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              border: hw.featured ? "2px solid #5c8a5c" : "1px solid #e5e5e0",
            }}
          >
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontSize: "12px", fontWeight: 700, color: hw.featured ? "#2d5016" : "#737373", textTransform: "uppercase" }}>
                  {hw.subtitle}
                </span>
                {hw.featured && (
                  <Badge variant="dark" size="sm">
                    Recommended NavCore
                  </Badge>
                )}
              </div>

              <h3 style={{ fontSize: "22px", fontWeight: 700, color: "#0f1410", marginBottom: "8px" }}>
                {hw.title}
              </h3>

              <div style={{ fontSize: "18px", fontWeight: 700, color: hw.featured ? "#2d5016" : "#0f1410", marginBottom: "16px" }}>
                {hw.price}
              </div>

              <div style={{ backgroundColor: "#ffffff", padding: "14px", borderRadius: "10px", border: "1px solid #e5e5e0", marginBottom: "16px" }}>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#888888", textTransform: "uppercase", marginBottom: "4px" }}>
                  Minimum Spec:
                </div>
                <div style={{ fontSize: "13px", color: "#0f1410", fontFamily: "monospace" }}>
                  {hw.specs}
                </div>
              </div>

              <p style={{ fontSize: "13px", lineHeight: "1.5", color: "#525252", margin: 0 }}>
                {hw.recommendedFor}
              </p>
            </div>

            <div style={{ marginTop: "24px", paddingTop: "16px", borderTop: "1px solid rgba(0,0,0,0.06)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "12px", color: "#737373" }}>Benchmarked Speed:</span>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "#2d5016" }}>{hw.latency}</span>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
};

