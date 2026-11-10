import React from "react";

type VoiceFeedbackProps = {
  isListening: boolean;
  isProcessing: boolean;
  transcript: string;
  liveCaptionsAvailable: boolean;
  error?: string;
};

export const VoiceFeedback: React.FC<VoiceFeedbackProps> = ({
  isListening,
  isProcessing,
  transcript,
  liveCaptionsAvailable,
  error,
}) => {
  if (!isListening && !isProcessing && !error) return null;

  return (
    <div className={`voice-feedback${isProcessing ? " is-processing" : " is-listening"}`} role={error ? "alert" : "status"} aria-live="polite">
      <div className="voice-feedback-mark" aria-hidden="true">
        <span className="voice-waveform">
          {Array.from({ length: 7 }, (_, index) => <i key={index} style={{ animationDelay: `${index * 75}ms` }} />)}
        </span>
      </div>
      <div className="voice-feedback-copy">
        <strong>{error ? "Microphone needs attention" : isProcessing ? "NavCore is finding your way" : "Listening to you"}</strong>
        <div className={`voice-feedback-caption${transcript ? " has-transcript" : ""}`}>
          {error || (transcript
            ? <><span>“{transcript}”</span>{isListening && <i className="voice-caption-cursor" aria-hidden="true" />}</>
            : isProcessing
              ? "Transcribing your recording and planning the route…"
              : liveCaptionsAvailable
                ? "Your words will appear here as you speak."
                : "Speak naturally. Your voice will be transcribed when you finish.")}
        </div>
        {!error && isListening && liveCaptionsAvailable && (
          <small className="voice-feedback-note">Live captions use your browser’s speech service; NavCore confirms the final transcript and route locally.</small>
        )}
        {!error && isListening && !liveCaptionsAvailable && (
          <small className="voice-feedback-note">Local Whisper will transcribe the recording when you finish.</small>
        )}
      </div>
      <span className="voice-feedback-state">{error ? "CHECK MIC" : isProcessing ? "LOCAL · WORKING" : "LIVE"}</span>
    </div>
  );
};
