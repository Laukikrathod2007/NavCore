import React, { useEffect } from "react";
import { CloseIcon } from "./Icons";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  maxWidth?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = "520px",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        backgroundColor: "rgba(15, 20, 16, 0.6)",
        backdropFilter: "blur(6px)",
        animation: "mossFadeIn 0.2s ease-out",
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth,
          backgroundColor: "#ffffff",
          borderRadius: "20px",
          border: "1px solid #e5e5e0",
          boxShadow: "0 24px 60px -12px rgba(0, 0, 0, 0.25)",
          padding: "28px",
          position: "relative",
          animation: "mossScaleUp 0.22s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
          <div>
            <h3 style={{ fontSize: "20px", fontWeight: 700, letterSpacing: "-0.02em", color: "#0f1410", margin: 0 }}>
              {title}
            </h3>
            {subtitle && (
              <p style={{ fontSize: "14px", color: "#737373", margin: "4px 0 0 0" }}>
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#f5f5f4",
              border: "none",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: "#525252",
            }}
          >
            <CloseIcon size={16} />
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
};

