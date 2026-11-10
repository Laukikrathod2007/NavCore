import React from "react";
import { publicAsset } from "../../lib/urls";

export const TrustBar: React.FC = () => {
  const hospitalPartners = [
    { name: "AIIMS New Delhi", tag: "Apex Institute" },
    { name: "Apollo Hospitals", tag: "Multi-Specialty" },
    { name: "Max Healthcare", tag: "Regional Health" },
    { name: "Tata Memorial Centre", tag: "Oncology Care" },
    { name: "Fortis Healthcare", tag: "Super Specialty" },
    { name: "NIMHANS Bengaluru", tag: "Neurosciences" },
  ];

  const mossLogos = [
    { src: publicAsset("/assets/moss/microsoft.svg"), alt: "Microsoft", height: 20 },
    { src: publicAsset("/assets/moss/berkeley.svg"), alt: "UC Berkeley", height: 22 },
    { src: publicAsset("/assets/moss/stanford.svg"), alt: "Stanford", height: 24 },
    { src: publicAsset("/assets/moss/cmu.svg"), alt: "CMU", height: 20 },
    { src: publicAsset("/assets/moss/langchain.svg"), alt: "LangChain", height: 22 },
    { src: publicAsset("/assets/moss/nextjs.svg"), alt: "Next.js", height: 18 },
  ];

  return (
    <section
      className="trust-section"
      style={{
        borderTop: "1px solid #f0f0ec",
        borderBottom: "1px solid #f0f0ec",
        backgroundColor: "#fbfbfa",
        padding: "48px 24px",
      }}
    >
      <div style={{ maxWidth: "1200px", margin: "0 auto", textAlign: "center" }}>
        {/* Eyebrow */}
        <p
          style={{
            fontSize: "12px",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "1px",
            color: "#888888",
            marginBottom: "28px",
          }}
        >
          Engineered for high-throughput public hospitals & NavCore edge infrastructure
        </p>

        {/* Hospital badges */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "24px",
            flexWrap: "wrap",
            marginBottom: "36px",
          }}
        >
          {hospitalPartners.map((hosp) => (
            <div
              key={hosp.name}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 16px",
                borderRadius: "10px",
                backgroundColor: "#ffffff",
                border: "1px solid #e5e5e0",
                fontSize: "13px",
                fontWeight: 600,
                color: "#2b2b2b",
                boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
              }}
            >
              <span style={{ color: "#2d5016" }}>🏥</span>
              <span>{hosp.name}</span>
              <span style={{ fontSize: "10px", color: "#888888", fontWeight: 400 }}>
                • {hosp.tag}
              </span>
            </div>
          ))}
        </div>

        {/* Moss Research & Technology Stack Logos */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "40px",
            flexWrap: "wrap",
            opacity: 0.75,
            filter: "grayscale(100%)",
            transition: "opacity 0.2s ease",
          }}
        >
          {mossLogos.map((logo, idx) => (
            <img
              key={idx}
              src={logo.src}
              alt={logo.alt}
              style={{ height: `${logo.height}px`, objectFit: "contain", maxWidth: "110px" }}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

