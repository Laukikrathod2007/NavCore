import React, { useState } from "react";
import { SectionHeader } from "../layout/SectionHeader";
import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { MicIcon, SearchIcon, VolumeIcon, CompassIcon, PinIcon } from "../ui/Icons";
import { resolveQueryOffline, HOSPITAL_NODES } from "../../lib/hospitalData";
import { useVoiceCapture } from "../../lib/useVoiceCapture";
import { VoiceFeedback } from "../ui/VoiceFeedback";

export const InteractiveNavCoreDemo: React.FC = () => {
  const [inputText, setInputText] = useState("dil ke doctor kahaan hain");
  const [activeFloor, setActiveFloor] = useState<number>(3);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [startNode, setStartNode] = useState("main_entrance");

  const resolution = resolveQueryOffline(inputText, startNode);
  const { isListening, isProcessing, liveTranscript, liveCaptionsAvailable, error: voiceError, startRecording, stopRecording } = useVoiceCapture({
    language: resolution.detected_language === "mr" ? "mr-IN" : resolution.detected_language === "hi" || resolution.detected_language === "hi-mix" ? "hi-IN" : "en-IN",
    currentNode: startNode,
    onTranscript: (transcript) => setInputText(transcript),
  });

  const sampleQueries = [
    { label: "Hindi Heart", query: "dil ke doctor kahaan hain" },
    { label: "Marathi Blood Test", query: "रक्त तपासणी कुठे करायची" },
    { label: "English Emergency", query: "Where is emergency casualty?" },
    { label: "Hinglish X-Ray", query: "xray karwane ke liye kahan jana padega" },
    { label: "Bone Specialist", query: "haddi ka doctor kaun se floor pe hai" },
  ];

  const handlePlayAudio = () => {
    setIsPlayingAudio(true);
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(resolution.directions);
      if (resolution.detected_language === "hi" || resolution.detected_language === "hi-mix") {
        utterance.lang = "hi-IN";
      } else if (resolution.detected_language === "mr") {
        utterance.lang = "mr-IN";
      } else {
        utterance.lang = "en-US";
      }
      utterance.onend = () => setIsPlayingAudio(false);
      utterance.onerror = () => setIsPlayingAudio(false);
      window.speechSynthesis.speak(utterance);
    } else {
      setTimeout(() => setIsPlayingAudio(false), 2500);
    }
  };

  return (
    <section id="interactive-demo" style={{ padding: "80px 24px", maxWidth: "1200px", margin: "0 auto" }}>
      <SectionHeader
        badge="INTERACTIVE SANDBOX"
        title={
          <>
            Test the live <span style={{ fontFamily: "var(--font-serif, serif)", fontStyle: "italic", fontWeight: 400 }}>multilingual spatial engine</span>
          </>
        }
        description="Try real patient queries in Hindi, Marathi, English, or code-mixed Hinglish. Watch Qdrant Edge resolve the canonical node and NetworkX plot the shortest multi-floor path."
      />

      <div
        style={{
          borderRadius: "24px",
          border: "1px solid #e5e5e0",
          backgroundColor: "#ffffff",
          boxShadow: "0 20px 60px -15px rgba(0, 0, 0, 0.08)",
          overflow: "hidden",
        }}
      >
        {/* Preset pill bar */}
        <div
          style={{
            padding: "16px 24px",
            backgroundColor: "#fafafa",
            borderBottom: "1px solid #e5e5e0",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            overflowX: "auto",
          }}
        >
          <span style={{ fontSize: "12px", fontWeight: 600, color: "#888888", whiteSpace: "nowrap" }}>
            Presets:
          </span>
          {sampleQueries.map((item) => (
            <button
              key={item.label}
              onClick={() => {
                setInputText(item.query);
                const res = resolveQueryOffline(item.query, startNode);
                setActiveFloor(res.floor);
              }}
              style={{
                padding: "6px 14px",
                borderRadius: "9999px",
                fontSize: "12px",
                fontWeight: inputText === item.query ? 600 : 450,
                backgroundColor: inputText === item.query ? "#0f1410" : "#ffffff",
                color: inputText === item.query ? "#ffffff" : "#525252",
                border: inputText === item.query ? "1px solid #0f1410" : "1px solid #e5e5e0",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ padding: "24px", borderBottom: "1px solid #e5e5e0" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "8px 12px 8px 18px",
              borderRadius: "16px",
              border: "1.5px solid #0f1410",
              backgroundColor: "#ffffff",
              boxShadow: "0 4px 16px -4px rgba(0, 0, 0, 0.05)",
            }}
          >
            <SearchIcon size={20} style={{ color: "#737373" }} />
            <input
              type="text"
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value);
                const res = resolveQueryOffline(e.target.value, startNode);
                setActiveFloor(res.floor);
              }}
              placeholder="Ask for any department in Hindi, Marathi, English (e.g. dil ke doctor, khoon test)..."
              style={{
                flex: 1,
                border: "none",
                fontSize: "16px",
                outline: "none",
                color: "#0f1410",
                backgroundColor: "transparent",
              }}
            />
            {/* Mic button with animation if listening */}
            <button
              onClick={isListening ? stopRecording : startRecording}
              disabled={isProcessing}
              aria-label={isListening ? "Stop voice recording" : isProcessing ? "Transcribing voice" : "Start voice search"}
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "12px",
                backgroundColor: isListening ? "#e40014" : "#2d5016",
                color: "#ffffff",
                border: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              title={isListening ? "Tap to finish recording" : "Record a real voice query"}
            >
              {isProcessing ? <span aria-hidden="true">…</span> : <MicIcon size={20} />}
            </button>
          </div>

          <VoiceFeedback isListening={isListening} isProcessing={isProcessing} transcript={liveTranscript} liveCaptionsAvailable={liveCaptionsAvailable} error={voiceError} />

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "12px", fontSize: "12px", color: "#737373" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span>Current Position:</span>
              <select
                value={startNode}
                onChange={(e) => setStartNode(e.target.value)}
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  border: "1px solid #e5e5e0",
                  fontSize: "12px",
                  color: "#0f1410",
                  backgroundColor: "#fafafa",
                  cursor: "pointer",
                }}
              >
                <option value="main_entrance">Main Entrance (Ground)</option>
                <option value="reception">Reception Counter (Ground)</option>
                <option value="lift_A">Lift A (Central)</option>
                <option value="floor_1_corridor_A">Floor 1 Corridor</option>
                <option value="floor_2_corridor_A">Floor 2 Corridor</option>
              </select>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Badge variant="moss" size="sm">
                Language: {resolution.detected_language.toUpperCase()}
              </Badge>
              <Badge variant="neutral" size="sm">
                Latency: {resolution.latency_ms}ms
              </Badge>
            </div>
          </div>
        </div>

        {/* Two-Column Results: Floor Visualizer & Guidance */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))" }}>
          {/* Left: Direction Instructions Card */}
          <div style={{ padding: "32px", borderRight: "1px solid #e5e5e0" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "10px",
                    backgroundColor: "#f0f7f2",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#2d5016",
                  }}
                >
                  <PinIcon size={18} />
                </span>
                <div>
                  <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#0f1410", margin: 0 }}>
                    {resolution.destination}
                  </h3>
                  <div style={{ fontSize: "12px", color: "#737373" }}>
                    Room {resolution.room_number || "OPD"} • Floor {resolution.floor}
                  </div>
                </div>
              </div>

              {/* Read Aloud button */}
              <Button
                variant="outline"
                size="sm"
                icon={<VolumeIcon size={14} />}
                onClick={handlePlayAudio}
                loading={isPlayingAudio}
              >
                {isPlayingAudio ? "Speaking..." : "Listen"}
              </Button>
            </div>

            {/* Generated Natural Instructions */}
            <div
              style={{
                backgroundColor: "#fafafa",
                padding: "20px",
                borderRadius: "14px",
                border: "1px solid #e5e5e0",
                marginBottom: "24px",
              }}
            >
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#5c8a5c", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
                Turn-by-Turn Directions ({resolution.detected_language})
              </div>
              <p style={{ fontSize: "15px", lineHeight: "1.6", color: "#0f1410", margin: 0, fontWeight: 500 }}>
                {resolution.directions}
              </p>
            </div>

            {/* Step-by-Step Waypoint Timeline */}
            <div>
              <div style={{ fontSize: "12px", fontWeight: 700, color: "#888888", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "12px" }}>
                Computed Waypoints ({resolution.path_nodes.length} nodes)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {resolution.path_nodes.map((nodeId, index) => {
                  const nodeObj = HOSPITAL_NODES[nodeId];
                  const isLast = index === resolution.path_nodes.length - 1;
                  return (
                    <div key={nodeId} style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                        <span
                          style={{
                            width: "24px",
                            height: "24px",
                            borderRadius: "50%",
                            backgroundColor: isLast ? "#2d5016" : index === 0 ? "#0f1410" : "#f0f7f2",
                            color: isLast || index === 0 ? "#ffffff" : "#2d5016",
                            fontSize: "11px",
                            fontWeight: 700,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          {index + 1}
                        </span>
                        {!isLast && (
                          <span style={{ width: "2px", height: "18px", backgroundColor: "#e5e5e0", margin: "2px 0" }} />
                        )}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "13px", fontWeight: 600, color: isLast ? "#2d5016" : "#0f1410" }}>
                          {nodeObj ? nodeObj.name : nodeId}
                        </div>
                        <div style={{ fontSize: "11px", color: "#737373" }}>
                          Floor {nodeObj ? nodeObj.floor : 0} {nodeObj?.roomNumber ? `• Room ${nodeObj.roomNumber}` : ""}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right: SVG Floor Map with Active Highlights */}
          <div style={{ padding: "32px", backgroundColor: "#fbfbfa" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <span style={{ fontSize: "13px", fontWeight: 600, color: "#0f1410" }}>
                Interactive Hospital Floor Map
              </span>
              {/* Floor Switcher */}
              <div style={{ display: "flex", gap: "4px" }}>
                {[0, 1, 2, 3].map((f) => (
                  <button
                    key={f}
                    onClick={() => setActiveFloor(f)}
                    style={{
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontSize: "12px",
                      fontWeight: activeFloor === f ? 700 : 500,
                      backgroundColor: activeFloor === f ? "#0f1410" : "#ffffff",
                      color: activeFloor === f ? "#ffffff" : "#525252",
                      border: "1px solid #e5e5e0",
                      cursor: "pointer",
                    }}
                  >
                    {f === 0 ? "Ground" : `Floor ${f}`}
                  </button>
                ))}
              </div>
            </div>

            {/* SVG Floor Plan Canvas */}
            <div
              style={{
                borderRadius: "14px",
                border: "1px solid #e5e5e0",
                backgroundColor: "#ffffff",
                padding: "16px",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
              }}
            >
              <svg viewBox="0 0 600 320" width="100%" height="240" fill="none">
                {/* Background grid */}
                <pattern id="navcoreGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0ec" strokeWidth="0.8" />
                </pattern>
                <rect width="600" height="320" fill="url(#navcoreGrid)" rx="8" />

                {/* Corridor backbone */}
                <rect x="120" y="140" width="380" height="40" rx="8" fill="#f5f5f4" stroke="#e5e5e0" strokeWidth="1.5" />
                <text x="310" y="164" textAnchor="middle" fontSize="11" fill="#888888" fontFamily="sans-serif">
                  {activeFloor === 0 ? "Ground Concourse" : `Floor ${activeFloor} Central Corridor`}
                </text>

                {/* Vertical elevator shaft */}
                <rect x="270" y="60" width="60" height="60" rx="8" fill="#f0f7f2" stroke="#abe6c7" strokeWidth="1.5" />
                <text x="300" y="95" textAnchor="middle" fontSize="12" fontWeight="700" fill="#2d5016" fontFamily="sans-serif">
                  Lift A
                </text>

                {/* Floor Nodes */}
                {Object.values(HOSPITAL_NODES)
                  .filter((n) => n.floor === activeFloor)
                  .map((node, i) => {
                    const isTarget = node.id === resolution.destination_node_id;
                    const isInPath = resolution.path_nodes.includes(node.id);
                    const posX = 150 + (i % 3) * 140;
                    const posY = i >= 3 ? 220 : 60;

                    return (
                      <g key={node.id} transform={`translate(${posX}, ${posY})`}>
                        <rect
                          width="110"
                          height="52"
                          rx="8"
                          fill={isTarget ? "#2d5016" : isInPath ? "#f0f7f2" : "#ffffff"}
                          stroke={isTarget ? "#2d5016" : isInPath ? "#5c8a5c" : "#e5e5e0"}
                          strokeWidth={isTarget || isInPath ? "2" : "1"}
                        />
                        <text
                          x="55"
                          y="24"
                          textAnchor="middle"
                          fontSize="11"
                          fontWeight={isTarget ? "700" : "600"}
                          fill={isTarget ? "#ffffff" : "#0f1410"}
                          fontFamily="sans-serif"
                        >
                          {node.name.length > 15 ? node.name.slice(0, 14) + "..." : node.name}
                        </text>
                        <text
                          x="55"
                          y="38"
                          textAnchor="middle"
                          fontSize="9"
                          fill={isTarget ? "#abe6c7" : "#737373"}
                          fontFamily="sans-serif"
                        >
                          {node.roomNumber ? `Rm ${node.roomNumber}` : node.type}
                        </text>
                      </g>
                    );
                  })}
              </svg>
            </div>

            <div style={{ marginTop: "14px", display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "11px", color: "#737373" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ display: "inline-block", width: "10px", height: "10px", borderRadius: "2px", backgroundColor: "#2d5016" }} />
                <span>Active Target</span>
                <span style={{ display: "inline-block", width: "10px", height: "10px", borderRadius: "2px", backgroundColor: "#f0f7f2", border: "1px solid #5c8a5c" }} />
                <span>Path Waypoint</span>
              </div>
              <span>Click floor buttons above to inspect vertical paths</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

