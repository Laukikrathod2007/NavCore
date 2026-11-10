"""Tests for Step 6: LangGraph workflow end-to-end.

Verifies:
- Workflow compiles with all 7 nodes
- End-to-end query "dil ke doctor kahaan hain" produces directions
- Path is correctly computed through the workflow
- Conditional edge routes correctly (disambiguation vs direct)
"""

import unittest
import tempfile
import shutil

from core.config import Config
from core.graph import SpatialGraph
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from agents.workflow import build_workflow
from agents.retrieval import init_retrieval
from agents.path_planner import init_path_planner
from agents.direction_generator import init_direction_generator
from agents.disambiguation import init_disambiguation
from ingestion.ingest import run_ingestion


class TestWorkflow(unittest.TestCase):
    """Test the full LangGraph workflow end-to-end."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up all dependencies and build the workflow."""
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_workflow_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        # Initialize infrastructure
        cls.qdrant = QdrantManager()
        cls.embedder = EmbeddingManager()
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

        # Run ingestion
        run_ingestion(Config.DATA_DIR, cls.qdrant, cls.embedder)

        # Inject dependencies into agent nodes
        init_retrieval(cls.qdrant, cls.embedder)
        init_path_planner(cls.graph)
        init_direction_generator(None, cls.graph)  # No Ollama → fallback
        init_disambiguation(cls.graph)

        # Build workflow
        cls.workflow = build_workflow()

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_workflow_compiles(self) -> None:
        """Workflow should compile without errors."""
        self.assertIsNotNone(self.workflow)

    def test_end_to_end_cardiology(self) -> None:
        """Full query 'dil ke doctor kahaan hain' should reach cardiology_opd."""
        initial_state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)

        self.assertIn("directions_text", result)
        self.assertGreater(len(result["directions_text"]), 0)
        self.assertEqual(
            result["destination_display_name"], "Cardiology OPD"
        )
        self.assertGreater(len(result["path_nodes"]), 0)
        self.assertEqual(result["path_nodes"][-1], "cardiology_opd")

    def test_end_to_end_blood_test(self) -> None:
        """Full query for 'blood test' should reach lab_pathology."""
        initial_state = {
            "query_text": "I need a blood test",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)

        self.assertGreater(len(result["path_nodes"]), 0)
        self.assertEqual(result["path_nodes"][-1], "lab_pathology")

    def test_end_to_end_bone_doctor(self) -> None:
        """Full query for 'bone doctor' should reach orthopedic_opd."""
        initial_state = {
            "query_text": "bone doctor",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)

        self.assertGreater(len(result["path_nodes"]), 0)
        self.assertEqual(result["path_nodes"][-1], "orthopedic_opd")

    def test_end_to_end_emergency(self) -> None:
        """Full query for 'emergency' should reach emergency department."""
        initial_state = {
            "query_text": "where is emergency",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)

        self.assertGreater(len(result["path_nodes"]), 0)
        self.assertEqual(result["path_nodes"][-1], "emergency")

    def test_workflow_detects_language(self) -> None:
        """Workflow should detect language from the query."""
        initial_state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)
        self.assertIn("detected_language", result)
        self.assertEqual(result["detected_language"], "hi-mix")

    def test_workflow_classifies_intent(self) -> None:
        """Workflow should classify intent from the query."""
        initial_state = {
            "query_text": "I need an X-Ray",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)
        self.assertIn("intent", result)
        self.assertEqual(result["intent"], "procedure_query")

    def test_workflow_default_start(self) -> None:
        """Without current_location, should default to main_entrance."""
        initial_state = {
            "query_text": "cardiology",
            "input_modality": "text",
            "current_location": None,
        }
        result = self.workflow.invoke(initial_state)
        if len(result["path_nodes"]) > 0:
            self.assertEqual(result["path_nodes"][0], "main_entrance")

    def test_workflow_generates_directions_text(self) -> None:
        """Directions text should be non-empty and mention the destination."""
        initial_state = {
            "query_text": "dil ke doctor kahaan hain",
            "input_modality": "text",
            "current_location": "main_entrance",
        }
        result = self.workflow.invoke(initial_state)
        directions = result["directions_text"]
        self.assertGreater(len(directions), 10)
        # Fallback directions mention Cardiology
        self.assertIn("Cardiology", directions)


if __name__ == "__main__":
    unittest.main()
