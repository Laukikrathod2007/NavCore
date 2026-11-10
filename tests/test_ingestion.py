"""Tests for Step 3: Ingestion pipeline.

Verifies:
- aliases.json loads with 8+ aliases per location
- Ingestion populates Qdrant with 20 topological nodes
- Ingestion populates Qdrant with 100+ semantic alias vectors
- Semantic search returns cardiology_opd for "dil ke doctor"
"""

import os
import json
import shutil
import tempfile
import unittest

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from ingestion.ingest import load_aliases, run_ingestion


class TestIngestion(unittest.TestCase):
    """Test the ingestion pipeline end-to-end."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up Qdrant with a temporary directory and run ingestion."""
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_ingest_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        cls.qdrant = QdrantManager()
        cls.embedder = EmbeddingManager()

        cls.result = run_ingestion(
            Config.DATA_DIR, cls.qdrant, cls.embedder
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Restore config and clean up."""
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_aliases_json_has_entries(self) -> None:
        """aliases.json should have at least 12 alias entries."""
        aliases = load_aliases(f"{Config.DATA_DIR}/aliases.json")
        self.assertGreaterEqual(len(aliases), 12)

    def test_each_location_has_8_plus_aliases(self) -> None:
        """Each department should have at least 7+ aliases."""
        aliases = load_aliases(f"{Config.DATA_DIR}/aliases.json")
        for entry in aliases:
            self.assertGreaterEqual(
                len(entry["aliases"]),
                7,
                f"{entry['canonical_node_id']} has fewer than 7 aliases",
            )

    def test_ingested_topological_nodes(self) -> None:
        """Should ingest exactly 20 topological nodes."""
        self.assertEqual(self.result["topological_nodes"], 20)

    def test_ingested_semantic_aliases(self) -> None:
        """Should ingest 100+ semantic alias vectors."""
        self.assertGreaterEqual(self.result["semantic_aliases"], 100)

    def test_total_vectors(self) -> None:
        """Total vectors should be sum of both collections."""
        self.assertEqual(
            self.result["total_vectors"],
            self.result["topological_nodes"]
            + self.result["semantic_aliases"],
        )

    def test_qdrant_has_topological_collection(self) -> None:
        """topological_nodes collection should have 20 points."""
        count = self.qdrant.count_points(Config.TOPOLOGICAL_COLLECTION)
        self.assertEqual(count, 20)

    def test_qdrant_has_semantic_collection(self) -> None:
        """semantic_aliases collection should have 100+ points."""
        count = self.qdrant.count_points(Config.SEMANTIC_COLLECTION)
        self.assertGreaterEqual(count, 100)

    def test_search_dil_ke_doctor_returns_cardiology(self) -> None:
        """Semantic search for 'dil ke doctor' should return cardiology_opd."""
        query_vec = self.embedder.encode("dil ke doctor")
        results = self.qdrant.search(
            Config.SEMANTIC_COLLECTION, query_vec, limit=3
        )
        self.assertGreater(len(results), 0)
        top_node = results[0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "cardiology_opd")

    def test_search_heart_doctor_returns_cardiology(self) -> None:
        """Semantic search for 'heart doctor' should return cardiology_opd."""
        query_vec = self.embedder.encode("heart doctor")
        results = self.qdrant.search(
            Config.SEMANTIC_COLLECTION, query_vec, limit=3
        )
        self.assertGreater(len(results), 0)
        top_node = results[0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "cardiology_opd")

    def test_search_blood_test_returns_lab(self) -> None:
        """Semantic search for 'blood test' should return lab_pathology."""
        query_vec = self.embedder.encode("blood test")
        results = self.qdrant.search(
            Config.SEMANTIC_COLLECTION, query_vec, limit=3
        )
        self.assertGreater(len(results), 0)
        top_node = results[0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "lab_pathology")

    def test_search_bone_doctor_returns_orthopedic(self) -> None:
        """Semantic search for 'bone doctor' should return orthopedic_opd."""
        query_vec = self.embedder.encode("bone doctor")
        results = self.qdrant.search(
            Config.SEMANTIC_COLLECTION, query_vec, limit=3
        )
        self.assertGreater(len(results), 0)
        top_node = results[0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "orthopedic_opd")


if __name__ == "__main__":
    unittest.main()
