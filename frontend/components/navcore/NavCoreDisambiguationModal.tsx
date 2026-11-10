import React from "react";
import { Modal } from "../ui/Modal";
import { SAMPLE_DEPARTMENTS } from "../../lib/hospitalData";

export interface NavCoreDisambiguationOption {
  display: string;
  node_id: string;
}

interface DisambiguationModalProps {
  isOpen: boolean;
  onClose: () => void;
  query: string;
  options?: NavCoreDisambiguationOption[];
  question?: string | null;
  onSelectDepartment: (option: NavCoreDisambiguationOption) => void;
}

export const NavCoreDisambiguationModal: React.FC<DisambiguationModalProps> = ({
  isOpen,
  onClose,
  query,
  options,
  question,
  onSelectDepartment,
}) => {
  const choices = options?.length
    ? options
    : SAMPLE_DEPARTMENTS.slice(0, 4).map((department) => ({
        display: `${department.name} · ${department.room} · Floor ${department.floor}`,
        node_id: department.nodeId,
      }));

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Which department are you visiting?"
      subtitle={question || `We found multiple matches for "${query}". Please select one:`}
      maxWidth="600px"
    >
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "12px", marginTop: "16px" }}>
        {choices.map((option) => (
          <div
            key={option.node_id}
            onClick={() => {
              onSelectDepartment(option);
              onClose();
            }}
            style={{
              padding: "16px 20px",
              borderRadius: "14px",
              border: "1.5px solid #e5e5e0",
              backgroundColor: "#ffffff",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              transition: "all 0.15s ease",
            }}
          >
            <div>
              <div style={{ fontSize: "16px", fontWeight: 700, color: "#0f1410" }}>
                {option.display}
              </div>
            </div>
            <span
              style={{
                padding: "6px 14px",
                borderRadius: "9999px",
                backgroundColor: "#f0f7f2",
                color: "#2d5016",
                fontSize: "12px",
                fontWeight: 700,
              }}
            >
              Select ➔
            </span>
          </div>
        ))}
      </div>
    </Modal>
  );
};

