import React from "react";
import { Badge } from "../ui/Badge";

export interface SectionHeaderProps {
  badge?: string;
  title: string | React.ReactNode;
  description?: string | React.ReactNode;
  align?: "left" | "center";
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  badge,
  title,
  description,
  align = "center",
  className = "",
}) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: align === "center" ? "center" : "flex-start",
        textAlign: align === "center" ? "center" : "left",
        maxWidth: align === "center" ? "740px" : "100%",
        margin: align === "center" ? "0 auto 48px auto" : "0 0 36px 0",
      }}
      className={className}
    >
      {badge && (
        <div style={{ marginBottom: "16px" }}>
          <Badge variant="moss" size="md">
            {badge}
          </Badge>
        </div>
      )}
      <h2
        style={{
          fontSize: "clamp(28px, 4vw, 42px)",
          fontWeight: 600,
          lineHeight: 1.18,
          letterSpacing: "-0.03em",
          color: "#0f1410",
          margin: "0 0 16px 0",
        }}
      >
        {title}
      </h2>
      {description && (
        <p
          style={{
            fontSize: "17px",
            lineHeight: 1.6,
            color: "#525252",
            margin: 0,
            maxWidth: "640px",
          }}
        >
          {description}
        </p>
      )}
    </div>
  );
};

