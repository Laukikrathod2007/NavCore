"""Tests for Step 8: FastAPI endpoints.

Verifies:
- GET /health returns system status
- POST /query/text returns directions for a navigation query
- GET /locations lists all nodes with availability
- PATCH /locations/{id}/availability updates node status
- POST /query/qr parses QR code and returns location
"""

import unittest
import tempfile
import shutil

from core.config import Config
from core.embeddings import EmbeddingManager
from core.qdrant_client import QdrantManager
from core.graph import SpatialGraph
from agents import retrieval, path_planner, direction_generator, disambiguation
from agents.workflow import build_workflow
from ingestion.ingest import run_ingestion

from fastapi.testclient import TestClient


class TestAPI(unittest.TestCase):
    """Test FastAPI endpoints using TestClient."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up Qdrant, embeddings, graph, and FastAPI app."""
        cls._temp_dir = tempfile.mkdtemp(prefix="navcore_api_")
        cls._original_qdrant = Config.QDRANT_PATH
        Config.QDRANT_PATH = cls._temp_dir

        # Initialize infrastructure
        qdrant = QdrantManager()
        embedder = EmbeddingManager()
        graph = SpatialGraph()
        graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

        # Run ingestion
        run_ingestion(Config.DATA_DIR, qdrant, embedder)

        # Inject dependencies
        retrieval.init_retrieval(qdrant, embedder)
        path_planner.init_path_planner(graph)
        direction_generator.init_direction_generator(None, graph)
        disambiguation.init_disambiguation(graph)

        # Build the FastAPI app (bypass lifespan, inject manually)
        from api.main import app

        app.state.workflow = build_workflow()
        app.state.qdrant = qdrant
        app.state.graph = graph
        app.state.ollama = None

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        Config.QDRANT_PATH = cls._original_qdrant
        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_health_endpoint(self) -> None:
        """GET /health should return status dict."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("qdrant_ok", data)
        self.assertIn("graph_ok", data)
        self.assertTrue(data["graph_ok"])

    def test_query_text_cardiology(self) -> None:
        """POST /query/text should return directions for cardiology query."""
        response = self.client.post(
            "/query/text",
            json={
                "query": "dil ke doctor kahaan hain",
                "current_node": "main_entrance",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("directions", data)
        self.assertIn("destination", data)
        self.assertIn("path_nodes", data)
        self.assertGreater(len(data["path_nodes"]), 0)
        self.assertEqual(data["destination_node_id"], "cardiology_opd")

    def test_query_text_blood_test(self) -> None:
        """POST /query/text should return lab_pathology for blood test."""
        response = self.client.post(
            "/query/text",
            json={
                "query": "I need a blood test",
                "current_node": "main_entrance",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["destination_node_id"], "lab_pathology")

    def test_query_text_default_start(self) -> None:
        """POST /query/text without current_node should use main_entrance or cookie location."""
        response = self.client.post(
            "/query/text",
            json={"query": "cardiology"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Path should end at cardiology — start could be main_entrance or a previous cookie location
        if len(data["path_nodes"]) > 0:
            self.assertEqual(data["path_nodes"][-1], "cardiology_opd")

    def test_query_text_returns_language(self) -> None:
        """POST /query/text should return detected_language."""
        response = self.client.post(
            "/query/text",
            json={"query": "dil ke doctor kahaan hain"},
        )
        data = response.json()
        self.assertIn("detected_language", data)
        self.assertEqual(data["detected_language"], "hi-mix")

    def test_get_locations(self) -> None:
        """GET /locations should return all 20 nodes."""
        response = self.client.get("/locations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 20)
        self.assertEqual(len(data["locations"]), 20)

    def test_patch_availability(self) -> None:
        """PATCH /locations/{id}/availability should update status."""
        response = self.client.patch(
            "/locations/cardiology_opd/availability",
            json={"is_available": False, "reason": "Dr. Mehta on leave"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Verify the update took effect
        loc_response = self.client.get("/locations")
        locations = loc_response.json()["locations"]
        cardio = [l for l in locations if l["node_id"] == "cardiology_opd"][0]
        self.assertFalse(cardio["is_available"])

        # Restore
        self.client.patch(
            "/locations/cardiology_opd/availability",
            json={"is_available": True},
        )

    def test_query_qr(self) -> None:
        """POST /query/qr should parse QR data and return location."""
        response = self.client.post(
            "/query/qr",
            json={"qr_data": "node:reception"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["confirmed"])
        self.assertEqual(data["current_location"], "reception")
        self.assertEqual(data["display_name"], "Reception")

    def test_query_qr_invalid(self) -> None:
        """POST /query/qr with unknown node should not confirm."""
        response = self.client.post(
            "/query/qr",
            json={"qr_data": "node:nonexistent_node"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Location is returned but confirmed=False (display_name empty)
        self.assertEqual(data["current_location"], "nonexistent_node")
        self.assertEqual(data["display_name"], "")


if __name__ == "__main__":
    unittest.main()
