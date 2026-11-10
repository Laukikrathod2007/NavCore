import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import {
  MicIcon,
  SearchIcon,
  VolumeIcon,
  PinIcon,
  HospitalIcon,
  QrCodeIcon,
  ArrowRightIcon,
  TurnLeftIcon,
  TurnRightIcon,
  ElevatorIcon,
  CloseIcon,
} from "../ui/Icons";
import { resolveQueryOffline, HOSPITAL_NODES, SAMPLE_DEPARTMENTS, DepartmentAlias } from "../../lib/hospitalData";
import { NavCoreVirtualKeyboard } from "./NavCoreVirtualKeyboard";
import { NavCoreDisambiguationModal, NavCoreDisambiguationOption } from "./NavCoreDisambiguationModal";
import { Modal } from "../ui/Modal";
import { useVoiceCapture, VoiceQueryResult } from "../../lib/useVoiceCapture";
import { VoiceFeedback } from "../ui/VoiceFeedback";

export const NavCoreView: React.FC = () => {
  const [query, setQuery] = useState("");
  const [activeLang, setActiveLang] = useState<"en" | "hi" | "mr" | "hiMix">("hi");
  const [showKeyboard, setShowKeyboard] = useState(false);
  const [isPlayingVoice, setIsPlayingVoice] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [showDisambig, setShowDisambig] = useState(false);
  const [disambiguationOptions, setDisambiguationOptions] = useState<NavCoreDisambiguationOption[]>([]);
  const [disambiguationQuestion, setDisambiguationQuestion] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState("");
  const [activeFloor, setActiveFloor] = useState<number>(3);
  const [isSearching, setIsSearching] = useState(false);
  const [isOfflineFallback, setIsOfflineFallback] = useState(false);
  const searchSequenceRef = useRef(0);

  const [result, setResult] = useState(() => resolveQueryOffline("dil ke doctor kahaan hain", "main_entrance"));

  const applyNavigationResult = (data: VoiceQueryResult, queryText: string) => {
    const destinationNode = data.destination_node_id
      ? HOSPITAL_NODES[data.destination_node_id]
      : undefined;
    const hasPath = Boolean(data.path_nodes?.length);

    setResult({
      destination: data.destination || (data.low_confidence ? "Destination not found" : "Route unavailable"),
      destination_node_id: data.destination_node_id || "",
      room_number: destinationNode?.roomNumber || "",
      floor: destinationNode?.floor ?? 0,
      detected_language: data.detected_language || "en",
      directions: data.directions || data.rephrase_message || "Please try another phrase or ask at reception.",
      path_nodes: data.path_nodes || [],
      warnings: data.warnings || [],
      requires_disambiguation: data.requires_disambiguation || false,
      confidence: data.low_confidence ? 0 : 1,
      latency_ms: data.latency_ms || 0,
    });
    if (hasPath && destinationNode) setActiveFloor(destinationNode.floor);
    setShowKeyboard(false);
    setIsOfflineFallback(false);
    const options = data.disambiguation_options || [];
    setDisambiguationOptions(options);
    setDisambiguationQuestion(data.disambiguation_question || null);
    setShowDisambig(Boolean(data.requires_disambiguation && options.length > 1));
    setQuery(queryText);
  };

  const { isListening, isProcessing, liveTranscript, liveCaptionsAvailable, error: voiceError, startRecording, stopRecording } = useVoiceCapture({
    language: activeLang === "mr" ? "mr-IN" : activeLang === "en" ? "en-IN" : "hi-IN",
    currentNode: "main_entrance",
    onTranscript: (transcript, voiceResult) => {
      if (!voiceResult.path_nodes?.length && !voiceResult.destination_node_id && !voiceResult.low_confidence && !voiceResult.directions) {
        void handleSearch(transcript);
        return;
      }
      applyNavigationResult(voiceResult, transcript);
    },
  });

  useEffect(() => {
    const updateTime = () => {
      const d = new Date();
      setCurrentTime(d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (text: string) => {
    if (!text.trim()) return;

    const requestId = ++searchSequenceRef.current;
    setQuery(text);
    setShowKeyboard(false);
    setIsSearching(true);

    try {
      const apiBase = (process.env.NEXT_PUBLIC_NAVCORE_API_URL || "").replace(/\/$/, "");
      const endpoint = apiBase ? `${apiBase}/query/text` : "/api/query/text";
      const languageOverride = activeLang === "hiMix" ? "hi-mix" : activeLang;
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          current_node: "main_entrance",
          language_override: languageOverride,
        }),
      });
      const rawBody = await response.text();
      let data: VoiceQueryResult = {};
      try {
        data = JSON.parse(rawBody);
      } catch {
        throw new Error("The navigation service returned an invalid response.");
      }
      if (!response.ok) {
        throw new Error("The navigation service could not find a route.");
      }
      if (requestId !== searchSequenceRef.current) return;
      applyNavigationResult(data, text);
    } catch {
      if (requestId !== searchSequenceRef.current) return;
      const offlineResult = resolveQueryOffline(text, "main_entrance");
      setResult(offlineResult);
      setActiveFloor(offlineResult.floor);
      setIsOfflineFallback(true);
      setDisambiguationOptions([]);
      setDisambiguationQuestion(null);
      setShowDisambig(offlineResult.confidence < 0.7);
    } finally {
      if (requestId === searchSequenceRef.current) setIsSearching(false);
    }
  };

  const handlePlayVoice = () => {
    setIsPlayingVoice(true);
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(result.directions);
      if (result.detected_language === "hi" || result.detected_language === "hi-mix") {
        utterance.lang = "hi-IN";
      } else if (result.detected_language === "mr") {
        utterance.lang = "mr-IN";
      } else {
        utterance.lang = "en-US";
      }
      utterance.onend = () => setIsPlayingVoice(false);
      utterance.onerror = () => setIsPlayingVoice(false);
      window.speechSynthesis.speak(utterance);
    } else {
      setTimeout(() => setIsPlayingVoice(false), 2000);
    }
  };

  const quickShortcuts = [
    { label: "Cardiology (दिल के डॉक्टर)", query: "dil ke doctor kahaan hain", icon: "❤️" },
    { label: "Blood Test (रक्त तपासणी)", query: "रक्त तपासणी कुठे करायची", icon: "🩸" },
    { label: "X-Ray & MRI (एक्स-रे)", query: "xray karwana hai room 212", icon: "🩻" },
    { label: "Bone Specialist (हड्डी)", query: "haddi ka doctor", icon: "🦴" },
    { label: "Pharmacy (दवा)", query: "parchi ki dawai kahan milegi", icon: "💊" },
    { label: "Pediatrics (बच्चों का डॉक्टर)", query: "child specialist", icon: "👶" },
  ];

  return (
    <div
      className="navcore-screen"
      style={{
        minHeight: "100vh",
        backgroundColor: "#0d110e",
        color: "#ffffff",
        display: "flex",
        flexDirection: "column",
        fontFamily: "var(--font-sans, sans-serif)",
      }}
    >
      {/* Top NavCore Header */}
      <header
        className="navcore-header"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "18px 32px",
          backgroundColor: "#131714",
          borderBottom: "1.5px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "12px" }}>
            <img src="/assets/brand/navcore-emblem-icon.png" alt="NavCore" width="40" height="40" />
            <div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: "#ffffff", letterSpacing: "-0.02em" }}>
                Nav<span style={{ color: "#abe6c7" }}>Core</span>
              </div>
              <div style={{ fontSize: "11px", color: "#5c8a5c", fontWeight: 600 }}>
                Offline Dual-Memory Spatial Guidance
              </div>
            </div>
          </Link>

          <div style={{ marginLeft: "20px" }}>
            <Badge variant="dark" pulse size="sm">
              <span style={{ color: "#05df72" }}>● 100% Offline Edge Active</span>
            </Badge>
          </div>
        </div>

        {/* Center: Live Clock & Location */}
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "20px", fontWeight: 700, letterSpacing: "1px", color: "#abe6c7" }}>
            {currentTime || "10:00 AM"}
          </div>
          <div style={{ fontSize: "12px", color: "#8b949e" }}>
            📍 You are at: <strong style={{ color: "#ffffff" }}>Main Entrance (Ground Floor)</strong>
          </div>
        </div>

        {/* Right: Emergency & Exit button */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <button
            onClick={() => handleSearch("emergency")}
            style={{
              padding: "10px 18px",
              borderRadius: "12px",
              backgroundColor: "#e40014",
              color: "#ffffff",
              border: "none",
              fontSize: "14px",
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: "0 0 15px rgba(228, 0, 20, 0.4)",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            🚨 Emergency (इमरजेंसी)
          </button>

          <Link href="/navcore" style={{ textDecoration: "none" }}>
            <button
              style={{
                padding: "10px 16px",
                borderRadius: "12px",
                backgroundColor: "rgba(255, 255, 255, 0.08)",
                color: "#ffffff",
                border: "1px solid rgba(255, 255, 255, 0.15)",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              ← Back to Home
            </button>
          </Link>
        </div>
      </header>

      {/* Main Touchscreen Body */}
      <main className="navcore-main" style={{ flex: 1, padding: "28px 32px", maxWidth: "1500px", margin: "0 auto", width: "100%", boxSizing: "border-box" }}>
        {/* Language selector bar */}
        <div className="navcore-language" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
          <div style={{ fontSize: "15px", fontWeight: 600, color: "#8b949e" }}>
            Choose Language / भाषा चुनें / भाषा निवडा:
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            {[
              { code: "hi", label: "हिन्दी (Hindi)" },
              { code: "mr", label: "मराठी (Marathi)" },
              { code: "en", label: "English" },
              { code: "hiMix", label: "Hinglish (Code-Mixed)" },
            ].map((lang) => (
              <button
                key={lang.code}
                className={activeLang === lang.code ? "is-active" : undefined}
                onClick={() => setActiveLang(lang.code as any)}
                style={{
                  padding: "8px 18px",
                  borderRadius: "10px",
                  fontSize: "14px",
                  fontWeight: activeLang === lang.code ? 700 : 500,
                  backgroundColor: activeLang === lang.code ? "#2d5016" : "rgba(255, 255, 255, 0.08)",
                  color: activeLang === lang.code ? "#ffffff" : "#c9d1d9",
                  border: activeLang === lang.code ? "1.5px solid #5c8a5c" : "1px solid rgba(255, 255, 255, 0.12)",
                  cursor: "pointer",
                }}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>

        {/* Large Touch Input Box with Mic */}
        <div
          className="navcore-search"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "14px",
            padding: "10px 16px 10px 24px",
            borderRadius: "20px",
            backgroundColor: "#161b17",
            border: "2px solid #5c8a5c",
            boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
            marginBottom: "20px",
          }}
        >
          <SearchIcon size={26} style={{ color: "#5c8a5c" }} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSearch(query);
            }}
            placeholder="Search department, doctor, procedure, or room number..."
            style={{
              flex: 1,
              backgroundColor: "transparent",
              border: "none",
              color: "#ffffff",
              fontSize: "22px",
              fontWeight: 500,
              outline: "none",
            }}
          />

          {/* Toggle Virtual Keyboard */}
          <button
            onClick={() => setShowKeyboard(!showKeyboard)}
            style={{
              padding: "10px 18px",
              borderRadius: "12px",
              backgroundColor: showKeyboard ? "#2d5016" : "rgba(255, 255, 255, 0.08)",
              color: "#ffffff",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              fontSize: "14px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            ⌨️ {showKeyboard ? "Hide Keyboard" : "Touch Keyboard"}
          </button>

          {/* Large Mic Voice Button */}
          <button
            onClick={isListening ? stopRecording : startRecording}
            disabled={isProcessing}
            aria-label={isListening ? "Stop recording" : isProcessing ? "Transcribing voice" : "Start voice search"}
            style={{
              width: "60px",
              height: "60px",
              borderRadius: "16px",
              backgroundColor: isListening ? "#e40014" : "#2d5016",
              color: "#ffffff",
              border: "2px solid #5c8a5c",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              boxShadow: isListening ? "0 0 24px #e40014" : "0 4px 16px rgba(45, 80, 22, 0.5)",
              transition: "all 0.2s ease",
            }}
            title="Speak into microphone"
          >
            {isProcessing ? <span aria-hidden="true">…</span> : <MicIcon size={28} />}
          </button>
        </div>

        <VoiceFeedback isListening={isListening} isProcessing={isProcessing} transcript={liveTranscript} liveCaptionsAvailable={liveCaptionsAvailable} error={voiceError} />
        {(isSearching || isOfflineFallback) && (
          <div
            role="status"
            aria-live="polite"
            style={{
              margin: "-10px 0 18px",
              color: isOfflineFallback ? "#9a6b35" : "#5c8a5c",
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            {isSearching
              ? "Finding a route through the hospital…"
              : "Backend unavailable — showing the local sample route."}
          </div>
        )}

        {/* Virtual Keyboard if open */}
        {showKeyboard && (
          <div style={{ marginBottom: "24px" }}>
            <NavCoreVirtualKeyboard
              onKeyPress={(char) => setQuery((prev) => prev + char)}
              onBackspace={() => setQuery((prev) => prev.slice(0, -1))}
              onClear={() => setQuery("")}
              onSubmit={() => handleSearch(query)}
            />
          </div>
        )}

        {/* Quick Shortcut Buttons */}
        <div className="navcore-shortcuts" style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "28px" }}>
          {quickShortcuts.map((sc) => (
            <button
              key={sc.label}
              onClick={() => {
                setQuery(sc.query);
                handleSearch(sc.query);
              }}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "12px 20px",
                borderRadius: "14px",
                backgroundColor: "#161b17",
                color: "#e6edf3",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                fontSize: "15px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              <span>{sc.icon}</span>
              <span>{sc.label}</span>
            </button>
          ))}
        </div>

        {/* Turn-by-Turn Result Panel + Floor Map */}
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: "24px" }} className="navcore-results navcore-grid-mobile">
          {/* Left: Direction Instructions Card */}
          <div
            className="navcore-result-card"
            style={{
              backgroundColor: "#161b17",
              borderRadius: "20px",
              border: "1.5px solid rgba(255, 255, 255, 0.12)",
              padding: "32px",
              boxShadow: "0 10px 40px rgba(0,0,0,0.4)",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "20px" }}>
              <div>
                <span style={{ fontSize: "12px", color: "#5c8a5c", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  Destination Found ({result.detected_language.toUpperCase()})
                </span>
                <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#ffffff", margin: "4px 0" }}>
                  {result.destination}
                </h2>
                <div style={{ fontSize: "14px", color: "#8b949e" }}>
                  Room: <strong style={{ color: "#abe6c7" }}>{result.room_number || "Main Wing"}</strong> • Floor: <strong style={{ color: "#abe6c7" }}>{result.floor}</strong>
                </div>
              </div>

              {/* Read Aloud button */}
              <button
                onClick={handlePlayVoice}
                style={{
                  padding: "10px 18px",
                  borderRadius: "12px",
                  backgroundColor: "#2d5016",
                  color: "#ffffff",
                  border: "1px solid #5c8a5c",
                  fontSize: "14px",
                  fontWeight: 600,
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  cursor: "pointer",
                }}
              >
                <VolumeIcon size={18} />
                <span>{isPlayingVoice ? "Speaking..." : "Read Aloud"}</span>
              </button>
            </div>

            {/* Natural Directions Box */}
            <div
              style={{
                backgroundColor: "#1f2620",
                borderRadius: "16px",
                border: "1.5px solid #2d5016",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div style={{ fontSize: "18px", lineHeight: "1.65", color: "#ffffff", fontWeight: 500 }}>
                {result.directions}
              </div>
            </div>

            {/* Waypoints Sequence */}
            <div style={{ marginBottom: "28px" }}>
              <div style={{ fontSize: "12px", color: "#8b949e", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "12px", fontWeight: 600 }}>
                Step-by-step route ({result.path_nodes.length} nodes):
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                {result.path_nodes.map((node, i) => (
                  <React.Fragment key={node}>
                    <span
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        fontSize: "13px",
                        fontFamily: "monospace",
                        backgroundColor: i === result.path_nodes.length - 1 ? "#2d5016" : "rgba(255, 255, 255, 0.08)",
                        color: "#ffffff",
                        border: "1px solid rgba(255, 255, 255, 0.1)",
                        fontWeight: 600,
                      }}
                    >
                      {node}
                    </span>
                    {i < result.path_nodes.length - 1 && (
                      <span style={{ color: "#5c8a5c", fontSize: "14px" }}>➔</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Action footer: QR transfer & Disambiguation */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "16px", borderTop: "1px solid rgba(255, 255, 255, 0.1)" }}>
              <button
                onClick={() => setShowQRModal(true)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "10px 18px",
                  borderRadius: "12px",
                  backgroundColor: "rgba(255, 255, 255, 0.08)",
                  color: "#ffffff",
                  border: "1px solid rgba(255, 255, 255, 0.15)",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <QrCodeIcon size={18} />
                <span>Beam Route to Phone (QR)</span>
              </button>

              <span style={{ fontSize: "12px", color: "#5c8a5c", fontWeight: 600 }}>
                ⚡ Local latency: {result.latency_ms}ms
              </span>
            </div>
          </div>

          {/* Right: SVG Floor Map with Route Active Highlight */}
          <div
            className="navcore-map-card"
            style={{
              backgroundColor: "#161b17",
              borderRadius: "20px",
              border: "1.5px solid rgba(255, 255, 255, 0.12)",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <span style={{ fontSize: "15px", fontWeight: 700, color: "#ffffff" }}>
                Interactive Facility Map
              </span>
              <div style={{ display: "flex", gap: "6px" }}>
                {[0, 1, 2, 3].map((f) => (
                  <button
                    key={f}
                    className={activeFloor === f ? "is-active" : undefined}
                    onClick={() => setActiveFloor(f)}
                    style={{
                      padding: "6px 12px",
                      borderRadius: "8px",
                      fontSize: "13px",
                      fontWeight: activeFloor === f ? 700 : 500,
                      backgroundColor: activeFloor === f ? "#2d5016" : "rgba(255, 255, 255, 0.08)",
                      color: activeFloor === f ? "#ffffff" : "#8b949e",
                      border: activeFloor === f ? "1px solid #5c8a5c" : "1px solid rgba(255, 255, 255, 0.1)",
                      cursor: "pointer",
                    }}
                  >
                    {f === 0 ? "Ground" : `Floor ${f}`}
                  </button>
                ))}
              </div>
            </div>

            {/* SVG Canvas */}
            <div
              className="navcore-map-canvas"
              style={{
                flex: 1,
                minHeight: "340px",
                backgroundColor: "#0d110e",
                borderRadius: "14px",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                padding: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg viewBox="0 0 600 360" width="100%" height="320" fill="none">
                {/* Central Corridor */}
                <rect x="80" y="150" width="440" height="50" rx="10" fill="#1f2620" stroke="#2d5016" strokeWidth="1.5" />
                <text x="300" y="180" textAnchor="middle" fontSize="12" fill="#8b949e" fontFamily="sans-serif">
                  {activeFloor === 0 ? "Ground Concourse" : `Floor ${activeFloor} Concourse`}
                </text>

                {/* Elevator Core */}
                <rect x="260" y="60" width="80" height="60" rx="8" fill="#2d5016" stroke="#5c8a5c" strokeWidth="2" />
                <text x="300" y="95" textAnchor="middle" fontSize="13" fontWeight="700" fill="#ffffff" fontFamily="sans-serif">
                  🛗 Lift A
                </text>

                {/* Nodes on active floor */}
                {Object.values(HOSPITAL_NODES)
                  .filter((n) => n.floor === activeFloor)
                  .map((node, i) => {
                    const isTarget = node.id === result.destination_node_id;
                    const isInPath = result.path_nodes.includes(node.id);
                    const posX = 70 + (i % 3) * 165;
                    const posY = i >= 3 ? 230 : 60;

                    return (
                      <g key={node.id} transform={`translate(${posX}, ${posY})`}>
                        <rect
                          width="140"
                          height="64"
                          rx="10"
                          fill={isTarget ? "#2d5016" : isInPath ? "#1f2620" : "#131714"}
                          stroke={isTarget ? "#05df72" : isInPath ? "#5c8a5c" : "rgba(255, 255, 255, 0.15)"}
                          strokeWidth={isTarget || isInPath ? "2.5" : "1"}
                        />
                        <text
                          x="70"
                          y="28"
                          textAnchor="middle"
                          fontSize="11"
                          fontWeight={isTarget ? "700" : "600"}
                          fill="#ffffff"
                          fontFamily="sans-serif"
                        >
                          {node.name.length > 17 ? node.name.slice(0, 16) + "…" : node.name}
                        </text>
                        <text
                          x="70"
                          y="46"
                          textAnchor="middle"
                          fontSize="10"
                          fill={isTarget ? "#05df72" : "#8b949e"}
                          fontFamily="sans-serif"
                        >
                          {node.roomNumber ? `Rm ${node.roomNumber}` : node.type}
                        </text>
                      </g>
                    );
                  })}
              </svg>
            </div>
          </div>
        </div>
      </main>

      {/* QR Code Modal */}
      <Modal
        isOpen={showQRModal}
        onClose={() => setShowQRModal(false)}
        title="Scan with your Phone Camera"
        subtitle="Take your directions with you — no app download required"
      >
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          {/* Simulated QR Code SVG */}
          <div
            style={{
              width: "180px",
              height: "180px",
              margin: "0 auto 16px",
              padding: "12px",
              backgroundColor: "#ffffff",
              borderRadius: "16px",
              border: "2px solid #0f1410",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <QrCodeIcon size={140} style={{ color: "#0f1410" }} />
          </div>
          <div style={{ fontSize: "16px", fontWeight: 700, color: "#0f1410", marginBottom: "4px" }}>
            Destination: {result.destination}
          </div>
          <div style={{ fontSize: "13px", color: "#525252" }}>
            Room {result.room_number || "OPD"} • Floor {result.floor}
          </div>
          <div style={{ marginTop: "16px", fontSize: "12px", color: "#888888" }}>
            Scanned routes load the offline map in your mobile browser.
          </div>
        </div>
      </Modal>

      {/* Disambiguation Modal */}
      <NavCoreDisambiguationModal
        isOpen={showDisambig}
        onClose={() => setShowDisambig(false)}
        query={query}
        options={disambiguationOptions}
        question={disambiguationQuestion}
        onSelectDepartment={(option) => {
          setQuery(option.display);
          setShowDisambig(false);
          void handleSearch(option.display);
        }}
      />
    </div>
  );
};

