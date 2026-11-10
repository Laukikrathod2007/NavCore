"""Node 3: Intent classification using rule-based pattern matching.

v2 adds:
- Fix 5: Multi-destination detection — "pehle X phir Y" style queries
"""

import logging
import re
from typing import Dict, List

from agents.state import NavigationState

logger = logging.getLogger(__name__)

# Intent patterns — more specific first
_INTENT_PATTERNS = [
    {
        "intent": "current_location_query",
        "patterns": [
            r"\bwhere am i\b",
            r"\bmy location\b",
            r"\bwhere is this\b",
        ],
    },
    {
        "intent": "doctor_query",
        "patterns": [
            r"\bdr\.?\s+\w+",
            r"\bdoctor\s+\w+",
            r"\bdr\s+\w+",
            r"\bmehta\b",
            r"\bdeshpande\b",
            r"\bpatil\b",
            r"\bsharma\b",
            r"\bmilna hai\b",
            r"\bmilenge\b",
        ],
    },
    {
        "intent": "procedure_query",
        "patterns": [
            r"\bx-?ray\b",
            r"\bmri\b",
            r"\bct scan\b",
            r"\becg\b",
            r"\becho\b",
            r"\bblood test\b",
            r"\bultrasound\b",
            r"\bkarwana\b",
            r"\btest\s+karah?na\b",
            r"\bscan\b",
            r"\bimaging\b",
        ],
    },
]

_DEFAULT_INTENT = "destination_query"

# Fix 5: Multi-destination connectors in all 4 languages
_MULTI_DESTINATION_CONNECTORS: List[str] = [
    # Hinglish / Hindi
    "phir", "aur phir", "uske baad", "bad mein", "baad mein",
    "pehle", "pahle",
    # Marathi
    "nantarach", "nantar", "mag", "aani mag",
    "पहिले", "नंतर", "मग", "आणि मग",
    # English
    "and then", "after that", "then go to", "followed by",
    "first", "first go to",
]


def detect_multi_destination(query: str) -> bool:
    """Check if query mentions two destinations (Fix 5).

    Args:
        query: User query text.

    Returns:
        True if multi-destination connectors are present.
    """
    query_lower = query.lower()
    return any(
        connector in query_lower
        for connector in _MULTI_DESTINATION_CONNECTORS
    )


def split_multi_destination_query(query: str) -> tuple[str, str]:
    """Split a multi-destination query into two non-empty destination parts.

    Finds the connector that creates two non-empty meaningful parts.
    Prefers connectors that appear in the middle (not at position 0).

    Args:
        query: Query text containing a connector.

    Returns:
        Tuple of (first_destination_query, second_destination_query).
    """
    query_lower = query.lower()
    best_idx = -1
    best_connector = ""

    # Find the connector that splits into two non-empty parts
    # Sort by length descending to match longer connectors first (e.g. "and then" before "then")
    for connector in sorted(_MULTI_DESTINATION_CONNECTORS, key=len, reverse=True):
        idx = query_lower.find(connector)
        # Must be in the middle (not at position 0) and give non-empty parts
        if idx > 0:
            part1_candidate = query[:idx].strip().rstrip(",")
            part2_candidate = query[idx + len(connector):].strip()
            if part1_candidate and part2_candidate:
                # Prefer the earliest valid split
                if best_idx == -1 or idx < best_idx:
                    best_idx = idx
                    best_connector = connector

    if best_idx > 0 and best_connector:
        part1 = query[:best_idx].strip().rstrip(",")
        part2 = query[best_idx + len(best_connector):].strip()
        return part1, part2

    # Fallback: split at comma
    parts = query.split(",", 1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (query, "")


def classify_intent(text: str) -> str:
    """Classify the intent of a navigation query.

    Args:
        text: The query text.

    Returns:
        One of: destination_query, procedure_query, doctor_query,
        current_location_query, general_info_query.
    """
    text_lower = text.lower()

    for spec in _INTENT_PATTERNS:
        for pattern in spec["patterns"]:
            if re.search(pattern, text_lower):
                logger.info(f"Intent: {spec['intent']} (matched: {pattern})")
                return spec["intent"]

    if any(
        marker in text_lower
        for marker in ["where is", "kahaan", "kaha", "kuthe", "where can"]
    ):
        logger.info("Intent: destination_query (location marker)")
        return "destination_query"

    logger.info(f"Intent: {_DEFAULT_INTENT} (default)")
    return _DEFAULT_INTENT


def _extract_entities(text: str) -> Dict:
    """Extract simple entities (doctors, rooms, floors, procedures).

    Args:
        text: The query text.

    Returns:
        Dict with extracted entities.
    """
    entities: Dict = {
        "doctors": [],
        "rooms": [],
        "floors": [],
        "procedures": [],
    }

    text_lower = text.lower()

    doctor_match = re.findall(
        r"[Dd]r\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text
    )
    if doctor_match:
        entities["doctors"] = doctor_match

    for surname in ["mehta", "sharma", "deshpande", "patil"]:
        if surname in text_lower:
            if surname.capitalize() not in entities["doctors"]:
                entities["doctors"].append(surname.capitalize())

    room_match = re.findall(r"\broom\s+(\d+[a-z]?)\b", text_lower)
    if room_match:
        entities["rooms"] = room_match

    floor_match = re.findall(r"\b(\d)(?:st|nd|rd|th)?\s+floor\b", text_lower)
    if floor_match:
        entities["floors"] = floor_match

    for proc in [
        "ecg", "echo", "mri", "x-ray", "xray", "ct scan",
        "blood test", "ultrasound", "angiography", "stress test",
    ]:
        if proc in text_lower:
            entities["procedures"].append(proc)

    return entities


def intent_classifier_node(state: NavigationState) -> Dict:
    """LangGraph Node 3: Classify the query intent.

    Also detects multi-destination queries (Fix 5) and stores
    the second destination query for later retrieval.

    Args:
        state: Current navigation state with query_text.

    Returns:
        State update with intent, extracted_entities, and
        multi_destination flag.
    """
    logger.info("Node 3: Intent classification")
    text = state.get("query_text", "")

    intent = classify_intent(text)
    entities = _extract_entities(text)

    # Fix 5: Multi-destination detection
    is_multi = detect_multi_destination(text)
    secondary_query = ""

    if is_multi:
        part1, part2 = split_multi_destination_query(text)
        logger.info(
            f"Multi-destination detected: '{part1}' then '{part2}'"
        )
        # Store second query in entities for path_planner to use
        entities["secondary_query"] = part2

    logger.info(
        f"Intent: {intent}, Multi-dest: {is_multi}, Entities: {entities}"
    )

    return {
        "intent": intent,
        "extracted_entities": entities,
        "multi_destination": is_multi,
    }
