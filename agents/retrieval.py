"""Node 4: Semantic retrieval from Qdrant.

v2 adds:
- Fix 4: Low-confidence handling — when top score < 0.40, ask to rephrase
- Rephrase messages in all 4 languages
"""

import logging
from typing import Dict

from agents.state import NavigationState
from core.qdrant_client import QdrantManager
from core.embeddings import EmbeddingManager
from core.config import Config

logger = logging.getLogger(__name__)

_qdrant: QdrantManager = None
_embedder: EmbeddingManager = None

REPHRASE_RESPONSES: Dict[str, str] = {
    "hi": (
        "Kripya apna sawaal aur clearly puchhein. "
        "For example: 'Cardiology department kahaan hai?' "
        "ya 'Blood test kahan hota hai?'"
    ),
    "mr": (
        "कृपया आपला प्रश्न अधिक स्पष्टपणे विचारा. "
        "उदाहरण: 'Cardiology कुठे आहे?' किंवा 'Blood test कुठे होतो?'"
    ),
    "en": (
        "I didn't understand that. Could you please rephrase? "
        "For example: 'Where is cardiology?' or 'Where do I get a blood test?'"
    ),
    "hi-mix": (
        "Samjha nahi. Please clearly poochhein — "
        "jaise 'Cardiology department kahaan hai?' "
        "ya 'Blood test kahan hota hai?'"
    ),
}


def init_retrieval(
    qdrant_manager: QdrantManager,
    embedding_manager: EmbeddingManager,
) -> None:
    """Initialize the retrieval module with dependencies.

    Args:
        qdrant_manager: Initialized QdrantManager instance.
        embedding_manager: Initialized EmbeddingManager instance.
    """
    global _qdrant, _embedder
    _qdrant = qdrant_manager
    _embedder = embedding_manager
    logger.info("Retrieval module initialized")


def retrieval_node(state: NavigationState) -> Dict:
    """Retrieve top-k candidate locations from Qdrant semantic collection.

    Disambiguation logic:
    - If top score >= DISAMBIGUATION_THRESHOLD AND gap >= 0.15: auto-resolve.
    - If top score < LOW_CONFIDENCE_THRESHOLD: ask to rephrase (Fix 4).
    - Otherwise: trigger disambiguation.

    Args:
        state: Current navigation state with query_text.

    Returns:
        State update with candidate_nodes, requires_disambiguation,
        confidence_scores, and optionally low_confidence + rephrase_message.
    """
    query = state.get("query_text", "")
    logger.info(f"Node 4: Retrieving candidates for: {query[:50]}...")

    # Initialize v2 fields
    base_result: Dict = {
        "low_confidence": False,
        "rephrase_message": None,
    }

    if _qdrant is None or _embedder is None:
        logger.error("Retrieval module not initialized")
        return {
            **base_result,
            "candidate_nodes": [],
            "requires_disambiguation": False,
            "confidence_scores": [],
        }

    try:
        query_vector = _embedder.encode(query)
    except RuntimeError as e:
        logger.error(f"Query encoding failed: {e}")
        return {
            **base_result,
            "candidate_nodes": [],
            "requires_disambiguation": False,
            "confidence_scores": [],
        }

    try:
        results = _qdrant.search(
            collection_name=Config.SEMANTIC_COLLECTION,
            query_vector=query_vector,
            limit=Config.MAX_RETRIEVAL_CANDIDATES,
        )
    except RuntimeError as e:
        logger.error(f"Qdrant search failed: {e}")
        return {
            **base_result,
            "candidate_nodes": [],
            "requires_disambiguation": False,
            "confidence_scores": [],
        }

    if not results:
        logger.warning("No candidates found")
        return {
            **base_result,
            "candidate_nodes": [],
            "requires_disambiguation": False,
            "confidence_scores": [],
        }

    top_score = results[0]["score"]
    second_score = results[1]["score"] if len(results) > 1 else 0.0
    confidence_scores = [r["score"] for r in results]

    # Fix 4: Low-confidence — ask patient to rephrase
    if top_score < Config.LOW_CONFIDENCE_THRESHOLD:
        lang = state.get("detected_language", "en")
        rephrase_msg = REPHRASE_RESPONSES.get(lang, REPHRASE_RESPONSES["en"])
        logger.warning(
            f"Low confidence retrieval: top_score={top_score:.4f} "
            f"(threshold={Config.LOW_CONFIDENCE_THRESHOLD})"
        )
        return {
            "candidate_nodes": [],
            "requires_disambiguation": False,
            "confidence_scores": confidence_scores,
            "low_confidence": True,
            "rephrase_message": rephrase_msg,
        }

    # Standard disambiguation check
    requires_disambiguation = (
        top_score < Config.DISAMBIGUATION_THRESHOLD
        or (top_score - second_score) < Config.DISAMBIGUATION_GAP
    )

    logger.info(
        f"Found {len(results)} candidates, top={top_score:.4f}, "
        f"second={second_score:.4f}, disambiguation={requires_disambiguation}"
    )

    return {
        **base_result,
        "candidate_nodes": results,
        "requires_disambiguation": requires_disambiguation,
        "confidence_scores": confidence_scores,
    }
