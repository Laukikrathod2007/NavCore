import React from "react";
import { AnimatedNumber } from "../ui/AnimatedNumber";

export const StatsCounterSection: React.FC = () => {
  return (
    <section
      className="metrics-section"
      style={{
        padding: "80px 24px 60px",
        maxWidth: "1200px",
        margin: "0 auto",
      }}
    >
      <div style={{ textAlign: "center", marginBottom: "48px" }}>
        <h2
          style={{
            fontSize: "clamp(28px, 3.5vw, 42px)",
            fontWeight: 650,
            letterSpacing: "-0.03em",
            color: "#0f1410",
            margin: 0,
          }}
        >
          Built for real-time spatial navigation at scale
        </h2>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "24px",
        }}
      >
        {/* Card 1: <10 ms */}
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "16px",
            border: "1px solid #e5e5e0",
            padding: "36px 32px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
          }}
        >
          <div
            style={{
              fontSize: "clamp(44px, 4.5vw, 60px)",
              fontWeight: 700,
              letterSpacing: "-0.04em",
              color: "#0f1410",
              lineHeight: 1,
              marginBottom: "16px",
            }}
          >
            &lt;<AnimatedNumber target={10} duration={1200} /> ms
          </div>
          <h3
            style={{
              fontSize: "19px",
              fontWeight: 600,
              color: "#0f1410",
              marginBottom: "8px",
            }}
          >
            End-to-end hot-path retrieval
          </h3>
          <p
            style={{
              fontSize: "14px",
              color: "#666666",
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            Up to 150x faster than cloud vector DBs. 0ms network round-trip delay.
          </p>
        </div>

        {/* Card 2: 76% Destination Accuracy */}
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "16px",
            border: "1px solid #e5e5e0",
            padding: "36px 32px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
          }}
        >
          <div
            style={{
              fontSize: "clamp(44px, 4.5vw, 60px)",
              fontWeight: 700,
              letterSpacing: "-0.04em",
              color: "#0f1410",
              lineHeight: 1,
              marginBottom: "16px",
            }}
          >
            <AnimatedNumber target={76} duration={1500} suffix="%" />
          </div>
          <h3
            style={{
              fontSize: "19px",
              fontWeight: 600,
              color: "#0f1410",
              marginBottom: "8px",
            }}
          >
            Destination accuracy
          </h3>
          <p
            style={{
              fontSize: "14px",
              color: "#666666",
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            Tested across 200 real patient queries in Hindi, Marathi, Hinglish, &amp; English.
          </p>
        </div>

        {/* Card 3: 100% Local Execution */}
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "16px",
            border: "1px solid #e5e5e0",
            padding: "36px 32px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
          }}
        >
          <div
            style={{
              fontSize: "clamp(44px, 4.5vw, 60px)",
              fontWeight: 700,
              letterSpacing: "-0.04em",
              color: "#0f1410",
              lineHeight: 1,
              marginBottom: "16px",
            }}
          >
            <AnimatedNumber target={100} duration={1300} suffix="%" />
          </div>
          <h3
            style={{
              fontSize: "19px",
              fontWeight: 600,
              color: "#0f1410",
              marginBottom: "8px",
            }}
          >
            Local edge execution
          </h3>
          <p
            style={{
              fontSize: "14px",
              color: "#666666",
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            Index and query offline with zero external vector DB or cloud Wi-Fi required.
          </p>
        </div>
      </div>
    </section>
  );
};

