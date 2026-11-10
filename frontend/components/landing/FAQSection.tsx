import React, { useState } from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { ChevronDownIcon } from "../ui/Icons";

interface FAQItem {
  q: string;
  a: string;
}

export const FAQSection: React.FC = () => {
  const faqs: FAQItem[] = [
    {
      q: "Why can't hospitals simply use Google Maps or Bluetooth beacons for indoor navigation?",
      a: "GPS satellite signals cannot penetrate multi-story concrete hospital slabs, providing zero vertical floor accuracy and failing completely in underground radiology basements. Bluetooth beacon networks cost thousands of dollars to install and maintain, battery replacements fail constantly, and patients are forced to download a proprietary app that doesn't work without high-speed Wi-Fi.",
    },
    {
      q: "How does NavCore understand colloquial terms like 'dil ke doctor' or 'khoon test'?",
      a: "NavCore's Semantic Memory uses multilingual-e5-small (a 384-dimensional dense vector model) fine-tuned for Indic vocabulary. It matches natural linguistic descriptions—such as 'dil wala doctor', 'Dr. Mehta', 'ECG room', and 'Room 312'—to the canonical node 'cardiology_opd' in under 12 milliseconds without relying on rigid keyword matching.",
    },
    {
      q: "Why doesn't NavCore let the LLM generate the route directly?",
      a: "Standalone generative models (including GPT-4 and Llama) have a 59% junction hallucination rate in physical navigation benchmarks—they invent non-existent corridors, walk patients through solid walls, or misroute emergency cases. In NavCore, the path is computed deterministically by NetworkX BFS. The LLM's only job is translating that verified topological path into patient-friendly speech.",
    },
    {
      q: "Can NavCore run in an underground basement with zero internet connection?",
      a: "Yes, 100%. All components—Qdrant Edge vector storage, NetworkX graph memory, Whisper Tiny voice transcription, and Llama 3.2 3B LLM—run entirely on the local CPU or edge hardware. No internet cables, Wi-Fi passwords, or external cloud API keys are required.",
    },
    {
      q: "How can hospital administrators update doctor OPD timings or close wings for cleaning?",
      a: "NavCore includes a built-in Hospital Admin Portal. Medical superintendents and nursing staff can toggle doctor duty status or mark elevators under repair with a single tap. The topological graph dynamically recalculates paths over WebSocket in real time to reroute patients around closed corridors.",
    },
  ];

  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section style={{ padding: "80px 24px 100px", maxWidth: "920px", margin: "0 auto" }}>
      <SectionHeader
        badge="FREQUENTLY ASKED QUESTIONS"
        title={
          <>
            Frequently asked <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>questions</span>
          </>
        }
        description="Everything you need to know about offline dual-memory spatial RAG and edge NavCore deployment."
      />

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {faqs.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div
              key={idx}
              style={{
                borderRadius: "14px",
                border: isOpen ? "1px solid #5c8a5c" : "1px solid #e5e5e0",
                backgroundColor: "#ffffff",
                overflow: "hidden",
                transition: "all 0.2s ease",
              }}
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                style={{
                  width: "100%",
                  padding: "20px 24px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  backgroundColor: "transparent",
                  border: "none",
                  textAlign: "left",
                  cursor: "pointer",
                }}
              >
                <span style={{ fontSize: "16px", fontWeight: 600, color: "#0f1410", paddingRight: "16px" }}>
                  {faq.q}
                </span>
                <span
                  style={{
                    transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                    transition: "transform 0.2s ease",
                    color: isOpen ? "#2d5016" : "#737373",
                    display: "flex",
                  }}
                >
                  <ChevronDownIcon size={18} />
                </span>
              </button>

              {isOpen && (
                <div
                  style={{
                    padding: "0 24px 22px",
                    fontSize: "15px",
                    lineHeight: "1.6",
                    color: "#525252",
                    borderTop: "1px solid #f0f0ec",
                    paddingTop: "16px",
                  }}
                >
                  {faq.a}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};

