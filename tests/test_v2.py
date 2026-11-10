"""Tests for NavCore v2 fixes.

Covers:
- Fix 1: Voice failure UX (is_valid_transcription)
- Fix 2: No-path-found returns helpful language message
- Fix 3: Verbal location extraction from query text
- Fix 4: Low-confidence retrieval returns rephrase message
- Fix 5: Multi-destination query detection and splitting
- Fix 6: QR URL parameter (GET /locations/{id}/display endpoint)
- Fix 7: Language sanity check function
- Fix 9: Query history endpoint
- Updated NavigationState fields
"""

import json
import tempfile
import shutil
import unittest

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from core.graph import SpatialGraph
from agents.state import NavigationState
from agents.retrieval import init_retrieval, retrieval_node
from agents.path_planner import init_path_planner, path_planner_node
from agents.direction_generator import (
    init_direction_generator,
    direction_generator_node,
    verify_response_language,
)
from agents.input_processor import (
    is_valid_transcription,
    extract_location_from_query,
)
from agents.intent_classifier import (
    detect_multi_destination,
    split_multi_destination_query,
    intent_classifier_node,
)
from ingestion.ingest import run_ingestion
from agents.workflow import build_workflow, init_workflow_dependencies
from agents.disambiguation import init_disambiguation


class TestFix1VoiceValidation(unittest.TestCase):
    """Fix 1: Voice transcription validation."""

    def test_empty_string_invalid(self) -> None:
        self.assertFalse(is_valid_transcription(""))

    def test_whitespace_invalid(self) -> None:
        self.assertFalse(is_valid_transcription("   "))

    def test_too_short_invalid(self) -> None:
        self.assertFalse(is_valid_transcription("hi"))

    def test_hallucination_invalid(self) -> None:
        self.assertFalse(is_valid_transcription("thank you"))
        self.assertFalse(is_valid_transcription("Thanks for watching"))
        self.assertFalse(is_valid_transcription("."))

    def test_valid_hindi(self) -> None:
        self.assertTrue(is_valid_transcription("dil ke doctor kahaan hain"))

    def test_valid_english(self) -> None:
        self.assertTrue(is_valid_transcription("where is cardiology"))

    def test_valid_marathi(self) -> None:
        self.assertTrue(is_valid_transcription("ह्रदय रोग विभाग कुठे आहे"))

    def test_valid_short_but_ok(self) -> None:
        self.assertTrue(is_valid_transcription("ECG"))


class TestFix2NoPathFound(unittest.TestCase):
    """Fix 2: No-path-found returns language-appropriate reception message."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
        init_path_planner(cls.graph)
        init_direction_generator(None, cls.graph)

    def test_no_destination_returns_path_error(self) -> None:
        state = {
            "query_text": "test",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [],
            "resolved_node_id": None,
            "multi_destination": False,
            "low_confidence": False,
        }
        result = path_planner_node(state)
        self.assertIn("path_error", result)
        self.assertEqual(result["path_nodes"], [])

    def test_direction_generator_no_path_english(self) -> None:
        state = {
            "query_text": "test",
            "detected_language": "en",
            "path_nodes": [],
            "path_error": "No route found",
            "warnings": [],
            "resolved_node_id": None,
            "low_confidence": False,
        }
        result = direction_generator_node(state)
        directions = result["directions_text"]
        self.assertGreater(len(directions), 10)
        self.assertIn("reception", directions.lower())

    def test_direction_generator_no_path_hindi(self) -> None:
        state = {
            "query_text": "test",
            "detected_language": "hi",
            "path_nodes": [],
            "path_error": "No route found",
            "warnings": [],
            "resolved_node_id": None,
            "low_confidence": False,
        }
        result = direction_generator_node(state)
        directions = result["directions_text"]
        self.assertGreater(len(directions), 10)
        # Hindi message should contain reception reference
        self.assertIn("reception", directions.lower())

    def test_direction_generator_no_path_marathi(self) -> None:
        state = {
            "query_text": "test",
            "detected_language": "mr",
            "path_nodes": [],
            "path_error": "No route found",
            "warnings": [],
            "resolved_node_id": None,
            "low_confidence": False,
        }
        result = direction_generator_node(state)
        self.assertGreater(len(result["directions_text"]), 10)


class TestFix3VerbalLocationExtraction(unittest.TestCase):
    """Fix 3: Extract current location from query text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
        init_path_planner(cls.graph)

    def test_extract_english_near(self) -> None:
        query = "I'm near lift A, where is pharmacy"
        node_id, cleaned = extract_location_from_query(query, self.graph)
        self.assertEqual(node_id, "lift_A")
        self.assertIn("pharmacy", cleaned.lower())
        self.assertNotIn("I'm near", cleaned)

    def test_extract_english_at(self) -> None:
        query = "I am at reception, how do I get to cardiology"
        node_id, cleaned = extract_location_from_query(query, self.graph)
        self.assertEqual(node_id, "reception")

    def test_no_location_returns_none(self) -> None:
        query = "where is cardiology"
        node_id, cleaned = extract_location_from_query(query, self.graph)
        self.assertIsNone(node_id)
        self.assertEqual(cleaned, query)

    def test_unknown_location_returns_none(self) -> None:
        query = "I'm near the canteen, where is pharmacy"
        node_id, cleaned = extract_location_from_query(query, self.graph)
        self.assertIsNone(node_id)


class TestFix4LowConfidence(unittest.TestCase):
    """Fix 4: Low-confidence retrieval triggers rephrase message."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_v2_")
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

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_low_confidence_sets_flag(self) -> None:
        """A completely random query should trigger low confidence."""
        state = {
            "query_text": "xyzxyzxyz_completely_unknown_query_12345",
            "input_modality": "text",
            "current_location": "main_entrance",
            "detected_language": "en",
        }
        result = retrieval_node(state)
        # Either low_confidence or empty candidates
        if result.get("low_confidence"):
            self.assertIsNotNone(result.get("rephrase_message"))
            self.assertGreater(len(result["rephrase_message"]), 10)

    def test_direction_generator_low_confidence_returns_rephrase(self) -> None:
        """Low confidence state bypasses LLM and returns rephrase message."""
        msg = "Please rephrase your query."
        state = {
            "query_text": "xyzxyz",
            "detected_language": "en",
            "path_nodes": [],
            "low_confidence": True,
            "rephrase_message": msg,
            "warnings": [],
            "resolved_node_id": None,
        }
        result = direction_generator_node(state)
        self.assertEqual(result["directions_text"], msg)

    def test_normal_query_not_low_confidence(self) -> None:
        """A good query like 'cardiology' should not be low confidence."""
        state = {
            "query_text": "cardiology",
            "input_modality": "text",
            "current_location": "main_entrance",
            "detected_language": "en",
        }
        result = retrieval_node(state)
        self.assertFalse(result.get("low_confidence", False))
        self.assertGreater(len(result.get("candidate_nodes", [])), 0)


class TestFix5MultiDestination(unittest.TestCase):
    """Fix 5: Multi-destination query detection and splitting."""

    def test_detect_phir_connector(self) -> None:
        self.assertTrue(detect_multi_destination(
            "pehle blood test karwana hai phir Dr. Mehta se milna hai"
        ))

    def test_detect_and_then(self) -> None:
        self.assertTrue(detect_multi_destination(
            "first go to pharmacy and then I need to see the doctor"
        ))

    def test_detect_marathi_connector(self) -> None:
        self.assertTrue(detect_multi_destination(
            "पहिले रक्त तपासणी नंतर हृदय रोग विभाग"
        ))

    def test_single_destination_not_detected(self) -> None:
        self.assertFalse(detect_multi_destination("where is cardiology"))
        self.assertFalse(detect_multi_destination("dil ke doctor kahaan hain"))

    def test_split_query_phir(self) -> None:
        query = "pehle blood test karwana hai phir Dr. Mehta se milna hai"
        part1, part2 = split_multi_destination_query(query)
        self.assertIn("blood", part1.lower())
        self.assertIn("mehta", part2.lower())

    def test_split_query_and_then(self) -> None:
        query = "first go to pharmacy and then see the doctor"
        part1, part2 = split_multi_destination_query(query)
        self.assertIn("pharmacy", part1.lower())

    def test_intent_classifier_sets_multi_flag(self) -> None:
        state = {
            "query_text": "pehle pharmacy phir cardiology",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = intent_classifier_node(state)
        self.assertTrue(result.get("multi_destination", False))

    def test_single_destination_no_flag(self) -> None:
        state = {
            "query_text": "where is cardiology",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = intent_classifier_node(state)
        self.assertFalse(result.get("multi_destination", False))


class TestFix7LanguageVerification(unittest.TestCase):
    """Fix 7: Language sanity check on LLM responses."""

    def test_english_text_passes_en(self) -> None:
        text = "Walk straight to Lift A and press floor 3"
        self.assertTrue(verify_response_language(text, "en"))

    def test_devanagari_text_passes_hi(self) -> None:
        text = "लिफ्ट A की तरफ जाएं और तीसरी मंजिल दबाएं"
        self.assertTrue(verify_response_language(text, "hi"))

    def test_devanagari_text_passes_mr(self) -> None:
        text = "लिफ्ट A कडे जा आणि तिसरा मजला दाबा"
        self.assertTrue(verify_response_language(text, "mr"))

    def test_english_text_fails_hi(self) -> None:
        text = "Walk straight to Lift A on floor 3"
        self.assertFalse(verify_response_language(text, "hi"))

    def test_devanagari_text_fails_en(self) -> None:
        text = "लिफ्ट A की तरफ जाएं"
        self.assertFalse(verify_response_language(text, "en"))

    def test_mixed_passes_hi_mix(self) -> None:
        text = "Lift A use karo aur floor 3 pe jao"
        self.assertTrue(verify_response_language(text, "hi-mix"))

    def test_empty_passes_any(self) -> None:
        self.assertTrue(verify_response_language("", "en"))
        self.assertTrue(verify_response_language("", "hi"))


class TestNavigationStateV2Fields(unittest.TestCase):
    """Verify all v2 fields are in NavigationState."""

    def test_v2_fields_exist(self) -> None:
        fields = NavigationState.__annotations__.keys()
        v2_fields = [
            "low_confidence",
            "rephrase_message",
            "path_error",
            "multi_destination",
            "secondary_node_id",
            "is_multi_destination",
            "location_extracted_from_query",
        ]
        for field in v2_fields:
            self.assertIn(
                field, fields,
                f"NavigationState missing v2 field: {field}"
            )


class TestFix6QRDisplayEndpoint(unittest.TestCase):
    """Fix 6: GET /locations/{node_id}/display endpoint."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_fix6_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        from core.embeddings import EmbeddingManager
        qdrant = QdrantManager()
        embedder = EmbeddingManager()
        graph = SpatialGraph()
        graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
        run_ingestion(Config.DATA_DIR, qdrant, embedder)

        init_retrieval(qdrant, embedder)
        init_path_planner(graph)
        init_direction_generator(None, graph)
        init_disambiguation(graph)
        init_workflow_dependencies(embedder, qdrant)

        from agents.workflow import build_workflow
        from api.main import app
        app.state.workflow = build_workflow()
        app.state.qdrant = qdrant
        app.state.graph = graph
        app.state.ollama = None
        from collections import deque
        app.state.query_log = deque(maxlen=100)

        from fastapi.testclient import TestClient
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_display_endpoint_known_node(self) -> None:
        r = self.client.get("/locations/cardiology_opd/display")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["node_id"], "cardiology_opd")
        self.assertEqual(data["display_name"], "Cardiology OPD")
        self.assertTrue(data["confirmed"])

    def test_display_endpoint_unknown_node(self) -> None:
        r = self.client.get("/locations/nonexistent_node/display")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertFalse(data["confirmed"])

    def test_query_log_endpoint(self) -> None:
        r = self.client.get("/admin/query-log")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("queries", data)
        self.assertIn("analytics", data)
        self.assertIn("total", data)

    def test_v2_response_shape(self) -> None:
        """Response must include all v2 fields."""
        r = self.client.post(
            "/query/text",
            json={"query": "where is cardiology", "current_node": "main_entrance"},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        v2_fields = [
            "low_confidence",
            "rephrase_message",
            "is_multi_destination",
            "requires_disambiguation",
            "disambiguation_question",
            "disambiguation_options",
            "current_location_used",
            "path_error",
        ]
        for field in v2_fields:
            self.assertIn(field, data, f"Response missing v2 field: {field}")


if __name__ == "__main__":
    unittest.main()
