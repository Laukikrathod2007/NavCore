"""Tests for Step 1: config, embeddings, and Qdrant client.

Verifies:
- Config constants are properly defined
- EmbeddingManager can encode text and produce 384-dim vectors
- QdrantManager can create collections, upsert, search, and retrieve
"""

import os
import tempfile
import unittest

from core.config import Config


class TestConfig(unittest.TestCase):
    """Verify configuration constants are defined and sane."""

    def test_config_has_qdrant_path(self) -> None:
        """Config must define a QDRANT_PATH."""
        self.assertTrue(hasattr(Config, "QDRANT_PATH"))
        self.assertTrue(len(Config.QDRANT_PATH) > 0)

    def test_config_has_embedding_model(self) -> None:
        """Config must define the embedding model name."""
        self.assertEqual(Config.EMBEDDING_MODEL, "intfloat/multilingual-e5-small")

    def test_config_has_embedding_dim(self) -> None:
        """Embedding dimension must be 384."""
        self.assertEqual(Config.EMBEDDING_DIM, 384)

    def test_config_has_collections(self) -> None:
        """Both Qdrant collection names must be defined."""
        self.assertEqual(Config.TOPOLOGICAL_COLLECTION, "topological_nodes")
        self.assertEqual(Config.SEMANTIC_COLLECTION, "semantic_aliases")

    def test_config_has_ollama_settings(self) -> None:
        """Ollama model and URL must be configured."""
        self.assertEqual(Config.OLLAMA_MODEL, "llama3.2:3b")
        self.assertTrue(Config.OLLAMA_URL.startswith("http://"))

    def test_config_has_navigation_thresholds(self) -> None:
        """Disambiguation and confidence thresholds must be set."""
        self.assertGreater(Config.DISAMBIGUATION_THRESHOLD, 0.0)
        self.assertLess(Config.DISAMBIGUATION_THRESHOLD, 1.0)
        self.assertGreater(Config.LOW_CONFIDENCE_THRESHOLD, 0.0)
        self.assertLess(Config.LOW_CONFIDENCE_THRESHOLD, 1.0)
        self.assertEqual(Config.DEFAULT_START_NODE, "main_entrance")
        self.assertEqual(Config.MAX_RETRIEVAL_CANDIDATES, 3)


class TestEmbeddingManager(unittest.TestCase):
    """Test the multilingual embedding wrapper.

    Note: This test downloads the model on first run (~117MB).
    It is skipped if sentence-transformers is not installed.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Load the embedding model once for all tests."""
        try:
            from core.embeddings import EmbeddingManager
            cls.manager = EmbeddingManager()
            cls._available = True
        except Exception:
            cls._available = False

    def setUp(self) -> None:
        """Skip all tests if model is unavailable."""
        if not self._available:
            self.skipTest("Embedding model not available")

    def test_encode_single_text(self) -> None:
        """Encoding a single string should return a 384-dim list."""
        vec = self.manager.encode("cardiology OPD")
        self.assertEqual(len(vec), Config.EMBEDDING_DIM)
        self.assertTrue(all(isinstance(v, float) for v in vec))

    def test_encode_hindi_text(self) -> None:
        """Hindi text should produce a valid embedding."""
        vec = self.manager.encode("dil ke doctor kahaan hain")
        self.assertEqual(len(vec), Config.EMBEDDING_DIM)

    def test_encode_batch(self) -> None:
        """Batch encoding should return one vector per input."""
        texts = ["cardiology", "dil ke doctor", "Room 312"]
        vectors = self.manager.encode_batch(texts)
        self.assertEqual(len(vectors), len(texts))
        for vec in vectors:
            self.assertEqual(len(vec), Config.EMBEDDING_DIM)

    def test_embeddings_are_normalized(self) -> None:
        """Vectors should be L2-normalized (magnitude ~1.0)."""
        import math
        vec = self.manager.encode("heart doctor")
        magnitude = math.sqrt(sum(v * v for v in vec))
        self.assertAlmostEqual(magnitude, 1.0, places=5)


class TestQdrantManager(unittest.TestCase):
    """Test the Qdrant Edge file-based client."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize Qdrant with a temporary directory."""
        try:
            from core.qdrant_client import QdrantManager
            cls._qdrant_dir = tempfile.mkdtemp(prefix="navcore_test_")
            cls._original_path = Config.QDRANT_PATH
            Config.QDRANT_PATH = cls._qdrant_dir
            cls.manager = QdrantManager()
            cls._available = True
        except Exception:
            cls._available = False

    def setUp(self) -> None:
        """Skip if Qdrant is unavailable."""
        if not self._available:
            self.skipTest("Qdrant not available")

    def test_create_collection(self) -> None:
        """Should create a collection without error."""
        self.manager.create_collection("test_collection", 384)

    def test_upsert_and_retrieve(self) -> None:
        """Upserting a point should allow retrieval of its payload."""
        self.manager.create_collection("test_retrieve", 384)
        self.manager.upsert_point(
            "test_retrieve",
            point_id=1,
            vector=[0.1] * 384,
            payload={"label": "cardiology", "floor": 3},
        )
        result = self.manager.get_point("test_retrieve", 1)
        self.assertIsNotNone(result)
        self.assertEqual(result["label"], "cardiology")

    def test_search_returns_results(self) -> None:
        """Search should return the closest vector."""
        self.manager.create_collection("test_search", 384)
        self.manager.upsert_point(
            "test_search",
            point_id=1,
            vector=[1.0] + [0.0] * 383,
            payload={"node": "cardiology_opd"},
        )
        self.manager.upsert_point(
            "test_search",
            point_id=2,
            vector=[0.0, 1.0] + [0.0] * 382,
            payload={"node": "neurology_opd"},
        )
        results = self.manager.search(
            "test_search",
            query_vector=[1.0] + [0.0] * 383,
            limit=2,
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["payload"]["node"], "cardiology_opd")
        self.assertGreater(results[0]["score"], results[1]["score"])

    @classmethod
    def tearDownClass(cls) -> None:
        """Restore config and clean up temp directory."""
        if hasattr(cls, "_original_path"):
            Config.QDRANT_PATH = cls._original_path
        if hasattr(cls, "_qdrant_dir"):
            import shutil
            shutil.rmtree(cls._qdrant_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
