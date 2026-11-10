import React from "react";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: "moss" | "neutral" | "dark" | "outline" | "warning";
  pulse?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "moss",
  pulse = false,
  size = "md",
  className = "",
  onClick,
}) => {
  const sizeStyles = {
    sm: { padding: "2px 8px", fontSize: "11px" },
    md: { padding: "4px 12px", fontSize: "12px" },
    lg: { padding: "6px 16px", fontSize: "14px" },
  }[size];

  const variantStyles: Record<string, React.CSSProperties> = {
    moss: {
      backgroundColor: "#f0f7f2",
      color: "#2d5016",
      border: "1px solid #abe6c7",
    },
    neutral: {
      backgroundColor: "#f5f5f4",
      color: "#525252",
      border: "1px solid #e5e5e0",
    },
    dark: {
      backgroundColor: "#0f1410",
      color: "#ffffff",
      border: "1px solid rgba(255, 255, 255, 0.15)",
    },
    outline: {
      backgroundColor: "transparent",
      color: "#0f1410",
      border: "1px solid #e5e5e0",
    },
    warning: {
      backgroundColor: "#fffbeb",
      color: "#b45309",
      border: "1px solid #fde68a",
    },
  };

  return (
    <span
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        borderRadius: "9999px",
        fontWeight: 500,
        letterSpacing: "-0.01em",
        lineHeight: 1.3,
        cursor: onClick ? "pointer" : "default",
        userSelect: "none",
        ...sizeStyles,
        ...variantStyles[variant],
      }}
      className={className}
    >
      {pulse && (
        <span
          style={{
            position: "relative",
            display: "inline-flex",
            width: "6px",
            height: "6px",
          }}
        >
          <span
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              borderRadius: "50%",
              backgroundColor: "#05df72",
              opacity: 0.75,
              animation: "mossPing 1.5s cubic-bezier(0, 0, 0.2, 1) infinite",
            }}
          />
          <span
            style={{
              position: "relative",
              display: "inline-block",
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "#00a544",
            }}
          />
        </span>
      )}
      {children}
    </span>
  );
};

