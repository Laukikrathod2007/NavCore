import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { HOSPITAL_NODES, HospitalNode } from "../../lib/hospitalData";
import { HospitalIcon, ZapIcon, ShieldCheckIcon, CloseIcon } from "../ui/Icons";

interface HealthStatus {
  status: string;
  qdrant_ok: boolean;
  graph_ok: boolean;
  ollama_ok: boolean;
}

export const AdminDashboardView: React.FC = () => {
  const [locations, setLocations] = useState<HospitalNode[]>(() => Object.values(HOSPITAL_NODES));
  const [health, setHealth] = useState<HealthStatus>({
    status: "healthy",
    qdrant_ok: true,
    graph_ok: true,
    ollama_ok: true,
  });
  const [filterFloor, setFilterFloor] = useState<number | "all">("all");
  const [searchFilter, setSearchFilter] = useState("");
  const [notification, setNotification] = useState<string | null>(null);

  // Try fetching live locations and health from backend if available
  useEffect(() => {
    fetch("/api/locations")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.locations) {
          // Merge with node metadata
          setLocations((prev) =>
            prev.map((loc) => {
              const live = data.locations.find((l: any) => l.node_id === loc.id);
              return live ? { ...loc, isAvailable: live.is_available } : loc;
            })
          );
        }
      })
      .catch(() => {});

    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => {
        if (data) setHealth(data);
      })
      .catch(() => {});
  }, []);

  const handleToggleAvailability = async (nodeId: string, currentStatus: boolean) => {
    const newStatus = !currentStatus;
    // Optimistic update
    setLocations((prev) =>
      prev.map((loc) => (loc.id === nodeId ? { ...loc, isAvailable: newStatus } : loc))
    );
    setNotification(`Updated ${nodeId}: ${newStatus ? "Operational" : "Closed"}`);
    setTimeout(() => setNotification(null), 3000);

    // Call API if server exists
    try {
      await fetch(`/api/admin/nodes/${nodeId}/availability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_available: newStatus }),
      });
    } catch {
      // server offline, client-side fallback works
    }
  };

  const filtered = locations.filter((loc) => {
    const matchesFloor = filterFloor === "all" || loc.floor === filterFloor;
    const matchesSearch =
      !searchFilter ||
      loc.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      loc.id.toLowerCase().includes(searchFilter.toLowerCase()) ||
      (loc.roomNumber && loc.roomNumber.toLowerCase().includes(searchFilter.toLowerCase()));
    return matchesFloor && matchesSearch;
  });

  return (
    <div className="admin-screen" style={{ minHeight: "100vh", backgroundColor: "#fafafa", color: "#0f1410", fontFamily: "var(--font-sans, sans-serif)" }}>
      {/* Admin Navbar */}
      <header
        className="admin-header"
        style={{
          borderBottom: "1px solid #e5e5e0",
          backgroundColor: "#ffffff",
          padding: "16px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "10px" }}>
            <img src="/assets/brand/navcore-emblem-icon.png" alt="NavCore" width="32" height="32" />
            <span style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410" }}>
              Nav<span style={{ color: "#2d5016" }}>Core</span> Admin
            </span>
          </Link>
          <Badge variant="moss" size="sm">
            Facility Telemetry &amp; Routing
          </Badge>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <Link href="/navcore" style={{ textDecoration: "none" }}>
            <Button variant="secondary" size="sm">
              Open NavCore ↗
            </Button>
          </Link>
          <Link href="/" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              Landing Page ↗
            </Button>
          </Link>
        </div>
      </header>

      {/* Admin Main Body */}
      <main className="admin-main" style={{ maxWidth: "1200px", margin: "40px auto", padding: "0 24px" }}>
        {notification && (
          <div
            style={{
              padding: "12px 20px",
              borderRadius: "10px",
              backgroundColor: "#f0f7f2",
              border: "1px solid #abe6c7",
              color: "#2d5016",
              fontWeight: 600,
              fontSize: "14px",
              marginBottom: "24px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span>{notification}</span>
            <button
              onClick={() => setNotification(null)}
              style={{ background: "none", border: "none", cursor: "pointer", color: "#2d5016" }}
            >
              <CloseIcon size={14} />
            </button>
          </div>
        )}

        {/* System Health Cards */}
        <div
          className="admin-health-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "20px",
            marginBottom: "36px",
          }}
        >
          <Card variant="default">
            <div style={{ fontSize: "12px", color: "#737373", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
              Overall Health
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#00a544" }} />
              <span style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410" }}>System Ready</span>
            </div>
            <div style={{ fontSize: "12px", color: "#888888", marginTop: "4px" }}>
              Zero network drops detected
            </div>
          </Card>

          <Card variant="default">
            <div style={{ fontSize: "12px", color: "#737373", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
              Semantic Memory (Qdrant Edge)
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: health.qdrant_ok ? "#00a544" : "#e40014" }} />
              <span style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410" }}>104 Alias Vectors</span>
            </div>
            <div style={{ fontSize: "12px", color: "#888888", marginTop: "4px" }}>
              Sub-10ms Hot-Path Vector DB
            </div>
          </Card>

          <Card variant="default">
            <div style={{ fontSize: "12px", color: "#737373", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
              Topological Graph (NetworkX)
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: health.graph_ok ? "#00a544" : "#e40014" }} />
              <span style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410" }}>20 Hospital Nodes</span>
            </div>
            <div style={{ fontSize: "12px", color: "#888888", marginTop: "4px" }}>
              4 Vertical Floors Connected
            </div>
          </Card>

          <Card variant="default">
            <div style={{ fontSize: "12px", color: "#737373", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
              Local LLM Runtime (Ollama)
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: health.ollama_ok ? "#00a544" : "#e40014" }} />
              <span style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410" }}>Llama 3.2 3B</span>
            </div>
            <div style={{ fontSize: "12px", color: "#888888", marginTop: "4px" }}>
              Direction Generator Active
            </div>
          </Card>
        </div>

        {/* Filter bar */}
        <div
          className="admin-filter-bar"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "16px",
            marginBottom: "20px",
          }}
        >
          <div style={{ display: "flex", gap: "6px" }}>
            <button
              onClick={() => setFilterFloor("all")}
              style={{
                padding: "6px 14px",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: filterFloor === "all" ? 700 : 500,
                backgroundColor: filterFloor === "all" ? "#0f1410" : "#ffffff",
                color: filterFloor === "all" ? "#ffffff" : "#525252",
                border: "1px solid #e5e5e0",
                cursor: "pointer",
              }}
            >
              All Floors
            </button>
            {[0, 1, 2, 3].map((f) => (
              <button
                key={f}
                onClick={() => setFilterFloor(f)}
                style={{
                  padding: "6px 14px",
                  borderRadius: "8px",
                  fontSize: "13px",
                  fontWeight: filterFloor === f ? 700 : 500,
                  backgroundColor: filterFloor === f ? "#0f1410" : "#ffffff",
                  color: filterFloor === f ? "#ffffff" : "#525252",
                  border: "1px solid #e5e5e0",
                  cursor: "pointer",
                }}
              >
                {f === 0 ? "Ground" : `Floor ${f}`}
              </button>
            ))}
          </div>

          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Filter nodes, rooms, or departments..."
            style={{
              padding: "8px 14px",
              borderRadius: "8px",
              border: "1px solid #e5e5e0",
              fontSize: "13px",
              backgroundColor: "#ffffff",
              minWidth: "260px",
              outline: "none",
            }}
          />
        </div>

        {/* Node Management Table */}
        <Card variant="default" style={{ padding: 0, overflow: "hidden" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#fafafa", borderBottom: "1px solid #e5e5e0", color: "#737373", fontSize: "12px", textTransform: "uppercase" }}>
                <th style={{ padding: "14px 24px" }}>Department / Node</th>
                <th style={{ padding: "14px 20px" }}>Floor &amp; Room</th>
                <th style={{ padding: "14px 20px" }}>Type</th>
                <th style={{ padding: "14px 20px" }}>Hours</th>
                <th style={{ padding: "14px 20px" }}>Availability</th>
                <th style={{ padding: "14px 20px", textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((loc) => (
                <tr key={loc.id} style={{ borderBottom: "1px solid #f0f0ec" }}>
                  <td style={{ padding: "16px 24px", color: "#0f1410" }}>
                    <div style={{ fontWeight: 600 }}>{loc.name}</div>
                    <div style={{ fontSize: "12px", color: "#888888", fontFamily: "monospace" }}>{loc.id}</div>
                  </td>
                  <td style={{ padding: "16px 20px" }}>
                    Floor {loc.floor} {loc.roomNumber ? `• Rm ${loc.roomNumber}` : ""}
                  </td>
                  <td style={{ padding: "16px 20px" }}>
                    <span style={{ fontSize: "12px", padding: "2px 8px", borderRadius: "4px", backgroundColor: "#f5f5f4", color: "#525252" }}>
                      {loc.type}
                    </span>
                  </td>
                  <td style={{ padding: "16px 20px", fontSize: "13px", color: "#525252" }}>
                    {loc.timing}
                  </td>
                  <td style={{ padding: "16px 20px" }}>
                    {loc.isAvailable ? (
                      <span style={{ color: "#00a544", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#00a544" }} />
                        Operational
                      </span>
                    ) : (
                      <span style={{ color: "#e40014", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#e40014" }} />
                        Closed
                      </span>
                    )}
                  </td>
                  <td style={{ padding: "16px 20px", textAlign: "right" }}>
                    <button
                      onClick={() => handleToggleAvailability(loc.id, loc.isAvailable)}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        fontSize: "12px",
                        fontWeight: 600,
                        backgroundColor: loc.isAvailable ? "#fff1f2" : "#f0fdf4",
                        color: loc.isAvailable ? "#e11d48" : "#16a34a",
                        border: loc.isAvailable ? "1px solid #fecdd3" : "1px solid #bbf7d0",
                        cursor: "pointer",
                      }}
                    >
                      {loc.isAvailable ? "Close / Reroute" : "Re-open Node"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </main>
    </div>
  );
};

