"""Main ingestion pipeline: reads graph.json + aliases.json, embeds, stores in Qdrant.

This is a one-time setup step. After ingestion, the system runs fully offline.

Two Qdrant collections are populated:
1. topological_nodes: one point per graph node, embedding of description
2. semantic_aliases: one point per alias, each resolving to canonical_node_id

Each alias is a separate vector point. This preserves match precision that
averaging would destroy — "dil ke doctor" and "Dr. Mehta" have very different
vector representations but both resolve to cardiology_opd.
"""

import json
import logging
import time
from typing import List, Tuple

from qdrant_client.models import PointStruct

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from core.graph import SpatialGraph

logger = logging.getLogger(__name__)


def load_graph_data(graph_path: str) -> Tuple[dict, SpatialGraph]:
    """Load the spatial graph from JSON.

    Args:
        graph_path: Path to graph.json.

    Returns:
        Tuple of (raw JSON dict, loaded SpatialGraph).

    Raises:
        FileNotFoundError: If file does not exist.
    """
    logger.info(f"Loading graph data from: {graph_path}")
    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    graph = SpatialGraph()
    graph.load_from_json(graph_path)
    return data, graph


def load_aliases(aliases_path: str) -> List[dict]:
    """Load alias definitions from JSON.

    Args:
        aliases_path: Path to aliases.json.

    Returns:
        List of alias entries, each with canonical_node_id, aliases, etc.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    logger.info(f"Loading aliases from: {aliases_path}")
    with open(aliases_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_topological_nodes(
    qdrant: QdrantManager,
    embedder: EmbeddingManager,
    graph_data: dict,
) -> int:
    """Embed and store all topological graph nodes in Qdrant.

    Each node's display_name + description is embedded. The full node
    metadata is stored as payload for retrieval and availability updates.

    Args:
        qdrant: Initialized QdrantManager.
        embedder: Initialized EmbeddingManager.
        graph_data: Raw graph JSON dict with "nodes" key.

    Returns:
        Number of topological nodes ingested.
    """
    qdrant.create_collection(
        Config.TOPOLOGICAL_COLLECTION, Config.EMBEDDING_DIM
    )

    nodes = graph_data["nodes"]
    point_id = 0
    for node_id, node_data in nodes.items():
        description_text = f"{node_data.get('display_name', node_id)} {node_data.get('description', '')}"
        vector = embedder.encode(description_text)
        payload = dict(node_data)
        payload["node_id"] = node_id
        qdrant.upsert_point(
            Config.TOPOLOGICAL_COLLECTION,
            point_id=point_id,
            vector=vector,
            payload=payload,
        )
        point_id += 1

    logger.info(f"Ingested {point_id} topological nodes")
    return point_id


def ingest_semantic_aliases(
    qdrant: QdrantManager,
    embedder: EmbeddingManager,
    aliases: List[dict],
) -> int:
    """Embed and store all semantic aliases in Qdrant.

    Each alias is a separate vector point. One canonical location
    produces many alias vectors. Query retrieves the closest alias,
    then resolves to canonical_node_id via the payload.

    Args:
        qdrant: Initialized QdrantManager.
        embedder: Initialized EmbeddingManager.
        aliases: List of alias entries from aliases.json.

    Returns:
        Number of alias vectors ingested.
    """
    qdrant.create_collection(
        Config.SEMANTIC_COLLECTION, Config.EMBEDDING_DIM
    )

    all_texts: List[str] = []
    all_payloads: List[dict] = []

    for entry in aliases:
        canonical_id = entry["canonical_node_id"]
        for alias in entry["aliases"]:
            all_texts.append(alias)
            all_payloads.append({
                "canonical_node_id": canonical_id,
                "alias_text": alias,
            })

    logger.info(f"Embedding {len(all_texts)} alias vectors...")
    vectors = embedder.encode_batch(all_texts)

    # Upsert in batches of 100 to avoid large requests
    batch_size = 100
    total = 0
    for start in range(0, len(vectors), batch_size):
        end = start + batch_size
        points = []
        for i in range(start, min(end, len(vectors))):
            points.append(
                PointStruct(
                    id=total + (i - start),
                    vector=vectors[i],
                    payload=all_payloads[i],
                )
            )
        qdrant.upsert_batch(Config.SEMANTIC_COLLECTION, points)
        total = len(points) + start

    logger.info(f"Ingested {total} semantic alias vectors")
    return total


def run_ingestion(
    data_dir: str = Config.DATA_DIR,
    qdrant: QdrantManager = None,
    embedder: EmbeddingManager = None,
) -> dict:
    """Run the full ingestion pipeline.

    Reads graph.json and aliases.json, embeds all content, and stores
    in Qdrant Edge. This is the one-time setup step.

    Args:
        data_dir: Path to the hospital data directory.
        qdrant: Optional pre-initialized QdrantManager.
        embedder: Optional pre-initialized EmbeddingManager.

    Returns:
        Dict with counts: topological_nodes, semantic_aliases, total_vectors.
    """
    logger.info("Starting NavCore ingestion pipeline")

    own_qdrant = qdrant is None
    own_embedder = embedder is None

    if own_qdrant:
        qdrant = QdrantManager()
    if own_embedder:
        embedder = EmbeddingManager()

    graph_path = f"{data_dir}/graph.json"
    aliases_path = f"{data_dir}/aliases.json"

    graph_data, graph = load_graph_data(graph_path)
    aliases = load_aliases(aliases_path)

    start_time = time.time()

    topo_count = ingest_topological_nodes(qdrant, embedder, graph_data)
    alias_count = ingest_semantic_aliases(qdrant, embedder, aliases)

    elapsed = time.time() - start_time
    result = {
        "topological_nodes": topo_count,
        "semantic_aliases": alias_count,
        "total_vectors": topo_count + alias_count,
        "elapsed_seconds": round(elapsed, 2),
    }
    logger.info(f"Ingestion complete: {result}")

    return result


if __name__ == "__main__":
    from core.config import setup_logging

    setup_logging()
    run_ingestion()
