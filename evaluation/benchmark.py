"""Run the NavCore benchmark across three conditions.

Condition A: Keyword baseline   — exact string match, no embeddings
Condition B: Flat semantic      — embeddings + LLM, no graph BFS
Condition C: NavCore            — embeddings + graph BFS + LLM

Output: evaluation/results/benchmark_results.json with all metrics
and a comparison section showing NavCore delta over flat semantic.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from core.graph import SpatialGraph
from evaluation.metrics import calculate_all_metrics
from evaluation.keyword_baseline import run_keyword_baseline
from evaluation.flat_semantic_baseline import run_flat_semantic_baseline

logger = logging.getLogger(__name__)


def load_test_set(test_set_path: str) -> List[Dict]:
    """Load test queries from JSON.

    Args:
        test_set_path: Path to test_set_200.json.

    Returns:
        List of test query dicts.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    logger.info(f"Loading test set from: {test_set_path}")
    with open(test_set_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
    logger.info(f"Loaded {len(queries)} test queries")
    return queries


def run_navcore_condition(
    test_queries: List[Dict],
    workflow,
) -> List[Dict]:
    """Condition C: Full NavCore dual-memory system.

    Uses the complete LangGraph workflow: semantic retrieval + graph BFS
    + LLM direction generation. The path is deterministic, never hallucinated.

    Args:
        test_queries: List of test query dicts.
        workflow: Compiled LangGraph workflow.

    Returns:
        List of result dicts.
    """
    logger.info(f"Running NavCore on {len(test_queries)} queries")
    results = []

    for q in test_queries:
        start_time = time.time()

        try:
            initial_state = {
                "query_text": q["query_text"],
                "input_modality": "text",
                "current_location": Config.DEFAULT_START_NODE,
            }
            output = workflow.invoke(initial_state)
        except Exception as e:
            logger.error(f"Workflow failed for {q['query_id']}: {e}")
            results.append({
                "query_id": q["query_id"],
                "query_text": q["query_text"],
                "language": q["language"],
                "expected_destination": q["expected_destination_node"],
                "predicted_destination": None,
                "destination_correct": False,
                "path_correct": False,
                "path_nodes": [],
                "predicted_path": [],
                "expected_junctions": q.get("junction_nodes_in_path", []),
                "directions": "",
                "latency_ms": (time.time() - start_time) * 1000,
            })
            continue

        predicted_dest = output.get("resolved_node_id")
        predicted_path = output.get("path_nodes", [])
        latency_ms = (time.time() - start_time) * 1000

        results.append({
            "query_id": q["query_id"],
            "query_text": q["query_text"],
            "language": q["language"],
            "expected_destination": q["expected_destination_node"],
            "predicted_destination": predicted_dest,
            "destination_correct": predicted_dest == q["expected_destination_node"],
            "path_correct": predicted_path == q["expected_path"],
            "path_nodes": predicted_path,
            "predicted_path": predicted_path,
            "expected_path": q["expected_path"],
            "expected_junctions": q.get("junction_nodes_in_path", []),
            "directions": output.get("directions_text", ""),
            "latency_ms": round(latency_ms, 2),
        })

    correct = sum(1 for r in results if r["destination_correct"])
    logger.info(
        f"NavCore: {correct}/{len(results)} correct ({correct/len(results):.1%})"
    )
    return results


def run_benchmark(
    test_set_path: str = None,
    qdrant: QdrantManager = None,
    embedder: EmbeddingManager = None,
    graph: SpatialGraph = None,
    workflow=None,
) -> Dict:
    """Run the full benchmark across all three conditions.

    Initializes dependencies if not provided, loads the test set,
    runs all three conditions, calculates metrics, and saves results.

    Args:
        test_set_path: Path to test set JSON. Defaults to standard path.
        qdrant: Optional pre-initialized QdrantManager.
        embedder: Optional pre-initialized EmbeddingManager.
        graph: Optional pre-loaded SpatialGraph.
        workflow: Optional compiled LangGraph workflow.

    Returns:
        Dict with results and metrics for all three conditions.
    """
    if test_set_path is None:
        test_set_path = str(
            Path(Config.PROJECT_ROOT) / "evaluation" / "test_set_200.json"
        )

    test_queries = load_test_set(test_set_path)
    total = len(test_queries)
    logger.info(f"Benchmark starting: {total} queries, 3 conditions")

    # Initialize dependencies if not provided
    if qdrant is None:
        qdrant = QdrantManager()
    if embedder is None:
        embedder = EmbeddingManager()
    if graph is None:
        graph = SpatialGraph()
        graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

    aliases_path = f"{Config.DATA_DIR}/aliases.json"

    # Load graph data for flat semantic baseline
    with open(f"{Config.DATA_DIR}/graph.json", "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    # Try to get Ollama for flat semantic (optional)
    ollama = None
    if workflow is None:
        # Running standalone — try to init all dependencies
        from core.ollama_client import OllamaManager
        from agents.retrieval import init_retrieval
        from agents.path_planner import init_path_planner
        from agents.direction_generator import init_direction_generator
        from agents.disambiguation import init_disambiguation
        from agents.workflow import build_workflow

        try:
            ollama = OllamaManager()
            if not ollama.check_health():
                logger.warning("Ollama not available, flat semantic will skip LLM")
                ollama = None
        except Exception:
            logger.warning("Ollama not available, flat semantic will skip LLM")

        init_retrieval(qdrant, embedder)
        init_path_planner(graph)
        init_direction_generator(ollama, graph)
        init_disambiguation(graph)
        workflow = build_workflow()
    else:
        # Try to get ollama from direction generator module
        try:
            from agents.direction_generator import _ollama as existing_ollama
            ollama = existing_ollama
        except Exception:
            pass

    # ── Condition A: Keyword baseline ────────────────────────────────
    logger.info("=" * 50)
    logger.info("Condition A: Keyword baseline")
    keyword_results = run_keyword_baseline(test_queries, _load_aliases(aliases_path))
    keyword_metrics = calculate_all_metrics(keyword_results, graph)

    # ── Condition B: Flat semantic ────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Condition B: Flat semantic retrieval")
    flat_results = run_flat_semantic_baseline(
        test_queries, qdrant, embedder, ollama, graph_data
    )
    flat_metrics = calculate_all_metrics(flat_results, graph)

    # ── Condition C: NavCore ──────────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Condition C: NavCore dual-memory")
    navcore_results = run_navcore_condition(test_queries, workflow)
    navcore_metrics = calculate_all_metrics(navcore_results, graph)

    # ── Comparison ────────────────────────────────────────────────────
    delta_dest = navcore_metrics["destination_accuracy"] - flat_metrics["destination_accuracy"]
    delta_junc = navcore_metrics["junction_accuracy"] - flat_metrics["junction_accuracy"]
    delta_path = navcore_metrics["path_accuracy"] - flat_metrics["path_accuracy"]

    comparison = {
        "destination_accuracy_delta": (
            f"NavCore is +{delta_dest*100:.1f}pp over flat semantic"
            if delta_dest >= 0
            else f"NavCore is {delta_dest*100:.1f}pp under flat semantic"
        ),
        "junction_accuracy_delta": (
            f"NavCore is +{delta_junc*100:.1f}pp over flat semantic"
            if delta_junc >= 0
            else f"NavCore is {delta_junc*100:.1f}pp under flat semantic"
        ),
        "path_accuracy_delta": (
            f"NavCore is +{delta_path*100:.1f}pp over flat semantic (flat has no path)"
            if delta_path >= 0
            else f"NavCore is {delta_path*100:.1f}pp under flat semantic"
        ),
        "navcore_beats_flat_semantic": navcore_metrics["destination_accuracy"]
        > flat_metrics["destination_accuracy"],
        "navcore_beats_keyword": navcore_metrics["destination_accuracy"]
        > keyword_metrics["destination_accuracy"],
    }

    # ── Output schema matching the spec ──────────────────────────────
    all_results = {
        "run_metadata": {
            "run_date": datetime.now().isoformat(timespec="seconds"),
            "test_set": Path(test_set_path).name,
            "test_query_count": total,
            "language_counts": {
                language: sum(1 for query in test_queries if query.get("language") == language)
                for language in sorted({query.get("language", "unknown") for query in test_queries})
            },
            "embedding_model": Config.EMBEDDING_MODEL,
            "embedding_dimension": Config.EMBEDDING_DIM,
            "embedding_device": str(getattr(getattr(embedder, "model", None), "device", "unknown")),
            "qdrant_path": Config.QDRANT_PATH,
            "ollama_available": ollama is not None,
            "directions_backend": "ollama" if ollama is not None else "template_fallback",
            "latency_scope": "Workflow invocation after model startup; excludes browser and audio transcription.",
            "junction_metric": "Expected next graph edge at each annotated expected-path junction; missing junction or route counts incorrect.",
        },
        "keyword_baseline": {
            "destination_accuracy": keyword_metrics["destination_accuracy"],
            "path_accuracy": 0.0,
            "total_queries": total,
            "language_accuracy": keyword_metrics["language_accuracy"],
            "avg_latency_ms": keyword_metrics["avg_latency_ms"],
            "results": keyword_results,
        },
        "flat_semantic": {
            "destination_accuracy": flat_metrics["destination_accuracy"],
            "path_accuracy": 0.0,
            "total_queries": total,
            "language_accuracy": flat_metrics["language_accuracy"],
            "avg_latency_ms": flat_metrics["avg_latency_ms"],
            "results": flat_results,
        },
        "navcore_dual_memory": {
            "destination_accuracy": navcore_metrics["destination_accuracy"],
            "path_accuracy": navcore_metrics["path_accuracy"],
            "junction_accuracy": navcore_metrics["junction_accuracy"],
            "total_queries": total,
            "language_accuracy": navcore_metrics["language_accuracy"],
            "avg_latency_ms": navcore_metrics["avg_latency_ms"],
            "p50_latency_ms": navcore_metrics["p50_latency_ms"],
            "p95_latency_ms": navcore_metrics["p95_latency_ms"],
            "results": navcore_results,
        },
        "comparison": comparison,
    }

    # Save results
    output_dir = Path(Config.PROJECT_ROOT) / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "benchmark_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    logger.info("=" * 50)
    logger.info(f"Benchmark complete. Results saved to {output_path}")
    logger.info(
        f"  Keyword:      {keyword_metrics['destination_accuracy']:.1%} dest accuracy"
    )
    logger.info(
        f"  Flat Semantic:{flat_metrics['destination_accuracy']:.1%} dest accuracy"
    )
    logger.info(
        f"  NavCore:      {navcore_metrics['destination_accuracy']:.1%} dest accuracy"
        f"  ({comparison['destination_accuracy_delta']})"
    )
    logger.info(
        f"  Junction:     {navcore_metrics['junction_accuracy']:.1%}"
        f"  ({comparison['junction_accuracy_delta']})"
    )

    return all_results


def _load_aliases(aliases_path: str) -> list:
    """Load alias data from file."""
    with open(aliases_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    from core.config import setup_logging
    setup_logging()
    run_benchmark()
