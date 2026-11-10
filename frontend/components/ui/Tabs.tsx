import React from "react";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

export interface TabsProps {
  items: TabItem[];
  activeId: string;
  onChange: (id: string) => void;
  variant?: "pill" | "underline" | "navcore";
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  items,
  activeId,
  onChange,
  variant = "pill",
  className = "",
}) => {
  if (variant === "navcore") {
    return (
      <div
        style={{
          display: "flex",
          gap: "8px",
          backgroundColor: "#f5f5f4",
          padding: "6px",
          borderRadius: "16px",
          border: "1px solid #e5e5e0",
          overflowX: "auto",
        }}
        className={className}
      >
        {items.map((tab) => {
          const isActive = tab.id === activeId;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 20px",
                borderRadius: "12px",
                fontSize: "16px",
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "#ffffff" : "#525252",
                backgroundColor: isActive ? "#0f1410" : "transparent",
                border: "none",
                cursor: "pointer",
                transition: "all 0.15s ease",
                whiteSpace: "nowrap",
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span
                  style={{
                    backgroundColor: isActive ? "rgba(255, 255, 255, 0.2)" : "#e5e5e0",
                    padding: "2px 6px",
                    borderRadius: "6px",
                    fontSize: "12px",
                  }}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        backgroundColor: "#f5f5f4",
        padding: "3px",
        borderRadius: "9999px",
        border: "1px solid #e5e5e0",
      }}
      className={className}
    >
      {items.map((tab) => {
        const isActive = tab.id === activeId;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 14px",
              borderRadius: "9999px",
              fontSize: "13px",
              fontWeight: isActive ? 600 : 450,
              color: isActive ? "#0f1410" : "#737373",
              backgroundColor: isActive ? "#ffffff" : "transparent",
              boxShadow: isActive ? "0 1px 2px rgba(0, 0, 0, 0.05)" : "none",
              border: "none",
              cursor: "pointer",
              transition: "all 0.15s ease",
              userSelect: "none",
              whiteSpace: "nowrap",
            }}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span
                style={{
                  fontSize: "11px",
                  padding: "1px 6px",
                  borderRadius: "9999px",
                  backgroundColor: isActive ? "#f0f7f2" : "rgba(0,0,0,0.06)",
                  color: isActive ? "#2d5016" : "#737373",
                  fontWeight: 600,
                }}
              >
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

