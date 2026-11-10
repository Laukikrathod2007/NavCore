import React, { useState } from "react";

interface UseCaseTab {
  id: string;
  label: string;
  icon: string;
  title: string;
  description: string;
  pills: string[];
  linkText: string;
  latency: string;
  query: string;
  response: string;
}

export const UseCasesSection: React.FC = () => {
  const tabs: UseCaseTab[] = [
    {
      id: "voice-navcore",
      label: "NavCore Voice",
      icon: "🎙️",
      title: "Real-time context, no awkward pauses",
      description:
        "Retrieve the right department, doctor room, and floor corridor in milliseconds so every patient interaction stays fluid and natural.",
      pills: ["Touchscreen NavCore", "Multilingual Voice", "Whisper Tiny"],
      linkText: "Build voice agents →",
      latency: "4ms",
      query: "dil ke doctor kahaan baithte hain?",
      response:
        "Cardiology OPD is on Floor 3, Room 312. Walk past reception, take Lift A to Floor 3, turn right at the nurse station.",
    },
    {
      id: "hospital-opd",
      label: "Hospital OPDs",
      icon: "🩺",
      title: "Colloquial speech to clinical signage",
      description:
        "Translates everyday slang like 'haddi ka doctor' or 'khoon test' into canonical clinic nodes with zero confusion.",
      pills: ["Doctor Rostering", "OPD Directory", "Dynamic Aliases"],
      linkText: "Explore hospital navigation →",
      latency: "6ms",
      query: "haddi wale doctor ka cabin kahan hai?",
      response:
        "Orthopedics OPD is on Floor 3, Room 324. Dr. Verma is on duty until 4:00 PM today.",
    },
    {
      id: "emergency",
      label: "Emergency & Triage",
      icon: "🚨",
      title: "Priority routing with zero cloud lag",
      description:
        "Instant deterministic path to emergency casualty, trauma bays, and resuscitation wards during critical incidents.",
      pills: ["Trauma Casualty", "Ambulance Bay", "Zero Wi-Fi Required"],
      linkText: "View emergency routing →",
      latency: "2ms",
      query: "emergency casualty fast",
      response:
        "Emergency Trauma Ward (ER-01) is located directly to your left on Ground Floor, 25 meters ahead.",
    },
    {
      id: "on-device",
      label: "On-Device Edge",
      icon: "💻",
      title: "Full retrieval power, zero cloud dependency",
      description:
        "Deploy NavCore locally for privacy-sensitive, offline, or latency-critical public physical spaces.",
      pills: ["Air-Gapped", "Basement Proof", "Zero API Bills"],
      linkText: "Deploy locally →",
      latency: "7ms",
      query: "रक्त तपासणी कुठे करायची?",
      response:
        "सेंट्रल पॅथॉलॉजी लॅब दुसऱ्या मजल्यावर खोली क्र. 220 मध्ये आहे. मुख्य लिफ्ट A ने दुसऱ्या मजल्यावर जा.",
    },
  ];

  const [activeTabId, setActiveTabId] = useState(tabs[0].id);
  const activeTab = tabs.find((t) => t.id === activeTabId) || tabs[0];

  return (
    <section
      id="use-cases"
      style={{
        padding: "80px 24px 90px",
        maxWidth: "1200px",
        margin: "0 auto",
      }}
    >
      {/* Header matching Screenshot 4 & 5 */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "24px",
          marginBottom: "36px",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "11px",
              fontFamily: "var(--font-mono, monospace)",
              letterSpacing: "1.5px",
              color: "#5c8a5c",
              textTransform: "uppercase",
              fontWeight: 600,
              marginBottom: "8px",
            }}
          >
            USE CASES
          </div>
          <h2
            style={{
              fontSize: "clamp(28px, 4vw, 42px)",
              fontWeight: 650,
              letterSpacing: "-0.03em",
              color: "#0f1410",
              margin: 0,
            }}
          >
            Built for real-time spatial applications
          </h2>
        </div>

        <p
          style={{
            fontSize: "15px",
            color: "#666666",
            maxWidth: "380px",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          For public physical systems where spatial retrieval is on the critical path and latency directly impacts human health.
        </p>
      </div>

      {/* Horizontal Tabs Bar matching Screenshot 4 & 5 */}
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #e5e5e0",
          marginBottom: "36px",
          overflowX: "auto",
        }}
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTabId;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTabId(tab.id)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "14px 24px",
                fontSize: "14px",
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "#0f1410" : "#666666",
                borderBottom: isActive ? "2px solid #5c8a5c" : "2px solid transparent",
                backgroundColor: "transparent",
                borderTop: "none",
                borderLeft: "none",
                borderRight: "none",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content Box matching Screenshot 4 & 5 */}
      <div
        style={{
          borderRadius: "20px",
          border: "1px solid #e5e5e0",
          backgroundColor: "#ffffff",
          padding: "48px 40px",
          display: "grid",
          gridTemplateColumns: "1fr 1.15fr",
          gap: "48px",
          alignItems: "center",
          boxShadow: "0 1px 4px rgba(0,0,0,0.03)",
        }}
        className="navcore-grid-mobile"
      >
        {/* Left Side: Copy & Pills */}
        <div>
          <h3
            style={{
              fontSize: "clamp(22px, 2.5vw, 28px)",
              fontWeight: 650,
              color: "#0f1410",
              letterSpacing: "-0.02em",
              marginBottom: "16px",
              lineHeight: 1.25,
            }}
          >
            {activeTab.title}
          </h3>
          <p
            style={{
              fontSize: "15px",
              color: "#666666",
              lineHeight: 1.6,
              marginBottom: "28px",
            }}
          >
            {activeTab.description}
          </p>

          {/* Sub-pills */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "36px" }}>
            {activeTab.pills.map((pill) => (
              <span
                key={pill}
                style={{
                  fontSize: "12px",
                  padding: "5px 12px",
                  borderRadius: "6px",
                  backgroundColor: "#f5f5f4",
                  color: "#525252",
                  fontWeight: 500,
                }}
              >
                {pill}
              </span>
            ))}
          </div>

          {/* Link */}
          <a
            href="#floor-map"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "14px",
              fontWeight: 600,
              color: "#2d5016",
              textDecoration: "none",
            }}
          >
            <span>{activeTab.linkText}</span>
          </a>
        </div>

        {/* Right Side: Dialogue Card with floating latency pill on mosaic backdrop (Screenshot 4 & 5) */}
        <div
          style={{
            position: "relative",
            borderRadius: "16px",
            overflow: "hidden",
            padding: "36px 32px",
            backgroundColor: "#f4faf6",
            border: "1px solid #d8ece0",
            minHeight: "260px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Subtle Mosaic Tiles Backdrop */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: 0.25,
              backgroundImage: "url('/assets/moss/mosaic-texture.svg')",
              backgroundSize: "cover",
            }}
          />

          {/* Chat Dialogue Card */}
          <div
            style={{
              position: "relative",
              zIndex: 2,
              backgroundColor: "#ffffff",
              borderRadius: "14px",
              border: "1px solid #e5e5e0",
              boxShadow: "0 10px 30px -5px rgba(0, 0, 0, 0.08)",
              padding: "24px 28px",
              width: "100%",
              maxWidth: "400px",
            }}
          >
            {/* User query bubble */}
            <div
              style={{
                fontSize: "13px",
                color: "#525252",
                backgroundColor: "#f5f5f4",
                padding: "10px 14px",
                borderRadius: "10px",
                marginBottom: "14px",
                fontStyle: "italic",
              }}
            >
              &ldquo;{activeTab.query}&rdquo;
            </div>

            {/* NavCore response bubble */}
            <div
              style={{
                fontSize: "14px",
                lineHeight: "1.5",
                color: "#0f1410",
                fontWeight: 500,
              }}
            >
              {activeTab.response}
            </div>
          </div>

          {/* Floating Mint Green Circular Latency Badge (Screenshot 4 & 5) */}
          <div
            style={{
              position: "absolute",
              right: "20px",
              bottom: "20px",
              zIndex: 3,
              width: "68px",
              height: "68px",
              borderRadius: "50%",
              backgroundColor: "#9fe6c8",
              boxShadow: "0 8px 24px rgba(45, 80, 22, 0.25)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#0f1410",
              fontWeight: 700,
              fontSize: "14px",
              animation: "mossScaleUp 0.3s ease",
            }}
          >
            <span style={{ fontSize: "11px", lineHeight: 1 }}>⚡</span>
            <span>{activeTab.latency}</span>
          </div>
        </div>
      </div>
    </section>
  );
};

