"""Flat semantic retrieval baseline — no graph BFS, LLM guesses directions.

This is Condition B in the benchmark. Uses multilingual-e5-small to
find the correct destination (should work well) but then passes only
node metadata to the LLM for direction generation — no computed path.

This isolates the contribution of the graph BFS: Condition B gets the
right destination, but the LLM must invent the route. The 59% junction
failure rate from "Lost in Aggregation" (arxiv 2606.22219) should
manifest here.
"""

import logging
import time
from typing import List, Dict

from core.qdrant_client import QdrantManager
from core.embeddings import EmbeddingManager
from core.ollama_client import OllamaManager
from core.config import Config

logger = logging.getLogger(__name__)


def run_flat_semantic_baseline(
    test_queries: List[Dict],
    qdrant: QdrantManager,
    embedder: EmbeddingManager,
    ollama: OllamaManager,
    graph_data: Dict,
) -> List[Dict]:
    """Run queries through flat semantic RAG without graph pathfinding.

    The LLM receives only destination metadata (floor, wing, room, description)
    and must generate directions on its own without a computed path. This is
    standard RAG — the LLM guesses the route.

    Args:
        test_queries: List of test query dicts.
        qdrant: Initialized QdrantManager.
        embedder: Initialized EmbeddingManager.
        ollama: Initialized OllamaManager (or None for no directions).
        graph_data: Loaded graph.json dict for node metadata.

    Returns:
        List of result dicts.
    """
    logger.info(f"Running flat semantic baseline on {len(test_queries)} queries")
    nodes = graph_data.get("nodes", graph_data.get("locations", {}))
    results = []

    for q in test_queries:
        start_time = time.time()
        query_text = q["query_text"]

        # Embed query
        try:
            query_vector = embedder.encode(query_text)
        except RuntimeError as e:
            logger.error(f"Embedding failed for {q['query_id']}: {e}")
            results.append(_empty_result(q))
            continue

        # Search semantic aliases — same as NavCore up to this point
        try:
            search_results = qdrant.search(
                collection_name=Config.SEMANTIC_COLLECTION,
                query_vector=query_vector,
                limit=1,
            )
        except RuntimeError as e:
            logger.error(f"Qdrant search failed for {q['query_id']}: {e}")
            results.append(_empty_result(q))
            continue

        if not search_results:
            results.append(_empty_result(q))
            continue

        predicted_node_id = search_results[0]["payload"]["canonical_node_id"]
        node_data = nodes.get(predicted_node_id, {})
        dest_name = node_data.get("display_name", predicted_node_id)
        floor = node_data.get("floor", 0)
        wing = node_data.get("wing", "")
        room = node_data.get("room_number", "")
        description = node_data.get("description", "")

        # Let LLM generate directions WITHOUT a computed path
        # This is the key difference from NavCore: no BFS, LLM guesses
        directions = ""
        if ollama is not None:
            prompt = (
                f"A patient wants to go to {dest_name}. "
                f"Location: Floor {floor}"
                + (f", Wing {wing}" if wing else "")
                + (f", Room {room}" if room else "")
                + f". {description}. "
                "Starting from the main entrance, give 2-3 sentence directions."
            )
            try:
                directions = ollama.generate(
                    system_prompt=(
                        "You are a hospital navigation guide. "
                        "Give short, friendly directions."
                    ),
                    user_message=prompt,
                )
            except RuntimeError as e:
                logger.warning(f"LLM failed for {q['query_id']}: {e}")
                directions = f"Go to {dest_name} on Floor {floor}."

        latency_ms = (time.time() - start_time) * 1000
        results.append({
            "query_id": q["query_id"],
            "query_text": query_text,
            "language": q["language"],
            "expected_destination": q["expected_destination_node"],
            "predicted_destination": predicted_node_id,
            "destination_correct": (
                predicted_node_id == q["expected_destination_node"]
            ),
            "path_correct": False,  # No path computed in flat semantic
            "predicted_path": [],
            "expected_junctions": q.get("junction_nodes_in_path", []),
            "directions": directions,
            "latency_ms": round(latency_ms, 2),
        })

    correct = sum(1 for r in results if r["destination_correct"])
    logger.info(
        f"Flat semantic baseline: {correct}/{len(results)} correct "
        f"({correct/len(results):.1%})"
    )
    return results


def _empty_result(q: Dict) -> Dict:
    """Return an empty result dict for a failed query."""
    return {
        "query_id": q["query_id"],
        "query_text": q["query_text"],
        "language": q["language"],
        "expected_destination": q["expected_destination_node"],
        "predicted_destination": None,
        "destination_correct": False,
        "path_correct": False,
        "predicted_path": [],
        "expected_junctions": q.get("junction_nodes_in_path", []),
        "directions": "",
        "latency_ms": 0.0,
    }
