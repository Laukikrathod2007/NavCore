import React, { useState } from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { CodeBlock } from "../ui/CodeBlock";
import { Tabs } from "../ui/Tabs";

export const CodeIntegration: React.FC = () => {
  const [activeTab, setActiveTab] = useState("python");

  const snippets: Record<string, { code: string; language: string; filename: string }> = {
    python: {
      filename: "app.py",
      language: "python",
      code: `from navcore.agents.workflow import create_workflow
from navcore.core.config import Config

# Initialize offline dual-memory workflow
workflow = create_workflow()

# Query in Hindi, Marathi, English, or code-mixed
result = workflow.invoke({
    "raw_query": "dil ke doctor kahaan hain",
    "current_node": "main_entrance",
    "language_override": None
})

print("Destination:", result["destination_node_id"])
# Output: cardiology_opd (Room 312, Floor 3)

print("Topological Path:", result["path_nodes"])
# Output: ['main_entrance', 'lift_A', 'floor_3_corridor_A', 'cardiology_opd']

print("Directions:", result["directions"])
# Output: "मुख्य प्रवेश द्वार से सीधे जाएं। लिफ्ट A लें..."`,
    },
    typescript: {
      filename: "navcore-component.tsx",
      language: "typescript",
      code: `import { useNavigation } from '@/hooks/useNavigation';

export function NavCoreNavigation() {
  const { query, result, loading, search } = useNavigation();

  return (
    <div className="navcore-container">
      <input 
        value={query} 
        onChange={(e) => search(e.target.value)}
        placeholder="Enter department in Hindi or English..." 
      />
      
      {result && (
        <div className="directions-panel">
          <h3>Destination: {result.destination}</h3>
          <p>{result.directions}</p>
          <span className="latency">{result.latency_ms}ms offline</span>
        </div>
      )}
    </div>
  );
}`,
    },
    curl: {
      filename: "terminal",
      language: "bash",
      code: `# Query local FastAPI edge server (Port 8001)
curl -X POST http://localhost:8001/query/text \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "रक्त तपासणी कुठे करायची",
    "current_node": "main_entrance"
  }'

# Response:
# {
#   "destination": "Pathology Lab (Room 220)",
#   "detected_language": "mr",
#   "path_nodes": ["main_entrance", "lift_A", "floor_2_corridor_A", "lab_pathology"],
#   "latency_ms": 11.4
# }`,
    },
    langgraph: {
      filename: "graph_builder.py",
      language: "python",
      code: `from langgraph.graph import StateGraph, END
from navcore.agents.state import NavigationState
from navcore.agents import (
    input_processor, language_detector, intent_classifier,
    retrieval, disambiguation, path_planner, direction_generator
)

builder = StateGraph(NavigationState)

builder.add_node("input", input_processor)
builder.add_node("language", language_detector)
builder.add_node("intent", intent_classifier)
builder.add_node("retrieval", retrieval)
builder.add_node("disambiguation", disambiguation)
builder.add_node("path_planner", path_planner)
builder.add_node("generator", direction_generator)

builder.set_entry_point("input")
# 100% Deterministic flow: LLM only exists in generator
app = builder.compile()`,
    },
  };

  const tabs = [
    { id: "python", label: "Python SDK" },
    { id: "typescript", label: "TypeScript / React" },
    { id: "curl", label: "FastAPI REST / cURL" },
    { id: "langgraph", label: "LangGraph StateGraph" },
  ];

  return (
    <section id="code-integration" style={{ padding: "90px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="DEVELOPER EXPERIENCE"
        title={
          <>
            Ship offline spatial navigation in <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>minutes</span>
          </>
        }
        description="Add sub-10ms dual-memory navigation to NavCore, campus portals, or edge devices. Works with your existing LangGraph and FastAPI microservices."
      />

      <div style={{ maxWidth: "860px", margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: "20px" }}>
          <Tabs
            items={tabs}
            activeId={activeTab}
            onChange={(id) => setActiveTab(id)}
            variant="pill"
          />
        </div>

        <CodeBlock
          code={snippets[activeTab].code}
          language={snippets[activeTab].language}
          filename={snippets[activeTab].filename}
        />
      </div>
    </section>
  );
};

