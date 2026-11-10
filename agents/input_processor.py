"""Node 1: Input processor — text/voice/QR → query_text + current_location.

v2 adds:
- Fix 3: Verbal location extraction — if query mentions current location,
  extract it and strip from query before forwarding to retrieval.
"""

import logging
import os
import re
import subprocess
import tempfile
from typing import Dict, Optional

from agents.state import NavigationState
from core.config import Config

logger = logging.getLogger(__name__)

_whisper_model = None

# Fix 3: Patterns to extract current location from query text
_LOCATION_PATTERNS = [
    # English
    r"i(?:'m| am) (?:near|at|by|in|on) (.+?)(?:,|\.|$)",
    r"(?:from|starting from|currently at) (.+?)(?:,|\.|$)",
    r"i(?:'m| am) (?:standing|waiting|sitting) (?:at|near) (.+?)(?:,|\.|$)",
    # Hindi/Hinglish
    r"main (.+?) (?:ke paas|mein|par) (?:hoon|hun|hu)\b",
    r"(.+?) (?:ke paas|mein|par) (?:se|hoon|hun)\b",
    r"abhi (.+?) (?:mein|par|ke paas) (?:hoon|hun|hu)\b",
    # Marathi
    r"(.+?) (?:जवळ|मध्ये|वर) (?:आहे|आहोत)\b",
]

# Phrases to strip from query after location extraction
_LOCATION_STRIP_PATTERNS = [
    r"i(?:'m| am) (?:near|at|by|in|on) [^,\.]+[,\.]?\s*",
    r"(?:from|starting from|currently at) [^,\.]+[,\.]?\s*",
    r"main [^\s]+ (?:ke paas|mein|par) (?:hoon|hun|hu),?\s*",
    r"abhi [^\s]+ (?:mein|par|ke paas) (?:hoon|hun|hu),?\s*",
]


def _get_whisper_model():
    """Lazy-load Whisper model on first audio request.

    Returns:
        Loaded Whisper model instance.

    Raises:
        RuntimeError: If Whisper is not installed.
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            logger.info(f"Loading Whisper model: {Config.WHISPER_MODEL}")
            _whisper_model = whisper.load_model(Config.WHISPER_MODEL)
            logger.info("Whisper model loaded")
        except ImportError as e:
            raise RuntimeError(
                "openai-whisper not installed. Run: pip install openai-whisper"
            ) from e
    return _whisper_model


def is_valid_transcription(text: str) -> bool:
    """Check if Whisper output is usable (Fix 1).

    Filters out known hallucinations on silence or poor audio.

    Args:
        text: Transcribed text from Whisper.

    Returns:
        True if transcription is valid and usable.
    """
    if not text or len(text.strip()) < 3:
        return False
    hallucinations = {
        "thank you", "thanks for watching", ".", " ", "you",
        "thank you for watching", "thanks", "bye", "goodbye",
        "[music]", "[applause]", "[silence]",
    }
    return text.strip().lower() not in hallucinations


def _convert_to_wav(input_path: str) -> str:
    """Convert audio to WAV 16kHz mono using ffmpeg.

    Args:
        input_path: Path to input audio file.

    Returns:
        Path to converted WAV file. Caller must delete it.
    """
    if input_path.lower().endswith(".wav"):
        return input_path

    wav_path = input_path.rsplit(".", 1)[0] + "_converted.wav"
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-ar", "16000",
                "-ac", "1",
                "-f", "wav",
                wav_path,
            ],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr.decode()[:200]}")
            return input_path
        return wav_path
    except FileNotFoundError:
        logger.warning("ffmpeg not found — using original audio")
        return input_path
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg conversion timed out")
        return input_path


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using Whisper.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Transcribed text string.

    Raises:
        RuntimeError: If transcription fails.
    """
    logger.info(f"Transcribing audio: {audio_path}")

    converted_path = _convert_to_wav(audio_path)
    cleanup_converted = converted_path != audio_path

    try:
        model = _get_whisper_model()
        result = model.transcribe(
            converted_path,
            task="transcribe",
            fp16=False,
            beam_size=1,
            best_of=1,
            condition_on_previous_text=False,
        )
        text = result.get("text", "").strip()
        detected_lang = result.get("language", "unknown")
        logger.info(f"Transcribed ({detected_lang}): '{text[:80]}'")
        return text
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise RuntimeError(f"Transcription failed: {e}") from e
    finally:
        if cleanup_converted and os.path.exists(converted_path):
            os.unlink(converted_path)


def extract_location_from_query(
    query: str,
    graph,
) -> tuple[Optional[str], str]:
    """Try to extract current location mentioned in the query (Fix 3).

    If found, strips the location clause from the query text.

    Args:
        query: User query text.
        graph: Loaded SpatialGraph for node validation.

    Returns:
        Tuple of (node_id or None, cleaned_query_text).
    """
    query_lower = query.lower()

    for pattern in _LOCATION_PATTERNS:
        match = re.search(pattern, query_lower)
        if match:
            location_text = match.group(1).strip()
            # Try to match against node display names
            for node_id in graph.get_all_nodes():
                try:
                    node_data = graph.get_node_data(node_id)
                    display = node_data.get("display_name", "").lower()
                    if location_text in display or display in location_text:
                        # Strip the location clause from the query
                        cleaned = query
                        for strip_pat in _LOCATION_STRIP_PATTERNS:
                            cleaned = re.sub(
                                strip_pat, "", cleaned,
                                flags=re.IGNORECASE
                            ).strip()
                        cleaned = cleaned.lstrip(",").strip()
                        logger.info(
                            f"Extracted location: {node_id} from '{location_text}' "
                            f"| Cleaned query: '{cleaned}'"
                        )
                        return node_id, cleaned if cleaned else query
                except KeyError:
                    continue

    return None, query


def parse_qr_code(qr_data: str) -> Dict[str, Optional[str]]:
    """Parse a QR code string to extract current location.

    Format: "node:<node_id>" or just "<node_id>"

    Args:
        qr_data: Raw QR code string.

    Returns:
        Dict with 'current_location' (node ID or None).
    """
    logger.info(f"Parsing QR code: {qr_data}")
    qr_data = qr_data.strip()
    if qr_data.startswith("node:"):
        node_id = qr_data[5:]
        logger.info(f"QR location: {node_id}")
        return {"current_location": node_id}
    if qr_data and not qr_data.isspace():
        return {"current_location": qr_data}
    logger.warning("QR code did not contain a valid location")
    return {"current_location": None}


def input_processor_node(state: NavigationState) -> Dict:
    """LangGraph Node 1: Process raw input into normalized state.

    Text:  pass through, attempt verbal location extraction (Fix 3)
    Audio: transcribe via Whisper, then attempt location extraction
    QR:    parse QR code string, set current_location

    Args:
        state: Initial navigation state with input_modality.

    Returns:
        State update with query_text, current_location,
        and location_extracted_from_query.
    """
    logger.info("Node 1: Input processing")
    modality = state.get("input_modality", "text")

    result: Dict = {
        "location_extracted_from_query": False,
        "multi_destination": False,
        "secondary_node_id": None,
        "is_multi_destination": False,
        "low_confidence": False,
        "rephrase_message": None,
        "path_error": None,
    }

    if modality == "audio":
        audio_path = state.get("query_text", "")
        try:
            text = transcribe_audio(audio_path)
            result["query_text"] = text
        except RuntimeError as e:
            logger.error(f"Audio transcription failed: {e}")
            result["query_text"] = ""
            return result

    elif modality == "qr":
        qr_data = state.get("query_text", "")
        qr_result = parse_qr_code(qr_data)
        result["current_location"] = qr_result["current_location"]
        result["query_text"] = ""
        return result

    else:
        result["query_text"] = state.get("query_text", "")

    # Fix 3: Try to extract current location from query text
    query_text = result.get("query_text", "")
    existing_location = state.get("current_location")

    # Only try extraction if no explicit location was already set
    if query_text and not existing_location:
        try:
            # Import here to avoid circular imports at module level
            from agents.path_planner import _spatial_graph
            if _spatial_graph is not None:
                extracted_node, cleaned_query = extract_location_from_query(
                    query_text, _spatial_graph
                )
                if extracted_node:
                    result["current_location"] = extracted_node
                    result["query_text"] = cleaned_query
                    result["location_extracted_from_query"] = True
        except Exception as e:
            logger.debug(f"Location extraction skipped: {e}")

    logger.info(
        f"Processed input: modality={modality}, "
        f"query='{result.get('query_text', '')[:50]}', "
        f"location={result.get('current_location')}, "
        f"location_from_query={result.get('location_extracted_from_query')}"
    )
    return result
