"""LangGraph state definition for the navigation workflow.

Each node reads from this state and writes specific fields back.
No node reads or writes fields outside its responsibility.
"""

from typing import TypedDict, Optional, List, Dict


class NavigationState(TypedDict):
    """Shared state passed through all 7 nodes of the LangGraph workflow.

    Attributes:
        query_text: The patient's navigation query (text).
        input_modality: How the query arrived — "text", "audio", or "qr".
        current_location: Node ID where the patient is now.

        detected_language: ISO code — "hi", "mr", "en", or "hi-mix".

        intent: Classified intent type.
        extracted_entities: Dict of entities extracted from the query.

        candidate_nodes: Top-k semantic retrieval results from Qdrant.
        requires_disambiguation: Whether clarification is needed.
        confidence_scores: Cosine similarity scores for each candidate.

        disambiguation_question: Clarifying question text (if needed).
        disambiguation_options: List of options for the patient.
        resolved_node_id: The final destination node ID after resolution.

        path_nodes: Ordered list of node IDs from start to destination.
        junction_nodes_in_path: Junction nodes in path (degree >= 3).
        warnings: Non-blocking warnings (e.g., doctor unavailable).

        directions_text: Natural language directions from Llama 3.2.
        directions_audio: Audio file path if TTS was requested.
        destination_display_name: Human-readable name of destination.

        latency_ms: Total processing time in milliseconds.
        query_id: Optional unique identifier for tracking.

        # v2 fields
        low_confidence: True when retrieval score < LOW_CONFIDENCE_THRESHOLD.
        rephrase_message: Message asking patient to rephrase in their language.
        path_error: Reason for empty path (e.g. "No path found", "Node not in graph").
        multi_destination: True when query contains two destinations.
        secondary_node_id: Second destination node ID for multi-destination queries.
        is_multi_destination: True when path covers two destinations sequentially.
        location_extracted_from_query: True when current_location was parsed from query text.
    """

    # Input
    query_text: str
    input_modality: str  # "text", "audio", "qr"
    current_location: Optional[str]

    # Language detection (Node 2)
    detected_language: str  # "hi", "mr", "en", "hi-mix"

    # Intent classification (Node 3)
    intent: str
    extracted_entities: Dict

    # Semantic retrieval (Node 4)
    candidate_nodes: List[Dict]
    requires_disambiguation: bool
    confidence_scores: List[float]

    # Disambiguation (Node 5 — conditional)
    disambiguation_question: Optional[str]
    disambiguation_options: Optional[List[Dict]]
    resolved_node_id: Optional[str]

    # Path planning (Node 6)
    path_nodes: List[str]
    junction_nodes_in_path: List[str]
    warnings: List[str]

    # Direction generation (Node 7)
    directions_text: str
    directions_audio: Optional[str]
    destination_display_name: str

    # Metadata
    latency_ms: float
    query_id: Optional[str]

    # v2 — Fix 4: Low-confidence retrieval
    low_confidence: bool
    rephrase_message: Optional[str]

    # v2 — Fix 2: No-path-found
    path_error: Optional[str]

    # v2 — Fix 5: Multi-destination
    multi_destination: bool
    secondary_node_id: Optional[str]
    is_multi_destination: bool

    # v2 — Fix 3: Verbal location extraction
    location_extracted_from_query: bool
