"""RAGAS evaluation for NavCore direction generation quality.

Measures:
  - Faithfulness: do directions match the retrieved context (path)?
  - Context Precision: was the retrieved context relevant to the query?
  - Answer Relevancy: is the answer relevant to the original question?

RAGAS requires an LLM for evaluation — this runs separately from the
runtime system, used only during research evaluation.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from core.config import Config

logger = logging.getLogger(__name__)


def prepare_ragas_dataset(
    navcore_results: List[Dict],
    output_path: Optional[str] = None,
) -> Dict:
    """Convert NavCore benchmark results into RAGAS evaluation format.

    RAGAS expects: question, answer, contexts, ground_truth.

    Args:
        navcore_results: Results from Condition C (NavCore).
        output_path: Optional path to save the dataset JSON.

    Returns:
        Dict in RAGAS-compatible format.
    """
    ragas_data: Dict[str, List] = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    for r in navcore_results:
        ragas_data["question"].append(r.get("query_text", ""))
        ragas_data["answer"].append(r.get("directions", ""))
        # Context = the path nodes joined as a string
        path = r.get("path_nodes", r.get("predicted_path", []))
        ragas_data["contexts"].append(
            [" -> ".join(path)] if path else ["No path computed"]
        )
        ragas_data["ground_truth"].append(r.get("expected_destination", ""))

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ragas_data, f, indent=2, ensure_ascii=False)
        logger.info(f"RAGAS dataset saved to {output_path}")

    return ragas_data


def run_ragas_evaluation(navcore_results: List[Dict]) -> Dict:
    """Run RAGAS metrics on NavCore direction outputs.

    Args:
        navcore_results: Results from running NavCore on test queries.

    Returns:
        Dictionary with RAGAS metric scores, or error dict if unavailable.
    """
    logger.info("Running RAGAS evaluation")

    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, context_precision, answer_relevancy
    except ImportError as e:
        logger.error(f"RAGAS not installed: {e}. Run: pip install ragas")
        return {"error": "RAGAS not installed. Run: pip install ragas"}

    try:
        from datasets import Dataset
    except ImportError as e:
        logger.error(f"datasets package not installed: {e}")
        return {"error": "datasets not installed. Run: pip install datasets"}

    if not navcore_results:
        logger.warning("No NavCore results to evaluate")
        return {"error": "No results to evaluate"}

    # Filter to results that have directions generated
    results_with_directions = [
        r for r in navcore_results if r.get("directions", "").strip()
    ]
    logger.info(
        f"Running RAGAS on {len(results_with_directions)} results "
        f"with directions (out of {len(navcore_results)} total)"
    )

    if not results_with_directions:
        return {"error": "No directions found in results — run NavCore with Ollama enabled"}

    # Prepare dataset
    dataset_path = str(
        Path(Config.PROJECT_ROOT) / "evaluation" / "results" / "ragas_dataset.json"
    )
    ragas_data = prepare_ragas_dataset(results_with_directions, dataset_path)
    dataset = Dataset.from_dict(ragas_data)

    try:
        result = evaluate(
            dataset,
            metrics=[faithfulness, context_precision, answer_relevancy],
        )
        scores = {
            "faithfulness": round(float(result.get("faithfulness", 0)), 4),
            "context_precision": round(float(result.get("context_precision", 0)), 4),
            "answer_relevancy": round(float(result.get("answer_relevancy", 0)), 4),
            "queries_evaluated": len(results_with_directions),
        }
        logger.info(f"RAGAS scores: {scores}")
        return scores
    except Exception as e:
        logger.error(f"RAGAS evaluation failed: {e}")
        return {"error": str(e)}
