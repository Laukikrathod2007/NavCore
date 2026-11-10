import React, { useState } from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { HOSPITAL_NODES, HospitalNode } from "../../lib/hospitalData";
import { HospitalIcon, PinIcon } from "../ui/Icons";

export const MultiFloorExplorer: React.FC = () => {
  const [selectedFloor, setSelectedFloor] = useState<number>(0);
  const [selectedNodeId, setSelectedNodeId] = useState<string>("main_entrance");

  const selectedNode: HospitalNode = HOSPITAL_NODES[selectedNodeId] || HOSPITAL_NODES["main_entrance"];
  const floorNodes = Object.values(HOSPITAL_NODES).filter((n) => n.floor === selectedFloor);

  return (
    <section id="floor-map" style={{ padding: "90px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="TOPOLOGICAL FACILITY MAP"
        title={
          <>
            Explore the <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>multi-floor spatial layout</span>
          </>
        }
        description="20 hospital nodes across 4 vertical floors. Click any room to inspect topological connections, doctor consultation timings, and wheelchair accessibility."
      />

      <div
        style={{
          borderRadius: "24px",
          border: "1px solid #e5e5e0",
          backgroundColor: "#ffffff",
          boxShadow: "0 20px 60px -15px rgba(0, 0, 0, 0.06)",
          overflow: "hidden",
        }}
      >
        {/* Floor Selection Bar */}
        <div
          style={{
            padding: "20px 28px",
            backgroundColor: "#fafafa",
            borderBottom: "1px solid #e5e5e0",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "16px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <HospitalIcon size={20} style={{ color: "#2d5016" }} />
            <span style={{ fontSize: "15px", fontWeight: 700, color: "#0f1410" }}>
              Sample Multi-Specialty Hospital
            </span>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            {[
              { floor: 0, label: "Ground Floor", sub: "Reception & Emergency" },
              { floor: 1, label: "Floor 1", sub: "General & Pediatrics" },
              { floor: 2, label: "Floor 2", sub: "Radiology & Blood Lab" },
              { floor: 3, label: "Floor 3", sub: "Cardiology & Surgery" },
            ].map((f) => (
              <button
                key={f.floor}
                onClick={() => {
                  setSelectedFloor(f.floor);
                  const firstNode = Object.values(HOSPITAL_NODES).find((n) => n.floor === f.floor);
                  if (firstNode) setSelectedNodeId(firstNode.id);
                }}
                style={{
                  padding: "8px 16px",
                  borderRadius: "10px",
                  fontSize: "13px",
                  fontWeight: selectedFloor === f.floor ? 700 : 500,
                  backgroundColor: selectedFloor === f.floor ? "#0f1410" : "#ffffff",
                  color: selectedFloor === f.floor ? "#ffffff" : "#525252",
                  border: selectedFloor === f.floor ? "1px solid #0f1410" : "1px solid #e5e5e0",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                <div>{f.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Map Layout & Node Details */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))" }}>
          {/* SVG Map Canvas */}
          <div style={{ padding: "32px", backgroundColor: "#fbfbfa", borderRight: "1px solid #e5e5e0" }}>
            <div style={{ marginBottom: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", color: "#888888", letterSpacing: "0.5px" }}>
                Interactive Floor {selectedFloor} Blueprint
              </span>
              <Badge variant="moss" size="sm">
                {floorNodes.length} Active Nodes
              </Badge>
            </div>

            <div
              style={{
                borderRadius: "14px",
                border: "1px solid #e5e5e0",
                backgroundColor: "#ffffff",
                padding: "16px",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.03)",
              }}
            >
              <svg viewBox="0 0 600 360" width="100%" height="280" fill="none">
                <rect width="600" height="360" fill="#fafafa" rx="10" />

                {/* Corridor backbone */}
                <rect x="80" y="160" width="440" height="40" rx="8" fill="#f0f0ec" stroke="#d5d5d3" strokeWidth="1.5" />
                <text x="300" y="184" textAnchor="middle" fontSize="11" fill="#737373" fontFamily="sans-serif" fontWeight="600">
                  {selectedFloor === 0 ? "Ground Main Lobby Concourse" : `Floor ${selectedFloor} Central Corridor`}
                </text>

                {/* Vertical elevator core */}
                <g
                  onClick={() => setSelectedNodeId("lift_A")}
                  style={{ cursor: "pointer" }}
                >
                  <rect
                    x="260"
                    y="70"
                    width="80"
                    height="60"
                    rx="8"
                    fill={selectedNodeId === "lift_A" ? "#2d5016" : "#f0f7f2"}
                    stroke={selectedNodeId === "lift_A" ? "#2d5016" : "#abe6c7"}
                    strokeWidth="2"
                  />
                  <text
                    x="300"
                    y="105"
                    textAnchor="middle"
                    fontSize="13"
                    fontWeight="700"
                    fill={selectedNodeId === "lift_A" ? "#ffffff" : "#2d5016"}
                    fontFamily="sans-serif"
                  >
                    🛗 Lift A
                  </text>
                </g>

                {/* Floor Nodes */}
                {floorNodes
                  .filter((n) => n.id !== "lift_A")
                  .map((node, i) => {
                    const isSelected = node.id === selectedNodeId;
                    const posX = 70 + (i % 3) * 165;
                    const posY = i >= 3 ? 230 : 60;

                    return (
                      <g
                        key={node.id}
                        transform={`translate(${posX}, ${posY})`}
                        onClick={() => setSelectedNodeId(node.id)}
                        style={{ cursor: "pointer" }}
                      >
                        <rect
                          width="140"
                          height="64"
                          rx="10"
                          fill={isSelected ? "#0f1410" : "#ffffff"}
                          stroke={isSelected ? "#0f1410" : "#e5e5e0"}
                          strokeWidth={isSelected ? "2" : "1.5"}
                          filter={isSelected ? "drop-shadow(0 4px 12px rgba(0,0,0,0.15))" : "none"}
                        />
                        <text
                          x="70"
                          y="28"
                          textAnchor="middle"
                          fontSize="11"
                          fontWeight={isSelected ? "700" : "600"}
                          fill={isSelected ? "#ffffff" : "#0f1410"}
                          fontFamily="sans-serif"
                        >
                          {node.name.length > 17 ? node.name.slice(0, 16) + "…" : node.name}
                        </text>
                        <text
                          x="70"
                          y="46"
                          textAnchor="middle"
                          fontSize="10"
                          fill={isSelected ? "#abe6c7" : "#5c8a5c"}
                          fontFamily="sans-serif"
                        >
                          {node.roomNumber ? `Room ${node.roomNumber}` : node.type}
                        </text>
                      </g>
                    );
                  })}
              </svg>
            </div>
            <div style={{ fontSize: "11px", color: "#888888", marginTop: "12px", textAlign: "center" }}>
              💡 Click any department card or elevator above to inspect its real-time topological metadata.
            </div>
          </div>

          {/* Node Metadata Inspector Card */}
          <div style={{ padding: "32px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    backgroundColor: "#f0f7f2",
                    color: "#2d5016",
                    fontSize: "12px",
                    fontWeight: 700,
                  }}
                >
                  Floor {selectedNode.floor} • Wing {selectedNode.wing || "Main"}
                </span>
                <span style={{ fontSize: "12px", color: selectedNode.isAvailable ? "#00a544" : "#e40014", fontWeight: 600 }}>
                  {selectedNode.isAvailable ? "● Operational (Open)" : "● Temporarily Closed"}
                </span>
              </div>

              <h3 style={{ fontSize: "24px", fontWeight: 700, color: "#0f1410", margin: "0 0 4px" }}>
                {selectedNode.name}
              </h3>
              {selectedNode.hindiName && (
                <div style={{ fontSize: "15px", color: "#5c8a5c", fontWeight: 500, marginBottom: "14px" }}>
                  {selectedNode.hindiName} / {selectedNode.marathiName}
                </div>
              )}

              <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#525252", margin: "0 0 20px" }}>
                {selectedNode.description}
              </p>

              {/* Attributes table */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "20px" }}>
                <div style={{ padding: "12px", borderRadius: "8px", backgroundColor: "#fafafa", border: "1px solid #e5e5e0" }}>
                  <span style={{ fontSize: "11px", color: "#888888", display: "block" }}>Room Designation</span>
                  <span style={{ fontSize: "14px", fontWeight: 600, color: "#0f1410" }}>
                    {selectedNode.roomNumber || "N/A"}
                  </span>
                </div>

                <div style={{ padding: "12px", borderRadius: "8px", backgroundColor: "#fafafa", border: "1px solid #e5e5e0" }}>
                  <span style={{ fontSize: "11px", color: "#888888", display: "block" }}>Operating Hours</span>
                  <span style={{ fontSize: "14px", fontWeight: 600, color: "#0f1410" }}>
                    {selectedNode.timing}
                  </span>
                </div>

                <div style={{ padding: "12px", borderRadius: "8px", backgroundColor: "#fafafa", border: "1px solid #e5e5e0" }}>
                  <span style={{ fontSize: "11px", color: "#888888", display: "block" }}>Accessibility</span>
                  <span style={{ fontSize: "13px", fontWeight: 600, color: selectedNode.isAccessible ? "#00a544" : "#b45309" }}>
                    {selectedNode.isAccessible ? "✓ Wheelchair Friendly" : "Stairs Only"}
                  </span>
                </div>

                <div style={{ padding: "12px", borderRadius: "8px", backgroundColor: "#fafafa", border: "1px solid #e5e5e0" }}>
                  <span style={{ fontSize: "11px", color: "#888888", display: "block" }}>Nearby Landmarks</span>
                  <span style={{ fontSize: "13px", fontWeight: 500, color: "#0f1410" }}>
                    {selectedNode.landmarks.join(", ") || "Corridor Signboard"}
                  </span>
                </div>
              </div>

              {/* Topological Neighbors */}
              <div>
                <span style={{ fontSize: "12px", fontWeight: 700, color: "#888888", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  Direct Topological Edges ({selectedNode.connectsTo.length})
                </span>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "8px" }}>
                  {selectedNode.connectsTo.map((edge) => (
                    <span
                      key={edge}
                      onClick={() => {
                        const target = HOSPITAL_NODES[edge];
                        if (target) {
                          setSelectedFloor(target.floor);
                          setSelectedNodeId(edge);
                        }
                      }}
                      style={{
                        padding: "3px 8px",
                        borderRadius: "6px",
                        fontSize: "11px",
                        fontFamily: "monospace",
                        backgroundColor: "#f5f5f4",
                        border: "1px solid #e5e5e0",
                        color: "#0f1410",
                        cursor: "pointer",
                      }}
                    >
                      {edge} ↗
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ marginTop: "24px", paddingTop: "16px", borderTop: "1px solid #f0f0ec", fontSize: "12px", color: "#888888" }}>
              Canonical Node ID: <code style={{ color: "#2d5016", fontWeight: 600 }}>{selectedNode.id}</code>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

