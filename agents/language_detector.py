"""Node 2: Language detection for Hindi/Marathi/English/code-mixed.

Uses langdetect for ISO 639 language codes, plus a heuristic for
code-mixed text (Hindi-English mix detected via Devanagari + Latin
script co-occurrence). Fully offline, no LLM call needed.
"""

import logging
import re
from typing import Dict

from agents.state import NavigationState

logger = logging.getLogger(__name__)

# Devanagari Unicode range: U+0900 to U+097F
_DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
# Latin script pattern (basic ASCII letters)
_LATIN_PATTERN = re.compile(r"[a-zA-Z]")

# Language code mapping from langdetect to our categories
_LANG_MAP = {
    "hi": "hi",
    "mr": "mr",
    "en": "en",
}


def _detect_code_mixed(text: str) -> bool:
    """Check if text contains both Devanagari and Latin scripts.

    Code-mixed Hindi-English (Hinglish) typically has both scripts
    or Romanized Hindi words mixed with English. This heuristic catches
    the Devanagari + Latin co-occurrence case.

    Args:
        text: Input text to analyze.

    Returns:
        True if both Devanagari and Latin scripts are present.
    """
    has_devanagari = bool(_DEVANAGARI_PATTERN.search(text))
    has_latin = bool(_LATIN_PATTERN.search(text))
    return has_devanagari and has_latin


def _detect_romanized_hindi(text: str) -> bool:
    """Heuristic check for Romanized Hindi without Devanagari.

    Common Hindi words written in Latin script indicate code-mixed
    input even without Devanagari characters.

    Args:
        text: Input text to analyze.

    Returns:
        True if common Romanized Hindi markers are found.
    """
    text_lower = text.lower()
    hindi_markers = [
        "kahaan", "kahan", "kaha", "kaisa", "kaisi",
        "mujhe", "mera", "meri", "hamko", "humko",
        "doctor", "dil", "haddi", "dawai", "baccho",
        "karwana", "milna", "milenge", "chahiye",
        "hai", "hoon", "tha", "thi",
    ]
    return any(marker in text_lower for marker in hindi_markers)


def detect_language(text: str) -> str:
    """Detect the language of the input text.

    Detection order:
    1. If text has both Devanagari and Latin → "hi-mix"
    2. If text has Devanagari only → use langdetect (likely "hi" or "mr")
    3. If text has Latin with Romanized Hindi markers → "hi-mix"
    4. Otherwise → use langdetect, default to "en"

    Args:
        text: Input text in any supported language.

    Returns:
        One of: "hi", "mr", "en", "hi-mix".
    """
    if not text or not text.strip():
        logger.warning("Empty text for language detection")
        return "en"

    # Check for code-mixed with Devanagari + Latin
    if _detect_code_mixed(text):
        logger.info(f"Detected code-mixed (Devanagari + Latin): {text[:50]}...")
        return "hi-mix"

    # Check for Romanized Hindi (Latin script with Hindi words)
    has_devanagari = bool(_DEVANAGARI_PATTERN.search(text))
    if not has_devanagari and _detect_romanized_hindi(text):
        logger.info(f"Detected Romanized Hindi: {text[:50]}...")
        return "hi-mix"

    # Use langdetect for non-mixed text
    try:
        from langdetect import detect as langdetect_detect
        lang_code = langdetect_detect(text)
        result = _LANG_MAP.get(lang_code, "en")
        logger.info(f"langdetect returned '{lang_code}' -> mapped to '{result}'")
        return result
    except Exception as e:
        logger.warning(f"langdetect failed: {e}, defaulting to 'en'")
        return "en"


def language_detector_node(state: NavigationState) -> Dict:
    """LangGraph Node 2: Detect the language of the query.

    Args:
        state: Current navigation state with query_text.

    Returns:
        State update with detected_language.
    """
    logger.info("Node 2: Language detection")
    text = state.get("query_text", "")
    lang = detect_language(text)
    logger.info(f"Detected language: {lang} for text: {text[:50]}...")
    return {"detected_language": lang}
