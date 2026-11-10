import React, { useState } from "react";
import Link from "next/link";

export const FloatingAgentPill: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="floating-agent"
      style={{
        position: "fixed",
        bottom: "24px",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 999,
      }}
    >
      <Link href="/navcore" style={{ textDecoration: "none" }}>
        <button
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "10px",
            padding: "10px 22px",
            borderRadius: "9999px",
            backgroundColor: isHovered ? "#f7fcf9" : "#ffffff",
            color: "#0f1410",
            border: isHovered ? "1.5px solid #5c8a5c" : "1.5px solid #d0d0c8",
            boxShadow: "0 8px 30px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.04)",
            cursor: "pointer",
            transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
            fontFamily: "var(--font-mono, monospace)",
            fontSize: "13px",
            fontWeight: 600,
          }}
        >
          {/* Mosaic circle avatar matching screenshot */}
          <span
            style={{
              width: "22px",
              height: "22px",
              borderRadius: "50%",
              overflow: "hidden",
              display: "inline-block",
              position: "relative",
            }}
          >
            <img
              src="/assets/brand/navcore-emblem-icon.png"
              alt="NavCore"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </span>

          <span style={{ color: "#0f1410" }}>Talk to NavCore Agent</span>

          <span style={{ fontSize: "14px", color: "#2d5016" }}>🎙️</span>
        </button>
      </Link>
    </div>
  );
};

