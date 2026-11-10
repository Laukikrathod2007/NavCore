"""Tests for Step 4: State, language detection, and retrieval.

Verifies:
- NavigationState has all required fields
- Language detection correctly identifies hi, mr, en, hi-mix
- Semantic retrieval returns correct candidates for Hindi queries
"""

import unittest
import tempfile
import shutil

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from agents.state import NavigationState
from agents.language_detector import detect_language, language_detector_node
from agents.retrieval import init_retrieval, retrieval_node
from ingestion.ingest import run_ingestion


class TestNavigationState(unittest.TestCase):
    """Verify NavigationState TypedDict has all required fields."""

    def test_state_has_all_fields(self) -> None:
        """NavigationState should contain all expected keys (v1 + v2)."""
        expected_keys = {
            # v1 fields
            "query_text", "input_modality", "current_location",
            "detected_language", "intent", "extracted_entities",
            "candidate_nodes", "requires_disambiguation", "confidence_scores",
            "disambiguation_question", "disambiguation_options",
            "resolved_node_id",
            "path_nodes", "junction_nodes_in_path", "warnings",
            "directions_text", "directions_audio", "destination_display_name",
            "latency_ms", "query_id",
            # v2 fields
            "low_confidence", "rephrase_message",
            "path_error",
            "multi_destination", "secondary_node_id", "is_multi_destination",
            "location_extracted_from_query",
        }
        actual_keys = set(NavigationState.__annotations__.keys())
        self.assertEqual(expected_keys, actual_keys)


class TestLanguageDetector(unittest.TestCase):
    """Test language detection across all 4 supported languages."""

    def test_detect_english(self) -> None:
        """English text should return 'en'."""
        self.assertEqual(detect_language("where is cardiology"), "en")

    def test_detect_hindi_devanagari(self) -> None:
        """Hindi in Devanagari script should return 'hi'."""
        self.assertEqual(detect_language("ह्रदय रोग विभाग कुठे आहे"), "mr")

    def test_detect_code_mixed_devanagari_latin(self) -> None:
        """Text with both Devanagari and Latin should return 'hi-mix'."""
        self.assertEqual(
            detect_language("mujhe Dr. Mehta se milna hai cardiology me"),
            "hi-mix",
        )

    def test_detect_romanized_hindi(self) -> None:
        """Romanized Hindi without Devanagari should return 'hi-mix'."""
        self.assertEqual(
            detect_language("dil ke doctor kahaan hain"),
            "hi-mix",
        )

    def test_detect_romanized_hindi_blood_test(self) -> None:
        """Another Romanized Hindi query should return 'hi-mix'."""
        self.assertEqual(
            detect_language("mujhe MRI karwana hai"),
            "hi-mix",
        )

    def test_language_detector_node(self) -> None:
        """The LangGraph node wrapper should return state update dict."""
        state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": None,
        }
        result = language_detector_node(state)
        self.assertIn("detected_language", result)
        self.assertEqual(result["detected_language"], "hi-mix")


class TestRetrieval(unittest.TestCase):
    """Test semantic retrieval from Qdrant."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up Qdrant and run ingestion."""
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_retrieval_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        cls.qdrant = QdrantManager()
        cls.embedder = EmbeddingManager()
        run_ingestion(Config.DATA_DIR, cls.qdrant, cls.embedder)
        init_retrieval(cls.qdrant, cls.embedder)

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_retrieval_returns_candidates(self) -> None:
        """Retrieval should return at least 1 candidate."""
        state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        self.assertGreater(len(result["candidate_nodes"]), 0)
        self.assertIn("confidence_scores", result)
        self.assertIn("requires_disambiguation", result)

    def test_retrieval_cardiology(self) -> None:
        """Retrieval for 'dil ke doctor' should return cardiology_opd."""
        state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        top_node = result["candidate_nodes"][0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "cardiology_opd")

    def test_retrieval_blood_test(self) -> None:
        """Retrieval for 'blood test' should return lab_pathology."""
        state = {
            "query_text": "I need a blood test",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        top_node = result["candidate_nodes"][0]["payload"]["canonical_node_id"]
        self.assertEqual(top_node, "lab_pathology")

    def test_retrieval_returns_scores(self) -> None:
        """Confidence scores should be present and sorted descending."""
        state = {
            "query_text": "cardiology",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        scores = result["confidence_scores"]
        self.assertGreater(len(scores), 0)
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_retrieval_has_payload(self) -> None:
        """Each candidate should have payload with canonical_node_id."""
        state = {
            "query_text": "heart doctor",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        for candidate in result["candidate_nodes"]:
            self.assertIn("payload", candidate)
            self.assertIn("canonical_node_id", candidate["payload"])

    def test_retrieval_returns_disambiguation_flag(self) -> None:
        """Retrieval should return requires_disambiguation as a bool."""
        state = {
            "query_text": "doctor",
            "input_modality": "text",
            "current_location": None,
        }
        result = retrieval_node(state)
        self.assertIsInstance(result["requires_disambiguation"], bool)


if __name__ == "__main__":
    unittest.main()
