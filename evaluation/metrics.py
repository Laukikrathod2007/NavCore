"""Metrics calculation for NavCore benchmark.

Calculates destination accuracy, path accuracy, junction accuracy,
and per-language breakdown across all test queries.
"""

import logging
from typing import List, Dict
import statistics

logger = logging.getLogger(__name__)


def calculate_destination_accuracy(results: List[Dict]) -> float:
    """Calculate the fraction of queries with correct destination.

    Args:
        results: List of result dicts with 'destination_correct' field.

    Returns:
        Destination accuracy as a float between 0 and 1.
    """
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get("destination_correct"))
    return correct / len(results)


def calculate_path_accuracy(results: List[Dict]) -> float:
    """Calculate the fraction of queries with correct full path.

    Args:
        results: List of result dicts with 'path_correct' field.

    Returns:
        Path accuracy as a float between 0 and 1.
    """
    if not results:
        return 0.0
    correct = sum(1 for r in results if r.get("path_correct"))
    return correct / len(results)


def calculate_junction_accuracy(results: List[Dict], graph=None) -> float:
    """Calculate correct next-edge choices at annotated route junctions.

    For every expected junction with a following node in the reference
    path, compare the predicted path's next node after that junction with
    the reference next node. Missing junctions and routes count as wrong.

    Args:
        results: List of result dicts with 'path_nodes' (or 'predicted_path'),
                 'expected_path', and 'expected_junctions'.
        graph: Optional SpatialGraph instance for additional verification.

    Returns:
        Junction accuracy as a float between 0 and 1.
    """
    correct_choices = 0
    total_choices = 0

    for r in results:
        expected_junctions = r.get("expected_junctions", [])
        expected_path = r.get("expected_path", [])
        actual_path = r.get("path_nodes", r.get("predicted_path", []))

        if not expected_junctions or not expected_path:
            continue

        for junction in expected_junctions:
            try:
                expected_index = expected_path.index(junction)
            except ValueError:
                continue
            if expected_index + 1 >= len(expected_path):
                continue

            total_choices += 1
            expected_next = expected_path[expected_index + 1]
            try:
                actual_index = actual_path.index(junction)
            except ValueError:
                continue
            if actual_index + 1 < len(actual_path):
                if actual_path[actual_index + 1] == expected_next:
                    correct_choices += 1

    return correct_choices / total_choices if total_choices > 0 else 0.0


def calculate_language_breakdown(
    results: List[Dict],
    metric: str = "destination_correct",
) -> Dict[str, float]:
    """Calculate accuracy broken down by language.

    Args:
        results: List of result dicts with 'language' and metric fields.
        metric: Field name to check (e.g. 'destination_correct').

    Returns:
        Dict mapping language code to accuracy.
    """
    lang_results: Dict[str, List[bool]] = {}

    for r in results:
        lang = r.get("language", "unknown")
        if lang not in lang_results:
            lang_results[lang] = []
        lang_results[lang].append(bool(r.get(metric, False)))

    return {
        lang: round(sum(vals) / len(vals), 4)
        for lang, vals in lang_results.items()
        if vals
    }


def calculate_latency_percentiles(results: List[Dict]) -> Dict[str, float]:
    """Calculate P50 and P95 latency from result list.

    Args:
        results: List of result dicts with 'latency_ms' field.

    Returns:
        Dict with avg_latency_ms, p50_latency_ms, p95_latency_ms.
    """
    latencies = sorted(
        r.get("latency_ms", 0) for r in results if r.get("latency_ms", 0) > 0
    )
    if not latencies:
        return {"avg_latency_ms": 0.0, "p50_latency_ms": 0.0, "p95_latency_ms": 0.0}

    p50_idx = int(len(latencies) * 0.50)
    p95_idx = int(len(latencies) * 0.95)

    return {
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
        "p50_latency_ms": round(latencies[min(p50_idx, len(latencies) - 1)], 2),
        "p95_latency_ms": round(latencies[min(p95_idx, len(latencies) - 1)], 2),
    }


def calculate_all_metrics(results: List[Dict], graph=None) -> Dict:
    """Calculate all benchmark metrics from a list of results.

    Args:
        results: List of result dicts from a benchmark condition.
        graph: Optional SpatialGraph for junction verification.

    Returns:
        Dict with all metrics in the standard benchmark output schema.
    """
    total = len(results)

    dest_acc = calculate_destination_accuracy(results)
    path_acc = calculate_path_accuracy(results)
    junction_acc = calculate_junction_accuracy(results, graph)
    lang_dest = calculate_language_breakdown(results, "destination_correct")
    latency = calculate_latency_percentiles(results)

    metrics = {
        "total_queries": total,
        "destination_accuracy": round(dest_acc, 4),
        "path_accuracy": round(path_acc, 4),
        "junction_accuracy": round(junction_acc, 4),
        "language_accuracy": {
            k: round(v, 4) for k, v in lang_dest.items()
        },
        **latency,
    }

    logger.info(
        f"Metrics: dest={dest_acc:.2%}, path={path_acc:.2%}, "
        f"junction={junction_acc:.2%}, P50={latency['p50_latency_ms']:.0f}ms"
    )

    return metrics
