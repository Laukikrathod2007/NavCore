"""Keyword matching baseline — no embeddings, no LLM, pure string matching.

This is Condition A in the benchmark. Expected to perform poorly on
synonyms and Hindi/Marathi queries because it only checks if the
exact alias text appears in the query string.
"""

import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


def keyword_match(query: str, aliases_data: List[Dict]) -> Optional[str]:
    """Match query against aliases using simple string containment.

    Sorts aliases by length (longest first) so multi-word aliases like
    "heart doctor" match before single-word aliases like "doctor".

    Args:
        query: User query text.
        aliases_data: List of alias entries from aliases.json.

    Returns:
        canonical_node_id if matched, None otherwise.
    """
    query_lower = query.lower().strip()

    # Build sorted alias list: longest first for better precision
    all_aliases: List[tuple] = []
    for entry in aliases_data:
        for alias in entry.get("aliases", []):
            all_aliases.append((alias.lower(), entry["canonical_node_id"]))
    all_aliases.sort(key=lambda x: len(x[0]), reverse=True)

    for alias_text, node_id in all_aliases:
        if alias_text in query_lower:
            logger.debug(f"Keyword match: '{alias_text}' -> {node_id}")
            return node_id

    return None


def run_keyword_baseline(
    test_queries: List[Dict],
    aliases_data: List[Dict],
) -> List[Dict]:
    """Run all test queries through keyword matching.

    Args:
        test_queries: List of test query dicts from test_set_200.json.
        aliases_data: List of alias entries from aliases.json.

    Returns:
        List of result dicts with destination_correct field.
        path_correct is always False — keyword matching has no path.
    """
    logger.info(f"Running keyword baseline on {len(test_queries)} queries")
    results = []

    for q in test_queries:
        predicted = keyword_match(q["query_text"], aliases_data)
        results.append({
            "query_id": q["query_id"],
            "query_text": q["query_text"],
            "language": q["language"],
            "expected_destination": q["expected_destination_node"],
            "predicted_destination": predicted,
            "destination_correct": predicted == q["expected_destination_node"],
            "path_correct": False,
            "predicted_path": [],
            "expected_junctions": q.get("junction_nodes_in_path", []),
        })

    correct = sum(1 for r in results if r["destination_correct"])
    logger.info(
        f"Keyword baseline: {correct}/{len(results)} correct "
        f"({correct/len(results):.1%})"
    )
    return results
