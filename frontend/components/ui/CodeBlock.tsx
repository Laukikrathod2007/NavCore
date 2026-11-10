import React, { useState } from "react";
import { CopyIcon, CheckIcon } from "./Icons";

export interface CodeBlockProps {
  code: string;
  language?: string;
  filename?: string;
  showLineNumbers?: boolean;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = "python",
  filename,
  showLineNumbers = true,
  className = "",
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  const lines = code.trim().split("\n");

  return (
    <div
      style={{
        borderRadius: "14px",
        backgroundColor: "#0d110e",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        overflow: "hidden",
        boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.5)",
        fontFamily: "var(--font-mono, ui-monospace, Menlo, Consolas, monospace)",
      }}
      className={className}
    >
      {/* Header bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 16px",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          backgroundColor: "#131714",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {/* Mac dots */}
          <div style={{ display: "flex", gap: "5px" }}>
            <span style={{ width: "9px", height: "9px", borderRadius: "50%", backgroundColor: "#ff5f56", display: "inline-block" }} />
            <span style={{ width: "9px", height: "9px", borderRadius: "50%", backgroundColor: "#ffbd2e", display: "inline-block" }} />
            <span style={{ width: "9px", height: "9px", borderRadius: "50%", backgroundColor: "#27c93f", display: "inline-block" }} />
          </div>
          {filename && (
            <span style={{ fontSize: "12px", color: "#8b949e", marginLeft: "8px" }}>
              {filename}
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "11px", color: "#5c8a5c", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            {language}
          </span>
          <button
            onClick={handleCopy}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              padding: "4px 8px",
              borderRadius: "6px",
              backgroundColor: "rgba(255, 255, 255, 0.08)",
              border: "1px solid rgba(255, 255, 255, 0.12)",
              color: copied ? "#05df72" : "#c9d1d9",
              fontSize: "12px",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            {copied ? <CheckIcon size={13} strokeWidth={2.5} /> : <CopyIcon size={13} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      </div>

      {/* Code body */}
      <pre
        style={{
          padding: "16px",
          margin: 0,
          overflowX: "auto",
          fontSize: "13px",
          lineHeight: "1.65",
          color: "#e6edf3",
        }}
      >
        <code>
          {lines.map((line, idx) => (
            <div key={idx} style={{ display: "flex" }}>
              {showLineNumbers && (
                <span
                  style={{
                    display: "inline-block",
                    width: "32px",
                    color: "#484f58",
                    userSelect: "none",
                    flexShrink: 0,
                    textAlign: "right",
                    paddingRight: "14px",
                  }}
                >
                  {idx + 1}
                </span>
              )}
              <span style={{ flex: 1 }}>{line}</span>
            </div>
          ))}
        </code>
      </pre>
    </div>
  );
};

