import React from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { ShieldCheckIcon, MicIcon, QrCodeIcon, ZapIcon, HospitalIcon } from "../ui/Icons";

export const BentoFeatures: React.FC = () => {
  return (
    <section style={{ padding: "90px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="PHYSICAL INFRASTRUCTURE FIRST"
        title={
          <>
            Built for chaotic, <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>high-density public spaces</span>
          </>
        }
        description="Physical navigation has constraints cloud software ignores: dead Wi-Fi zones, illiterate patients, crowded corridors, and shifting doctor OPD rotas."
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 1fr)",
          gap: "20px",
        }}
      >
        {/* Card 1: 100% Air-gapped (Large 7 col) */}
        <div style={{ gridColumn: "span 7" }} className="bento-col-12-mobile">
          <Card hoverEffect variant="moss" style={{ height: "100%", padding: "32px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
                <span style={{ width: "38px", height: "38px", borderRadius: "10px", backgroundColor: "#2d5016", color: "#ffffff", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <ShieldCheckIcon size={20} />
                </span>
                <Badge variant="dark" size="sm">Zero Cloud Dependencies</Badge>
              </div>
              <h3 style={{ fontSize: "24px", fontWeight: 700, color: "#0f1410", marginBottom: "12px" }}>
                100% Offline &amp; Air-Gapped Ready
              </h3>
              <p style={{ fontSize: "15px", lineHeight: "1.6", color: "#223d11", margin: 0 }}>
                NavCore requires zero internet connection, zero Bluetooth beacons, and zero monthly cloud API bills. Vectors live locally in Qdrant Edge, graph paths in memory, and LLM inferences in Ollama. Operates during power cuts, network blackouts, and underground basements.
              </p>
            </div>
            <div style={{ marginTop: "24px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <span style={{ fontSize: "12px", padding: "4px 10px", borderRadius: "6px", backgroundColor: "#ffffff", color: "#2d5016", fontWeight: 600 }}>
                • No Pinecone / OpenAI bills
              </span>
              <span style={{ fontSize: "12px", padding: "4px 10px", borderRadius: "6px", backgroundColor: "#ffffff", color: "#2d5016", fontWeight: 600 }}>
                • Zero patient PHI privacy leaks
              </span>
            </div>
          </Card>
        </div>

        {/* Card 2: Multilingual Voice (5 col) */}
        <div style={{ gridColumn: "span 5" }} className="bento-col-12-mobile">
          <Card hoverEffect variant="default" style={{ height: "100%", padding: "32px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <span style={{ width: "38px", height: "38px", borderRadius: "10px", backgroundColor: "#f0f7f2", color: "#2d5016", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <MicIcon size={20} />
              </span>
              <Badge variant="moss" size="sm">Whisper Tiny ASR</Badge>
            </div>
            <h3 style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410", marginBottom: "10px" }}>
              Multilingual Voice Input
            </h3>
            <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#525252", margin: "0 0 16px 0" }}>
              Elderly or semi-literate patients tap the mic button and speak naturally: &ldquo;dil ke doctor&rdquo; or &ldquo;रक्त तपासणी कुठे करायची&rdquo;. Whisper Tiny transcribes locally in 1.2s.
            </p>
            <div style={{ backgroundColor: "#fafafa", padding: "10px 14px", borderRadius: "8px", border: "1px solid #e5e5e0", fontSize: "12px", color: "#0f1410", fontStyle: "italic" }}>
              &ldquo;haddi ka doctor kahan milega&rdquo; → Orthopedic OPD (Floor 3)
            </div>
          </Card>
        </div>

        {/* Card 3: QR Transfer (4 col) */}
        <div style={{ gridColumn: "span 4" }} className="bento-col-12-mobile">
          <Card hoverEffect variant="default" style={{ height: "100%", padding: "28px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <span style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: "#f5f5f4", color: "#0f1410", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <QrCodeIcon size={18} />
              </span>
              <Badge variant="neutral" size="sm">No App Download</Badge>
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410", marginBottom: "8px" }}>
              QR Navigation Handoff
            </h3>
            <p style={{ fontSize: "13px", lineHeight: "1.6", color: "#525252", margin: 0 }}>
              Patients scan a QR code displayed on the NavCore screen to transfer the computed path directly onto their smartphone browser — no app store install needed.
            </p>
          </Card>
        </div>

        {/* Card 4: Dynamic Admin Telemetry (4 col) */}
        <div style={{ gridColumn: "span 4" }} className="bento-col-12-mobile">
          <Card hoverEffect variant="default" style={{ height: "100%", padding: "28px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <span style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: "#f5f5f4", color: "#0f1410", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <HospitalIcon size={18} />
              </span>
              <Badge variant="neutral" size="sm">WebSocket Live Sync</Badge>
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410", marginBottom: "8px" }}>
              Live Hospital Operations
            </h3>
            <p style={{ fontSize: "13px", lineHeight: "1.6", color: "#525252", margin: 0 }}>
              Staff toggle doctor duty status, close corridors for sanitation, or mark lifts under maintenance. NavCore instantly recalculates alternate accessible routes.
            </p>
          </Card>
        </div>

        {/* Card 5: Sub-10ms Hot-Path (4 col) */}
        <div style={{ gridColumn: "span 4" }} className="bento-col-12-mobile">
          <Card hoverEffect variant="default" style={{ height: "100%", padding: "28px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <span style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: "#f0f7f2", color: "#2d5016", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <ZapIcon size={18} />
              </span>
              <Badge variant="moss" size="sm">Sub-10ms Retrieval</Badge>
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410", marginBottom: "8px" }}>
              Hot-Path Determinism
            </h3>
            <p style={{ fontSize: "13px", lineHeight: "1.6", color: "#525252", margin: 0 }}>
              While traditional cloud vector databases require 800-2,400ms network round-trips, NavCore computes vector similarity and BFS graphs in under 12ms locally.
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
};

