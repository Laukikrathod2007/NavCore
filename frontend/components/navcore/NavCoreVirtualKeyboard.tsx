import React from "react";

interface VirtualKeyboardProps {
  onKeyPress: (char: string) => void;
  onBackspace: () => void;
  onClear: () => void;
  onSubmit: () => void;
  language?: "en" | "hi";
}

export const NavCoreVirtualKeyboard: React.FC<VirtualKeyboardProps> = ({
  onKeyPress,
  onBackspace,
  onClear,
  onSubmit,
  language = "en",
}) => {
  const enRows = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M"],
  ];

  return (
    <div
      style={{
        backgroundColor: "#131714",
        borderRadius: "16px",
        padding: "16px",
        boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
        maxWidth: "760px",
        margin: "16px auto 0",
        userSelect: "none",
      }}
    >
      {enRows.map((row, rIdx) => (
        <div
          key={rIdx}
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "8px",
            marginBottom: "8px",
          }}
        >
          {row.map((char) => (
            <button
              key={char}
              onClick={() => onKeyPress(char.toLowerCase())}
              style={{
                width: "56px",
                height: "52px",
                borderRadius: "10px",
                backgroundColor: "#1f2620",
                color: "#ffffff",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                fontSize: "18px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                transition: "all 0.1s ease",
              }}
            >
              {char}
            </button>
          ))}
        </div>
      ))}

      {/* Bottom control row */}
      <div style={{ display: "flex", justifyContent: "center", gap: "10px", marginTop: "8px" }}>
        <button
          onClick={onClear}
          style={{
            padding: "0 20px",
            height: "52px",
            borderRadius: "10px",
            backgroundColor: "#2e1e1e",
            color: "#ff6568",
            border: "1px solid rgba(255, 100, 100, 0.2)",
            fontSize: "15px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Clear
        </button>

        <button
          onClick={() => onKeyPress(" ")}
          style={{
            flex: 1,
            maxWidth: "340px",
            height: "52px",
            borderRadius: "10px",
            backgroundColor: "#1f2620",
            color: "#ffffff",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            fontSize: "16px",
            fontWeight: 500,
            cursor: "pointer",
          }}
        >
          Space
        </button>

        <button
          onClick={onBackspace}
          style={{
            padding: "0 22px",
            height: "52px",
            borderRadius: "10px",
            backgroundColor: "#2a2f2b",
            color: "#ffffff",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            fontSize: "15px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          ⌫ Back
        </button>

        <button
          onClick={onSubmit}
          style={{
            padding: "0 28px",
            height: "52px",
            borderRadius: "10px",
            backgroundColor: "#2d5016",
            color: "#ffffff",
            border: "1px solid #5c8a5c",
            fontSize: "16px",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Find Room ➔
        </button>
      </div>
    </div>
  );
};

