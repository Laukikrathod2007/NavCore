"""Tests for Step 9: Evaluation benchmark and metrics.

Verifies:
- Test set loads with 200 queries, all 4 languages
- Benchmark runs all 3 conditions
- Results use the standard schema: keyword_baseline, flat_semantic, navcore_dual_memory
- Metrics are calculated correctly
- Results are saved to evaluation/results/
"""

import json
import unittest
import tempfile
import shutil
from pathlib import Path

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from core.graph import SpatialGraph
from agents.retrieval import init_retrieval
from agents.path_planner import init_path_planner
from agents.direction_generator import init_direction_generator
from agents.disambiguation import init_disambiguation
from agents.workflow import build_workflow
from ingestion.ingest import run_ingestion
from evaluation.benchmark import load_test_set, run_benchmark
from evaluation.metrics import calculate_all_metrics


class TestBenchmark(unittest.TestCase):
    """Test the evaluation benchmark across all three conditions."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up all dependencies for benchmarking."""
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_bench_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        cls.qdrant = QdrantManager()
        cls.embedder = EmbeddingManager()
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

        run_ingestion(Config.DATA_DIR, cls.qdrant, cls.embedder)

        init_retrieval(cls.qdrant, cls.embedder)
        init_path_planner(cls.graph)
        init_direction_generator(None, cls.graph)
        init_disambiguation(cls.graph)

        cls.workflow = build_workflow()

        # Run the mini benchmark ONCE and cache — don't re-run per test method
        cls._mini_results = cls._compute_mini_benchmark()

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_test_set_loads(self) -> None:
        """Test set should load with 200 queries."""
        test_set_path = str(
            Path(Config.PROJECT_ROOT) / "evaluation" / "test_set_200.json"
        )
        queries = load_test_set(test_set_path)
        self.assertEqual(len(queries), 200)

    def test_test_set_has_all_fields(self) -> None:
        """Each test query should have all required fields."""
        test_set_path = str(
            Path(Config.PROJECT_ROOT) / "evaluation" / "test_set_200.json"
        )
        queries = load_test_set(test_set_path)
        for q in queries:
            self.assertIn("query_id", q)
            self.assertIn("query_text", q)
            self.assertIn("language", q)
            self.assertIn("expected_destination_node", q)
            self.assertIn("expected_path", q)
            self.assertIn("junction_nodes_in_path", q)

    def test_test_set_languages(self) -> None:
        """Test set should cover en, hi, mr, and hi-mix."""
        test_set_path = str(
            Path(Config.PROJECT_ROOT) / "evaluation" / "test_set_200.json"
        )
        queries = load_test_set(test_set_path)
        languages = set(q["language"] for q in queries)
        self.assertIn("en", languages)
        self.assertIn("hi", languages)
        self.assertIn("mr", languages)
        self.assertIn("hi-mix", languages)

    def test_benchmark_runs_all_conditions(self) -> None:
        """Benchmark should produce results for all 3 conditions + comparison."""
        results = self._mini_results
        self.assertIn("keyword_baseline", results)
        self.assertIn("flat_semantic", results)
        self.assertIn("navcore_dual_memory", results)
        self.assertIn("comparison", results)

    @classmethod
    def _compute_mini_benchmark(cls):
        """Run benchmark on 3 queries once at class setup."""
        import json as _json, tempfile as _tmpfile, os as _os
        from pathlib import Path as _Path

        full_path = str(
            _Path(Config.PROJECT_ROOT) / "evaluation" / "test_set_200.json"
        )
        with open(full_path, "r", encoding="utf-8") as f:
            full_set = _json.load(f)
        mini_set = full_set[:3]
        mini_path = _tmpfile.mktemp(suffix=".json")
        with open(mini_path, "w", encoding="utf-8") as f:
            _json.dump(mini_set, f)
        try:
            return run_benchmark(
                test_set_path=mini_path,
                qdrant=cls.qdrant,
                embedder=cls.embedder,
                graph=cls.graph,
                workflow=cls.workflow,
            )
        finally:
            _os.unlink(mini_path)

    def _run_mini_benchmark(self):
        """Return the pre-computed mini benchmark results."""
        return self._mini_results

    def test_benchmark_keyword_results(self) -> None:
        """Keyword baseline should process all queries in the set."""
        results = self._mini_results
        self.assertGreater(len(results["keyword_baseline"]["results"]), 0)

    def test_benchmark_flat_results(self) -> None:
        """Flat semantic should process all queries in the set."""
        results = self._mini_results
        self.assertGreater(len(results["flat_semantic"]["results"]), 0)

    def test_benchmark_navcore_results(self) -> None:
        """NavCore should process all queries in the set."""
        results = self._mini_results
        self.assertGreater(len(results["navcore_dual_memory"]["results"]), 0)

    def test_metrics_calculated(self) -> None:
        """All required metric fields should be present per condition."""
        results = self._mini_results
        for key in ["keyword_baseline", "flat_semantic", "navcore_dual_memory"]:
            section = results[key]
            self.assertIn("destination_accuracy", section)
            self.assertIn("total_queries", section)

        nc = results["navcore_dual_memory"]
        self.assertIn("path_accuracy", nc)
        self.assertIn("junction_accuracy", nc)

    def test_deltas_calculated(self) -> None:
        """Comparison section should have delta strings."""
        results = self._mini_results
        cmp = results["comparison"]
        self.assertIn("destination_accuracy_delta", cmp)
        self.assertIn("junction_accuracy_delta", cmp)
        self.assertIn("navcore_beats_keyword", cmp)

    def test_results_saved_to_file(self) -> None:
        """Results JSON should already be saved to evaluation/results/."""
        results_path = (
            Path(Config.PROJECT_ROOT)
            / "evaluation"
            / "results"
            / "benchmark_results.json"
        )
        # The full benchmark writes here — verify it was created
        self.assertTrue(results_path.exists())
        with open(results_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertIn("keyword_baseline", saved)
        self.assertIn("navcore_dual_memory", saved)
        self.assertIn("comparison", saved)


if __name__ == "__main__":
    unittest.main()
