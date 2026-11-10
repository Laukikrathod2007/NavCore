import React, { useState } from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";

interface WorkflowNode {
  step: number;
  id: string;
  name: string;
  role: string;
  technology: string;
  input: string;
  output: string;
  latencyBudget: string;
}

export const WorkflowPipeline: React.FC = () => {
  const nodes: WorkflowNode[] = [
    {
      step: 1,
      id: "input_processor",
      name: "Input Processor",
      role: "Normalizes raw text, resolves start location from QR code or NavCore anchor.",
      technology: "Python Regex / Heuristics",
      input: "Raw query string + optional location cookie",
      output: "Normalized query text + current_node ('main_entrance')",
      latencyBudget: "<1ms",
    },
    {
      step: 2,
      id: "language_detector",
      name: "Language Detector",
      role: "Detects Hindi, Marathi, Hinglish, or English using Unicode script and vocabulary heuristics.",
      technology: "Regex script ranges (0x0900-0x097F) + word tokens",
      input: "Normalized query string",
      output: "Language code ('hi' | 'mr' | 'hi-mix' | 'en')",
      latencyBudget: "<2ms",
    },
    {
      step: 3,
      id: "intent_classifier",
      name: "Intent Classifier",
      role: "Classifies whether patient wants to locate department, get turn-by-turn route, or ask doctor timings.",
      technology: "Rule-based & lightweight vector intent filter",
      input: "Query + language",
      output: "Intent ('navigate' | 'locate' | 'doctor_timing')",
      latencyBudget: "<3ms",
    },
    {
      step: 4,
      id: "retrieval",
      name: "Semantic Vector Retrieval",
      role: "Matches query embedding against 104 department alias vectors using Cosine similarity.",
      technology: "Qdrant Edge + multilingual-e5-small (384-dim)",
      input: "Query embedding vector",
      output: "Candidate nodes with similarity scores (e.g. cardiology_opd: 0.89)",
      latencyBudget: "10-15ms",
    },
    {
      step: 5,
      id: "disambiguation",
      name: "Disambiguation Gate",
      role: "Detects ambiguous requests (e.g. 'doctor' without specialty or top score gap < 0.08).",
      technology: "Score margin logic & branch routing",
      input: "Top-k retrieval scores",
      output: "Single canonical target OR disambiguation prompt options",
      latencyBudget: "<1ms",
    },
    {
      step: 6,
      id: "path_planner",
      name: "Topological Path Planner",
      role: "Computes deterministic multi-floor shortest path from patient's current node to target room.",
      technology: "NetworkX Breadth-First Search (BFS)",
      input: "Start node ('main_entrance'), Target node ('cardiology_opd')",
      output: "Ordered list of graph node IDs across floors",
      latencyBudget: "<1ms",
    },
    {
      step: 7,
      id: "direction_generator",
      name: "Edge Direction Generator",
      role: "Translates the verified topological path into fluent natural directions with landmarks.",
      technology: "Llama 3.2 3B via Ollama Edge",
      input: "Path nodes + landmark context + patient language",
      output: "Fluent turn-by-turn instructions in Hindi/Marathi/English",
      latencyBudget: "300-350ms",
    },
  ];

  const [activeStep, setActiveStep] = useState(nodes[3]);

  return (
    <section id="langgraph" className="workflow-section" style={{ padding: "90px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="LANGGRAPH AGENT WORKFLOW"
        title={
          <>
            Deterministic 7-Node <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>Edge Pipeline</span>
          </>
        }
        description="Every patient inquiry moves through a tightly governed state machine. The LLM is confined to Node 7 and cannot alter path nodes or invent rooms."
      />

      {/* Visual Pipeline flow */}
      <div
        style={{
          borderRadius: "20px",
          border: "1px solid #e5e5e0",
          backgroundColor: "#ffffff",
          padding: "24px",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.04)",
          marginBottom: "36px",
        }}
      >
        <img
          src="/assets/diagrams/langgraph-workflow.svg"
          alt="LangGraph 7 Node Pipeline"
          style={{ width: "100%", height: "auto" }}
        />
      </div>

      {/* Interactive Step Explorer */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
          gap: "8px",
          marginBottom: "28px",
        }}
      >
        {nodes.map((n) => {
          const isSelected = activeStep.step === n.step;
          return (
            <button
              key={n.step}
              className={isSelected ? "pipeline-node is-active" : "pipeline-node"}
              onClick={() => setActiveStep(n)}
              style={{
                padding: "12px 10px",
                borderRadius: "12px",
                backgroundColor: isSelected ? "#0f1410" : "#ffffff",
                color: isSelected ? "#ffffff" : "#525252",
                border: isSelected ? "1px solid #0f1410" : "1px solid #e5e5e0",
                cursor: "pointer",
                textAlign: "center",
                transition: "all 0.15s ease",
              }}
            >
              <div style={{ fontSize: "11px", fontWeight: 700, color: isSelected ? "#abe6c7" : "#5c8a5c" }}>
                NODE {n.step}
              </div>
              <div style={{ fontSize: "12px", fontWeight: 600, marginTop: "4px" }}>
                {n.name}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Node Deep Dive Card */}
      <Card variant="moss" style={{ padding: "32px" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "16px", marginBottom: "20px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
              <span style={{ fontSize: "14px", fontWeight: 700, color: "#2d5016", textTransform: "uppercase" }}>
                Step {activeStep.step} of 7
              </span>
              <Badge variant="dark" size="sm">
                Latency Budget: {activeStep.latencyBudget}
              </Badge>
            </div>
            <h3 style={{ fontSize: "24px", fontWeight: 700, color: "#0f1410", margin: 0 }}>
              {activeStep.name}
            </h3>
          </div>
          <Badge variant="moss" size="md">
            Engine: {activeStep.technology}
          </Badge>
        </div>

        <p style={{ fontSize: "16px", lineHeight: "1.6", color: "#223d11", margin: "0 0 24px" }}>
          {activeStep.role}
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
          <div style={{ backgroundColor: "#ffffff", padding: "16px", borderRadius: "12px", border: "1px solid #dbf0e0" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#5c8a5c", textTransform: "uppercase" }}>
              Input Payload
            </span>
            <div style={{ fontSize: "13px", color: "#0f1410", fontFamily: "monospace", marginTop: "6px" }}>
              {activeStep.input}
            </div>
          </div>

          <div style={{ backgroundColor: "#ffffff", padding: "16px", borderRadius: "12px", border: "1px solid #dbf0e0" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#2d5016", textTransform: "uppercase" }}>
              Output State
            </span>
            <div style={{ fontSize: "13px", color: "#0f1410", fontFamily: "monospace", marginTop: "6px" }}>
              {activeStep.output}
            </div>
          </div>
        </div>
      </Card>
    </section>
  );
};

