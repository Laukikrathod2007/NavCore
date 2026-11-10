import React from "react";

export interface MetricPillProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  trend?: string;
  color?: "moss" | "dark" | "blue" | "neutral";
}

export const MetricPill: React.FC<MetricPillProps> = ({
  label,
  value,
  unit,
  subtext,
  trend,
  color = "moss",
}) => {
  const colorMap = {
    moss: { border: "#abe6c7", bg: "#f0f7f2", text: "#2d5016" },
    dark: { border: "#0f1410", bg: "#0f1410", text: "#ffffff" },
    blue: { border: "#bfdbfe", bg: "#eff6ff", text: "#1d4ed8" },
    neutral: { border: "#e5e5e0", bg: "#fafafa", text: "#0f1410" },
  }[color];

  return (
    <div
      style={{
        display: "inline-flex",
        flexDirection: "column",
        padding: "16px 20px",
        borderRadius: "14px",
        backgroundColor: colorMap.bg,
        border: `1px solid ${colorMap.border}`,
        minWidth: "140px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
        <span style={{ fontSize: "12px", color: color === "dark" ? "#a1a1aa" : "#737373", fontWeight: 500 }}>
          {label}
        </span>
        {trend && (
          <span style={{ fontSize: "11px", fontWeight: 600, color: "#00a544", backgroundColor: "rgba(0, 165, 68, 0.1)", padding: "1px 6px", borderRadius: "9999px" }}>
            {trend}
          </span>
        )}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
        <span style={{ fontSize: "28px", fontWeight: 700, letterSpacing: "-0.03em", color: colorMap.text }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: "13px", fontWeight: 500, color: color === "dark" ? "#a1a1aa" : "#737373" }}>
            {unit}
          </span>
        )}
      </div>
      {subtext && (
        <span style={{ fontSize: "11px", color: color === "dark" ? "#71717a" : "#888888", marginTop: "4px" }}>
          {subtext}
        </span>
      )}
    </div>
  );
};

