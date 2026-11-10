"""Node 5: Disambiguation — conditional node for clarifying questions.

When semantic retrieval returns multiple candidates with close scores,
this node generates a clarifying question in the detected language
asking the patient to choose between options.

This handles the Indian name ambiguity problem: multiple doctors
with the same surname (Dr. Mehta in Cardiology vs Dr. Mehta in
Gynaecology), or overlapping procedure names.
"""

import logging
from typing import Dict, List, Optional

from agents.state import NavigationState
from core.graph import SpatialGraph
from core.config import Config

logger = logging.getLogger(__name__)

# Injected at startup
_spatial_graph: SpatialGraph = None


def init_disambiguation(graph: SpatialGraph) -> None:
    """Initialize with spatial graph for resolving display names.

    Args:
        graph: Loaded SpatialGraph instance.
    """
    global _spatial_graph
    _spatial_graph = graph
    logger.info("Disambiguation module initialized")


# Disambiguation question templates by language
_DISAMBIGUATION_TEMPLATES = {
    "en": "Did you mean {option_1} or {option_2}?",
    "hi": "Kya aap {option_1} ya {option_2} se milna chahte hain?",
    "mr": "तुम्हाला {option_1} किंवा {option_2} यांना भेटायचे आहे का?",
    "hi-mix": "Kya aap {option_1} ya {option_2} se milna chahte hain?",
}


def _build_option_display(
    candidate: Dict,
    graph: Optional[SpatialGraph],
) -> str:
    """Build a human-readable display string for a candidate node.

    Args:
        candidate: A Qdrant search result dict with payload.
        graph: Optional spatial graph for node metadata.

    Returns:
        Display string like "Cardiology OPD" or "Dr. Mehta (Cardiology)".
    """
    payload = candidate.get("payload", {})
    canonical_id = payload.get("canonical_node_id", "")
    alias_text = payload.get("alias_text", canonical_id)

    if graph is not None:
        try:
            node_data = graph.get_node_data(canonical_id)
            display_name = node_data.get("display_name", alias_text)
            floor = node_data.get("floor")
            if floor:
                return f"{display_name} (Floor {floor})"
            return display_name
        except KeyError:
            pass

    return alias_text


def disambiguation_node(state: NavigationState) -> Dict:
    """Generate a clarifying question when retrieval is ambiguous.

    This node only runs when requires_disambiguation is True.
    It presents the top candidates as options and lets the patient
    choose. After the patient responds, the workflow re-runs retrieval
    with the clarified query.

    For the initial implementation, we auto-resolve to the top
    candidate and add a warning. A real interactive system would
    pause and wait for user input here.

    Args:
        state: Navigation state with candidate_nodes and detected_language.

    Returns:
        State update with disambiguation_question, disambiguation_options,
        and resolved_node_id.
    """
    logger.info("Node 5: Disambiguation")

    candidates = state.get("candidate_nodes", [])
    language = state.get("detected_language", "en")

    if not candidates:
        logger.warning("No candidates for disambiguation")
        return {
            "resolved_node_id": None,
            "disambiguation_question": None,
            "disambiguation_options": None,
        }

    # Build options from top candidates
    options: List[Dict] = []
    seen_nodes = set()
    for candidate in candidates[:3]:
        payload = candidate.get("payload", {})
        canonical_id = payload.get("canonical_node_id")
        if canonical_id and canonical_id not in seen_nodes:
            display = _build_option_display(candidate, _spatial_graph)
            options.append({
                "display": display,
                "node_id": canonical_id,
            })
            seen_nodes.add(canonical_id)

    # Generate question
    if len(options) >= 2:
        template = _DISAMBIGUATION_TEMPLATES.get(
            language, _DISAMBIGUATION_TEMPLATES["en"]
        )
        question = template.format(
            option_1=options[0]["display"],
            option_2=options[1]["display"],
        )
    else:
        question = None
        options = None

    # For now, auto-resolve to top candidate (interactive mode would pause here)
    resolved_node_id = candidates[0]["payload"].get("canonical_node_id")
    logger.info(
        f"Disambiguation: {len(options) if options else 0} options, "
        f"auto-resolving to {resolved_node_id}"
    )

    return {
        "disambiguation_question": question,
        "disambiguation_options": options,
        "resolved_node_id": resolved_node_id,
    }
