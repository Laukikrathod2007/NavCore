"""LangGraph workflow definition — wires all 7 nodes.

v2: Adds secondary destination resolution for multi-destination queries.
"""

import logging
from typing import Optional, Dict

from langgraph.graph import StateGraph, END

from agents.state import NavigationState
from agents import (
    input_processor,
    language_detector,
    intent_classifier,
    retrieval,
    disambiguation,
    path_planner,
    direction_generator,
)
from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager

logger = logging.getLogger(__name__)

# Injected at build time for secondary destination lookup
_embedder: Optional[EmbeddingManager] = None
_qdrant: Optional[QdrantManager] = None


def init_workflow_dependencies(
    embedder: EmbeddingManager,
    qdrant: QdrantManager,
) -> None:
    """Inject embedder and qdrant for secondary destination lookup.

    Args:
        embedder: Initialized EmbeddingManager.
        qdrant: Initialized QdrantManager.
    """
    global _embedder, _qdrant
    _embedder = embedder
    _qdrant = qdrant


def _resolve_secondary_destination(secondary_query: str) -> Optional[str]:
    """Resolve a secondary destination query to a node ID.

    Used for multi-destination queries (Fix 5).

    Args:
        secondary_query: The second part of the query.

    Returns:
        canonical_node_id or None.
    """
    if not secondary_query or not _embedder or not _qdrant:
        return None
    try:
        vec = _embedder.encode(secondary_query)
        results = _qdrant.search(
            collection_name=Config.SEMANTIC_COLLECTION,
            query_vector=vec,
            limit=1,
        )
        if results and results[0]["score"] >= Config.LOW_CONFIDENCE_THRESHOLD:
            node_id = results[0]["payload"]["canonical_node_id"]
            logger.info(
                f"Secondary destination resolved: '{secondary_query}' -> {node_id}"
            )
            return node_id
    except Exception as e:
        logger.warning(f"Secondary destination lookup failed: {e}")
    return None


def _inject_secondary_destination(state: NavigationState) -> Dict:
    """Middle node: resolve secondary destination for multi-destination queries.

    Runs between disambiguation and path_planner. If multi_destination is
    True and extracted_entities has a secondary_query, resolve it.

    Args:
        state: Current navigation state.

    Returns:
        State update with secondary_node_id.
    """
    if not state.get("multi_destination", False):
        return {"secondary_node_id": None}

    entities = state.get("extracted_entities", {})
    secondary_query = entities.get("secondary_query", "")

    if not secondary_query:
        logger.info("Multi-destination but no secondary query found")
        return {"secondary_node_id": None}

    secondary_node = _resolve_secondary_destination(secondary_query)
    return {"secondary_node_id": secondary_node}


def should_disambiguate(state: NavigationState) -> str:
    """Conditional edge: route to disambiguation or path planner.

    Args:
        state: Current navigation state.

    Returns:
        Next node name.
    """
    # Low-confidence — skip to direction generator directly
    if state.get("low_confidence", False):
        logger.info("Routing to direction_generator (low confidence)")
        return "direction_generator"

    if state.get("requires_disambiguation", False):
        logger.info("Routing to disambiguation")
        return "disambiguation"

    candidates = state.get("candidate_nodes", [])
    if candidates:
        logger.info("No disambiguation needed, proceeding to secondary_resolver")
        return "secondary_resolver"

    logger.warning("No candidates found")
    return "direction_generator"


def build_workflow():
    """Build and compile the LangGraph navigation workflow.

    Nodes:
        input_processor → language_detector → intent_classifier
        → retrieval → (conditional) → disambiguation → secondary_resolver
        → path_planner → direction_generator → END

    Returns:
        Compiled LangGraph runnable.
    """
    workflow = StateGraph(NavigationState)

    # Add all nodes
    workflow.add_node("input_processor",    input_processor.input_processor_node)
    workflow.add_node("language_detector",  language_detector.language_detector_node)
    workflow.add_node("intent_classifier",  intent_classifier.intent_classifier_node)
    workflow.add_node("retrieval",          retrieval.retrieval_node)
    workflow.add_node("disambiguation",     disambiguation.disambiguation_node)
    workflow.add_node("secondary_resolver", _inject_secondary_destination)
    workflow.add_node("path_planner",       path_planner.path_planner_node)
    workflow.add_node("direction_generator", direction_generator.direction_generator_node)

    # Linear edges
    workflow.set_entry_point("input_processor")
    workflow.add_edge("input_processor",    "language_detector")
    workflow.add_edge("language_detector",  "intent_classifier")
    workflow.add_edge("intent_classifier",  "retrieval")

    # Conditional: retrieval → disambiguation / secondary_resolver / direction_generator
    workflow.add_conditional_edges(
        "retrieval",
        should_disambiguate,
        {
            "disambiguation":     "disambiguation",
            "secondary_resolver": "secondary_resolver",
            "direction_generator": "direction_generator",
        },
    )

    # Disambiguation → secondary_resolver
    workflow.add_edge("disambiguation",     "secondary_resolver")

    # Secondary resolver → path_planner → direction_generator → END
    workflow.add_edge("secondary_resolver", "path_planner")
    workflow.add_edge("path_planner",       "direction_generator")
    workflow.add_edge("direction_generator", END)

    compiled = workflow.compile()
    logger.info("LangGraph workflow compiled (8 nodes with secondary resolver)")
    return compiled
