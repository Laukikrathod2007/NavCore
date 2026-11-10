"""Node 7: Generate natural language directions using Llama 3.2.

v2 adds:
- Fix 2: No-path-found returns language-appropriate reception message
- Fix 4: Low-confidence returns rephrase message (no LLM call)
- Fix 7: Language sanity check with one retry on mismatch
- Multi-destination sequential directions (Fix 5)
"""

import logging
import threading
from typing import Dict, List, Optional

from agents.state import NavigationState
from core.graph import SpatialGraph
from core.config import Config

logger = logging.getLogger(__name__)

_ollama = None
_spatial_graph: SpatialGraph = None

LLM_TIMEOUT_SECONDS = Config.LLM_TIMEOUT_SECONDS

LANGUAGE_INSTRUCTIONS: Dict[str, str] = {
    "hi":     "Reply in Hindi.",
    "mr":     "Reply in Marathi.",
    "en":     "Reply in English.",
    "hi-mix": "Reply in Hinglish (mix Hindi+English).",
}

LANGUAGE_NAMES: Dict[str, str] = {
    "hi":     "Hindi",
    "mr":     "Marathi",
    "en":     "English",
    "hi-mix": "Hinglish (Hindi-English mix)",
}

# Fix 2: Helpful no-path messages per language
NO_PATH_RESPONSES: Dict[str, str] = {
    "hi": (
        "Maafi karen, is jagah ka rasta nahi mil raha. "
        "Kripya reception counter par poochhein — woh aapki madad karenge."
    ),
    "mr": (
        "माफ करा, या ठिकाणाचा रस्ता सापडला नाही. "
        "कृपया reception counter वर विचारा."
    ),
    "en": (
        "Sorry, I could not find a route to that location. "
        "Please ask at the reception counter for assistance."
    ),
    "hi-mix": (
        "Sorry, us location ka rasta nahi mila. "
        "Reception counter pe poochhein please."
    ),
}


def init_direction_generator(
    ollama_manager,
    graph: SpatialGraph,
) -> None:
    """Initialize with Ollama and spatial graph dependencies.

    Args:
        ollama_manager: Initialized OllamaManager instance (or None).
        graph: Loaded SpatialGraph instance.
    """
    global _ollama, _spatial_graph
    _ollama = ollama_manager
    _spatial_graph = graph
    logger.info("Direction generator initialized")


def _build_compact_context(path_nodes: List[str], graph: SpatialGraph) -> str:
    """Build the shortest useful context string for the LLM.

    Args:
        path_nodes: List of node IDs in the path.
        graph: Loaded spatial graph.

    Returns:
        Compact context string.
    """
    parts = []
    prev_floor = None

    for i, node_id in enumerate(path_nodes):
        data = graph.get_node_data(node_id)
        name = data.get("display_name", node_id)
        floor = data.get("floor", 0)
        landmarks = data.get("landmarks_nearby", [])
        is_junction = graph.get_degree(node_id) >= 3
        room = data.get("room_number")

        part = name
        if floor != prev_floor:
            part += f" [Floor {floor}]"
            prev_floor = floor
        if is_junction and landmarks:
            part += f" near {landmarks[0]}"
        if i == len(path_nodes) - 1 and room:
            part += f" Room {room}"

        parts.append(part)

    return " -> ".join(parts)


def _llm_generate_with_timeout(
    system_prompt: str,
    user_message: str,
    timeout: float,
) -> Optional[str]:
    """Run LLM generation with a hard timeout.

    Args:
        system_prompt: System instructions for the LLM.
        user_message: User message.
        timeout: Max seconds to wait.

    Returns:
        Generated text, or None if timeout exceeded.
    """
    result_container = [None]
    exception_container = [None]

    def _run():
        try:
            result_container[0] = _ollama.generate(
                system_prompt=system_prompt,
                user_message=user_message,
            )
        except Exception as e:
            exception_container[0] = e

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        logger.warning(
            f"LLM generation exceeded {timeout}s timeout, using fallback"
        )
        return None

    if exception_container[0]:
        logger.error(f"LLM generation error: {exception_container[0]}")
        return None

    return result_container[0]


def verify_response_language(response: str, expected_language: str) -> bool:
    """Check if response is in the expected language (Fix 7).

    Uses Unicode character set detection:
    - Devanagari (U+0900–U+097F) for hi/mr
    - Latin for en
    - Any mix for hi-mix

    Args:
        response: Generated text to check.
        expected_language: Expected language code.

    Returns:
        True if response matches expected language, False otherwise.
    """
    if not response:
        return True

    devanagari_count = sum(
        1 for c in response if "\u0900" <= c <= "\u097F"
    )
    total_alpha = sum(1 for c in response if c.isalpha())

    if total_alpha == 0:
        return True

    devanagari_ratio = devanagari_count / total_alpha

    if expected_language in ("hi", "mr"):
        return devanagari_ratio > 0.3
    elif expected_language == "en":
        return devanagari_ratio < 0.1
    else:  # hi-mix — accept any
        return True


def direction_generator_node(state: NavigationState) -> Dict:
    """Convert a computed path into natural language directions.

    Handles these cases in order:
    1. Low-confidence query (Fix 4) → return rephrase message
    2. Empty path with path_error (Fix 2) → language-appropriate reception message
    3. Empty path without error → generic error message
    4. Normal path → LLM directions with language verify (Fix 7) + timeout fallback
    5. Multi-destination (Fix 5) → sequential directions

    Args:
        state: Navigation state with path_nodes and detected_language.

    Returns:
        State update with directions_text and destination_display_name.
    """
    logger.info("Node 7: Direction generation")
    language = state.get("detected_language", "en")

    # Fix 4: Low-confidence — return rephrase message, skip everything else
    if state.get("low_confidence", False):
        msg = state.get("rephrase_message") or (
            "Please rephrase your query more clearly."
        )
        logger.info("Low confidence — returning rephrase message")
        return {
            "directions_text": msg,
            "destination_display_name": "",
        }

    path = state.get("path_nodes", [])

    # Fix 2: No path found — return language-appropriate reception message
    if not path:
        path_error = state.get("path_error")
        if path_error:
            logger.warning(f"No path — error: {path_error}")
        else:
            logger.error("No path in state")
        response = NO_PATH_RESPONSES.get(language, NO_PATH_RESPONSES["en"])
        return {
            "directions_text": response,
            "destination_display_name": "",
        }

    if _spatial_graph is None:
        logger.error("Direction generator not initialized")
        return {
            "directions_text": "System not initialized. Please ask at reception.",
            "destination_display_name": "",
        }

    try:
        compact_context = _build_compact_context(path, _spatial_graph)
    except KeyError as e:
        logger.error(f"Failed to build context: {e}")
        return {
            "directions_text": NO_PATH_RESPONSES.get(language, NO_PATH_RESPONSES["en"]),
            "destination_display_name": "",
        }

    dest_data = _spatial_graph.get_node_data(path[-1])
    dest_name = dest_data.get("display_name", path[-1])

    warnings = state.get("warnings", [])
    is_emergency = "emergency" in (state.get("resolved_node_id") or "")
    is_multi = state.get("is_multi_destination", False)
    warning_prefix = f"NOTE: {warnings[0]} " if warnings else ""
    urgent_prefix = "URGENT. " if is_emergency else ""

    # Try LLM with short prompt + timeout + language verify (Fix 7)
    if _ollama is not None:
        lang_instruction = LANGUAGE_INSTRUCTIONS.get(
            language, LANGUAGE_INSTRUCTIONS["en"]
        )

        multi_note = (
            "This is a TWO-STOP route. Mention both destinations clearly. "
            if is_multi else ""
        )

        system_prompt = (
            f"Hospital guide. {lang_instruction} "
            f"2-3 sentences max. Mention floor changes and landmarks. "
            f"{multi_note}"
        )
        user_message = (
            f"{urgent_prefix}{warning_prefix}"
            f"Path: {compact_context}"
        )

        logger.info(
            f"LLM prompt: {len(system_prompt) + len(user_message)} chars "
            f"(timeout={LLM_TIMEOUT_SECONDS}s)"
        )

        directions = _llm_generate_with_timeout(
            system_prompt=system_prompt,
            user_message=user_message,
            timeout=LLM_TIMEOUT_SECONDS,
        )

        # Fix 7: Language sanity check — retry once if mismatch
        if directions and not verify_response_language(directions, language):
            logger.warning(
                f"Language mismatch detected ({language}), forcing retry"
            )
            lang_name = LANGUAGE_NAMES.get(language, language)
            forced_message = (
                f"IMPORTANT: Respond ONLY in {lang_name}. "
                f"{user_message}"
            )
            directions = _llm_generate_with_timeout(
                system_prompt=system_prompt,
                user_message=forced_message,
                timeout=LLM_TIMEOUT_SECONDS,
            )

        if directions:
            logger.info(f"LLM directions: {directions[:80]}...")
            return {
                "directions_text": directions,
                "destination_display_name": dest_name,
            }

    # Fallback: instant template-based directions
    logger.info("Using fallback template directions")
    directions = _fallback_directions(path, _spatial_graph, warning_prefix, is_multi)
    return {
        "directions_text": directions,
        "destination_display_name": dest_name,
    }


def _fallback_directions(
    path: List[str],
    graph: SpatialGraph,
    prefix: str = "",
    is_multi: bool = False,
) -> str:
    """Generate instant template-based directions without LLM.

    Args:
        path: List of node IDs in the path.
        graph: Loaded spatial graph.
        prefix: Optional warning text to prepend.
        is_multi: Whether this is a two-stop sequential route.

    Returns:
        English directions string.
    """
    parts = []
    prev_floor = None

    for i, node_id in enumerate(path):
        data = graph.get_node_data(node_id)
        name = data.get("display_name", node_id)
        floor = data.get("floor", 0)
        landmarks = data.get("landmarks_nearby", [])
        is_junction = graph.get_degree(node_id) >= 3

        if i == 0:
            parts.append(f"Start at {name}.")
            prev_floor = floor
        elif i == len(path) - 1:
            room = data.get("room_number")
            timing = data.get("timing", "")
            floor_note = f" on Floor {floor}" if floor != prev_floor else ""
            room_note = f", Room {room}" if room else ""
            time_note = (
                f" (Open: {timing})"
                if timing and "24/7" not in timing
                else ""
            )
            label = "Final stop" if is_multi else "Your destination"
            parts.append(
                f"{label}: {name}{floor_note}{room_note}{time_note}."
            )
        else:
            floor_note = ""
            if floor != prev_floor:
                floor_note = f" (Floor {floor})"
                prev_floor = floor
            landmark_note = f" (near {landmarks[0]})" if landmarks else ""
            turn_note = ", turn here" if is_junction else ""
            parts.append(
                f"Go to {name}{floor_note}{landmark_note}{turn_note}."
            )

    text = " ".join(parts)
    return f"{prefix}{text}" if prefix else text
