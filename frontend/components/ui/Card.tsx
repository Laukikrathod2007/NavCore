import React, { useState } from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "subtle" | "moss" | "dark" | "interactive";
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = "default",
  hoverEffect = false,
  style,
  className = "",
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case "subtle":
        return {
          backgroundColor: "#fbfbfa",
          border: "1px solid #e5e5e0",
          color: "#0f1410",
        };
      case "moss":
        return {
          backgroundColor: "#f0f7f2",
          border: "1px solid #abe6c7",
          color: "#0f1410",
        };
      case "dark":
        return {
          backgroundColor: "#0f1410",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          color: "#ffffff",
        };
      case "interactive":
      case "default":
      default:
        return {
          backgroundColor: "#ffffff",
          border: isHovered && hoverEffect ? "1px solid #5c8a5c" : "1px solid #e5e5e0",
          boxShadow: isHovered && hoverEffect
            ? "0 12px 32px -8px rgba(0, 0, 0, 0.08), 0 2px 8px -2px rgba(0, 0, 0, 0.04)"
            : "0 1px 3px rgba(0, 0, 0, 0.04), 0 6px 16px -4px rgba(0, 0, 0, 0.02)",
          color: "#0f1410",
        };
    }
  };

  return (
    <div
      {...props}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        borderRadius: "16px",
        padding: "24px",
        transition: "all 0.22s cubic-bezier(0.16, 1, 0.3, 1)",
        transform: isHovered && hoverEffect ? "translateY(-2px)" : "none",
        position: "relative",
        overflow: "hidden",
        ...getVariantStyles(),
        ...style,
      }}
      className={className}
    >
      {children}
    </div>
  );
};

