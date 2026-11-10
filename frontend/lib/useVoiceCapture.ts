import { useCallback, useEffect, useRef, useState } from "react";
import { apiUrl } from "./urls";

type VoiceCaptureOptions = {
  onTranscript: (text: string, result: VoiceQueryResult) => void;
  language?: string;
  currentNode?: string;
};

type RecognitionResult = { isFinal: boolean; 0: { transcript: string } };
type RecognitionEvent = { resultIndex: number; results: ArrayLike<RecognitionResult> };
type RecognitionErrorEvent = { error: string };
type RecognitionController = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: RecognitionEvent) => void) | null;
  onerror: ((event: RecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};
type RecognitionConstructor = new () => RecognitionController;

export type VoiceQueryResult = {
  destination?: string;
  destination_node_id?: string;
  detected_language?: string;
  directions?: string;
  path_nodes?: string[];
  warnings?: string[];
  latency_ms?: number;
  low_confidence?: boolean;
  rephrase_message?: string | null;
  requires_disambiguation?: boolean;
  disambiguation_question?: string | null;
  disambiguation_options?: Array<{ display: string; node_id: string }> | null;
};

/** Record a real microphone query and send it to NavCore's local Whisper API. */
export function useVoiceCapture({ onTranscript, language = "en-IN", currentNode = "main_entrance" }: VoiceCaptureOptions) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<RecognitionController | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const finalTranscriptRef = useRef<string[]>([]);
  const activeRef = useRef(false);
  const cancelledRef = useRef(false);
  const liveCaptionsDisabledRef = useRef(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const recognitionRestartRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [liveCaptionsAvailable, setLiveCaptionsAvailable] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  const stopRecording = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
    activeRef.current = false;
    recognitionRef.current?.stop();
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
  }, []);

  const startRecording = useCallback(async () => {
    if (isListening || isProcessing) return;
    setError("");
    setLiveTranscript("");
    setLiveCaptionsAvailable(true);
    finalTranscriptRef.current = [];
    cancelledRef.current = false;
    liveCaptionsDisabledRef.current = false;

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("This browser cannot record audio. Try a current version of Chrome or Edge.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      });
      streamRef.current = stream;
      chunksRef.current = [];

      const mimeType = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"]
        .find((type) => MediaRecorder.isTypeSupported(type));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        activeRef.current = false;
        recognitionRef.current?.stop();
        recognitionRef.current = null;
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        recorderRef.current = null;
        setIsListening(false);

        if (cancelledRef.current) return;

        const audio = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        chunksRef.current = [];
        if (audio.size < 700) {
          setError("I didn’t catch any audio. Tap the microphone and try again.");
          return;
        }

        const extension = audio.type.includes("mp4") ? "m4a" : "webm";
        const form = new FormData();
        form.append("file", audio, `navcore-voice.${extension}`);
        form.append("current_node", currentNode);
        setIsProcessing(true);
        try {
          // Local dev uses the Next.js proxy; static deployments call the API directly.
          const response = await fetch(apiUrl("/query/audio"), { method: "POST", body: form });
          const rawBody = await response.text();
          let data: VoiceQueryResult & { message?: string; detail?: string; transcribed_text?: string } = {};
          try {
            data = JSON.parse(rawBody);
          } catch {
            data.message = rawBody.trim().slice(0, 240);
          }
          if (!response.ok) {
            if (data.transcribed_text?.trim()) {
              const recoveredTranscript = data.transcribed_text.trim();
              setLiveTranscript("");
              onTranscriptRef.current(recoveredTranscript, data);
              setError("I caught your words, but the route service had a problem. Showing the local result.");
              return;
            }
            const detail = data.message || data.detail;
            throw new Error(detail
              ? `Voice service error (${response.status}): ${detail}`
              : `Voice service error (${response.status}). Please try again or type your query.`);
          }

          const transcript = typeof data.transcribed_text === "string" ? data.transcribed_text.trim() : "";
          if (!transcript) throw new Error("NavCore couldn’t understand that recording. Please try again.");
          setLiveTranscript("");
          onTranscriptRef.current(transcript, data as VoiceQueryResult);
        } catch (cause) {
          const message = cause instanceof Error ? cause.message : "Voice transcription failed.";
          setError(message.includes("Failed to fetch")
            ? "NavCore’s local voice service isn’t running. Start the backend and try again."
            : message);
        } finally {
          setIsProcessing(false);
        }
      };

      recorder.start(250);
      activeRef.current = true;
      setIsListening(true);

      const recognitionWindow = window as Window & {
        SpeechRecognition?: RecognitionConstructor;
        webkitSpeechRecognition?: RecognitionConstructor;
      };
      const Recognition = recognitionWindow.SpeechRecognition || recognitionWindow.webkitSpeechRecognition;
      if (Recognition) {
        const startLiveCaptions = () => {
          if (!activeRef.current) return;
          const recognition = new Recognition();
          recognition.lang = language;
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.onresult = (event) => {
            const interim: string[] = [];
            for (let i = event.resultIndex; i < event.results.length; i += 1) {
              const phrase = event.results[i][0]?.transcript?.trim();
              if (!phrase) continue;
              if (event.results[i].isFinal) finalTranscriptRef.current.push(phrase);
              else interim.push(phrase);
            }
            setLiveTranscript([...finalTranscriptRef.current, ...interim].join(" "));
          };
          recognition.onerror = (event) => {
            if (event.error !== "no-speech") {
              liveCaptionsDisabledRef.current = true;
              setLiveCaptionsAvailable(false);
            }
          };
          recognition.onend = () => {
            if (activeRef.current && !cancelledRef.current && !liveCaptionsDisabledRef.current) {
              recognitionRestartRef.current = setTimeout(startLiveCaptions, 220);
            }
          };
          recognitionRef.current = recognition;
          try {
            recognition.start();
          } catch {
            setLiveCaptionsAvailable(false);
          }
        };
        startLiveCaptions();
      } else {
        setLiveCaptionsAvailable(false);
      }

      timeoutRef.current = setTimeout(() => {
        if (recorder.state === "recording") recorder.stop();
      }, 12000);
    } catch (cause) {
      const errorName = cause instanceof DOMException ? cause.name : "";
      setError(errorName === "NotAllowedError"
        ? "Microphone access is blocked. Allow microphone access in your browser and try again."
        : errorName === "NotFoundError"
          ? "No microphone was found. Connect a microphone and try again."
          : "Couldn’t start the microphone. Check your device and try again.");
    }
  }, [isListening, isProcessing, language, currentNode]);

  useEffect(() => () => {
    cancelledRef.current = true;
    activeRef.current = false;
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (recognitionRestartRef.current) clearTimeout(recognitionRestartRef.current);
    recognitionRef.current?.abort();
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  return { isListening, isProcessing, liveTranscript, liveCaptionsAvailable, error, startRecording, stopRecording };
}
