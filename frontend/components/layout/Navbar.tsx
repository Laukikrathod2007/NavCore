import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRightIcon } from "../ui/Icons";
import { publicAsset } from "../../lib/urls";

interface NavbarProps {
  onOpenNavCore?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenNavCore }) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* Product status announcement */}
      <div
        className="marketing-announcement"
        style={{
          backgroundColor: "#f7fcf9",
          borderBottom: "1px solid #e2f1e8",
          padding: "8px 24px",
          textAlign: "center",
          fontSize: "13px",
          color: "#2d5016",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          fontWeight: 500,
        }}
      >
        <span
          style={{
            backgroundColor: "#fef9c3",
            color: "#854d0e",
            fontSize: "10px",
            fontWeight: 700,
            padding: "2px 6px",
            borderRadius: "4px",
            letterSpacing: "0.5px",
          }}
        >
          NEW
        </span>
        <span>NavCore v2.4 Offline Spatial RAG is live</span>
        <span style={{ color: "#abe6c7" }}>|</span>
        <a
          href="#benchmark"
          style={{
            color: "#2d5016",
            textDecoration: "none",
            fontWeight: 600,
            display: "inline-flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          <span>View Hospital Benchmarks</span>
          <span>→</span>
        </a>
      </div>

      {/* Main Sticky Navbar */}
      <header
        className="marketing-nav"
        style={{
          position: "sticky",
          top: 0,
          zIndex: 100,
          width: "100%",
          backgroundColor: scrolled ? "rgba(255, 255, 255, 0.94)" : "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid #e5e5e0",
          transition: "all 0.2s ease",
        }}
      >
        <div
          className="marketing-nav-inner"
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "16px 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          {/* Brand Logo & Wordmark */}
          <Link href="/" className="brand-lockup" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
            <img
              src={publicAsset("/assets/brand/navcore-emblem-icon.png")}
              alt="NavCore"
              width="32"
              height="32"
              style={{ borderRadius: "8px" }}
            />
            <span style={{ fontSize: "20px", fontWeight: 700, color: "#0f1410", letterSpacing: "-0.03em" }}>
              Nav<span style={{ color: "#2d5016" }}>Core</span>
            </span>
          </Link>

          {/* Navigation links (like moss.dev screenshot) */}
          <nav style={{ display: "flex", alignItems: "center", gap: "32px" }} className="nav-links">
            <a href="#dual-memory" style={navLinkStyle}>PRODUCT</a>
            <a href="#use-cases" style={navLinkStyle}>USE CASES</a>
            <a href="#benchmark" style={navLinkStyle}>BENCHMARKS</a>
            <a href="#floor-map" style={navLinkStyle}>FACILITY MAP</a>
            <Link href="/admin" style={navLinkStyle}>ADMIN</Link>
          </nav>

          {/* Actions: Start Free / Launch NavCore Button */}
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <Link href="/navcore" className="nav-launch" style={{ textDecoration: "none" }}>
              <button
                onClick={onOpenNavCore}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "9px 20px",
                  borderRadius: "9999px",
                  backgroundColor: "#9fe6c8",
                  color: "#0f1410",
                  fontSize: "14px",
                  fontWeight: 600,
                  border: "none",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#85e0ba")}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#9fe6c8")}
              >
                <span>Launch NavCore</span>
                <span style={{ fontSize: "15px" }}>→</span>
              </button>
            </Link>
          </div>
        </div>
      </header>
    </>
  );
};

const navLinkStyle: React.CSSProperties = {
  fontSize: "13px",
  fontWeight: 550,
  letterSpacing: "0",
  color: "#525252",
  textDecoration: "none",
  transition: "color 0.15s ease",
  cursor: "pointer",
};
