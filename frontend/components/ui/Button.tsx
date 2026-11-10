import React, { useState } from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "moss" | "secondary" | "outline" | "ghost" | "navcore";
  size?: "sm" | "md" | "lg" | "touch";
  icon?: React.ReactNode;
  iconRight?: React.ReactNode;
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  icon,
  iconRight,
  loading = false,
  disabled,
  style,
  onClick,
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isActive, setIsActive] = useState(false);

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { height: "32px", padding: "0 12px", fontSize: "13px", gap: "6px" },
    md: { height: "40px", padding: "0 18px", fontSize: "14px", gap: "8px" },
    lg: { height: "48px", padding: "0 24px", fontSize: "15px", gap: "10px" },
    touch: { height: "58px", padding: "0 28px", fontSize: "18px", gap: "12px", fontWeight: 600 },
  };

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case "moss":
        return {
          backgroundColor: isHovered ? "#223d11" : "#2d5016",
          color: "#ffffff",
          border: "1px solid #223d11",
          boxShadow: "0 1px 2px rgba(0, 0, 0, 0.08)",
        };
      case "secondary":
      case "outline":
        return {
          backgroundColor: isHovered ? "#f7f7f6" : "#ffffff",
          color: "#0f1410",
          border: isHovered ? "1px solid #d0d0c8" : "1px solid #e5e5e0",
          boxShadow: "0 1px 2px rgba(0, 0, 0, 0.04)",
        };
      case "ghost":
        return {
          backgroundColor: isHovered ? "rgba(0, 0, 0, 0.05)" : "transparent",
          color: "#0f1410",
          border: "1px solid transparent",
        };
      case "navcore":
        return {
          backgroundColor: isHovered ? "#1a251b" : "#0f1410",
          color: "#ffffff",
          border: "2px solid #5c8a5c",
          boxShadow: "0 8px 24px -6px rgba(45, 80, 22, 0.3)",
          borderRadius: "16px",
        };
      case "primary":
      default:
        return {
          backgroundColor: isHovered ? "#262b24" : "#0f1410",
          color: "#ffffff",
          border: "1px solid #0f1410",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.08)",
        };
    }
  };

  return (
    <button
      {...props}
      disabled={disabled || loading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setIsActive(false);
      }}
      onMouseDown={() => setIsActive(true)}
      onMouseUp={() => setIsActive(false)}
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: variant === "navcore" ? "16px" : "9999px",
        fontWeight: 500,
        letterSpacing: "-0.01em",
        cursor: disabled || loading ? "not-allowed" : "pointer",
        opacity: disabled ? 0.6 : 1,
        transition: "all 0.18s cubic-bezier(0.16, 1, 0.3, 1)",
        transform: isActive && !disabled ? "scale(0.98)" : isHovered && !disabled ? "translateY(-1px)" : "none",
        outline: "none",
        userSelect: "none",
        whiteSpace: "nowrap",
        ...sizeStyles[size],
        ...getVariantStyles(),
        ...style,
      }}
    >
      {loading ? (
        <span
          style={{
            display: "inline-block",
            width: "16px",
            height: "16px",
            border: "2px solid rgba(255, 255, 255, 0.3)",
            borderTopColor: "#ffffff",
            borderRadius: "50%",
            animation: "mossSpin 0.7s linear infinite",
          }}
        />
      ) : (
        icon
      )}
      <span>{children}</span>
      {!loading && iconRight}
    </button>
  );
};

