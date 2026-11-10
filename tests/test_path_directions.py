"""Tests for Step 5: Path planner and direction generator.

Verifies:
- Path planner computes correct BFS path from main_entrance to cardiology_opd
- Junctions are correctly identified in the path
- Destination availability warnings are generated
- Direction generator produces text (LLM or fallback)
- Fallback directions work without Ollama running
"""

import unittest
import tempfile
import shutil

from core.config import Config
from core.graph import SpatialGraph
from agents.path_planner import init_path_planner, path_planner_node
from agents.direction_generator import (
    init_direction_generator,
    direction_generator_node,
    _build_compact_context,
    _fallback_directions,
)


class TestPathPlanner(unittest.TestCase):
    """Test BFS path planning on the spatial graph."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the graph and initialize path planner."""
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
        init_path_planner(cls.graph)

    def test_path_to_cardiology(self) -> None:
        """Path planner should compute path from main_entrance to cardiology_opd."""
        state = {
            "query_text": "dil ke doctor",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [
                {"payload": {"canonical_node_id": "cardiology_opd"}},
            ],
            "resolved_node_id": None,
        }
        result = path_planner_node(state)
        path = result["path_nodes"]
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], "main_entrance")
        self.assertEqual(path[-1], "cardiology_opd")
        self.assertEqual(len(path), 4)

    def test_path_includes_junctions(self) -> None:
        """Path should include floor_3_corridor_A as a junction."""
        state = {
            "query_text": "cardiology",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [],
            "resolved_node_id": "cardiology_opd",
        }
        result = path_planner_node(state)
        self.assertIn("floor_3_corridor_A", result["junction_nodes_in_path"])

    def test_path_uses_default_start(self) -> None:
        """If no current_location, should default to main_entrance."""
        state = {
            "query_text": "cardiology",
            "input_modality": "text",
            "current_location": None,
            "candidate_nodes": [],
            "resolved_node_id": "cardiology_opd",
        }
        result = path_planner_node(state)
        self.assertEqual(result["path_nodes"][0], "main_entrance")

    def test_path_to_emergency(self) -> None:
        """Path to emergency should be 2 steps (direct from main_entrance)."""
        state = {
            "query_text": "emergency",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [],
            "resolved_node_id": "emergency",
        }
        result = path_planner_node(state)
        self.assertEqual(len(result["path_nodes"]), 2)

    def test_path_resolves_from_candidate(self) -> None:
        """If no resolved_node_id, should use top candidate's canonical_node_id."""
        state = {
            "query_text": "blood test",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [
                {"payload": {"canonical_node_id": "lab_pathology"}},
            ],
            "resolved_node_id": None,
        }
        result = path_planner_node(state)
        self.assertEqual(result["resolved_node_id"], "lab_pathology")
        self.assertEqual(result["path_nodes"][-1], "lab_pathology")

    def test_unavailable_destination_warning(self) -> None:
        """Should warn if destination is marked unavailable."""
        # Temporarily mark cardiology as unavailable
        node_data = self.graph.get_node_data("cardiology_opd")
        self.graph.graph.nodes["cardiology_opd"]["is_available"] = False
        try:
            state = {
                "query_text": "cardiology",
                "input_modality": "text",
                "current_location": "main_entrance",
                "candidate_nodes": [],
                "resolved_node_id": "cardiology_opd",
            }
            result = path_planner_node(state)
            self.assertTrue(
                any("unavailable" in w for w in result["warnings"])
            )
        finally:
            self.graph.graph.nodes["cardiology_opd"]["is_available"] = True

    def test_no_destination(self) -> None:
        """Should return warning if no destination can be resolved."""
        state = {
            "query_text": "unknown",
            "input_modality": "text",
            "current_location": "main_entrance",
            "candidate_nodes": [],
            "resolved_node_id": None,
        }
        result = path_planner_node(state)
        self.assertIn("No destination resolved", result["warnings"])


class TestDirectionGenerator(unittest.TestCase):
    """Test direction generation with and without Ollama."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load graph and initialize without Ollama (fallback mode)."""
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
        init_direction_generator(None, cls.graph)

    def test_fallback_directions_cardiology(self) -> None:
        """Fallback directions should mention Cardiology OPD."""
        path = ["main_entrance", "lift_A", "floor_3_corridor_A", "cardiology_opd"]
        directions = _fallback_directions(path, self.graph)
        self.assertIn("Cardiology", directions)
        self.assertIn("Start at", directions)
        self.assertIn("destination", directions.lower())

    def test_build_spatial_context(self) -> None:
        """Compact context should include step info and landmarks."""
        path = ["main_entrance", "lift_A", "floor_3_corridor_A", "cardiology_opd"]
        context = _build_compact_context(path, self.graph)
        self.assertIn("Main Entrance", context)
        self.assertIn("Cardiology OPD", context)
        self.assertIn("->", context)  # compact format uses ->
        self.assertIn("Floor 3", context)  # floor change noted

    def test_direction_generator_fallback(self) -> None:
        """Without Ollama, direction generator should use fallback."""
        state = {
            "query_text": "dil ke doctor",
            "input_modality": "text",
            "current_location": "main_entrance",
            "detected_language": "hi-mix",
            "path_nodes": ["main_entrance", "lift_A", "floor_3_corridor_A", "cardiology_opd"],
        }
        result = direction_generator_node(state)
        self.assertIn("directions_text", result)
        self.assertGreater(len(result["directions_text"]), 0)
        self.assertEqual(result["destination_display_name"], "Cardiology OPD")

    def test_direction_generator_no_path(self) -> None:
        """With empty path, should return error message."""
        state = {
            "query_text": "test",
            "input_modality": "text",
            "current_location": "main_entrance",
            "path_nodes": [],
        }
        result = direction_generator_node(state)
        self.assertIn("reception", result["directions_text"].lower())

    def test_fallback_mentions_floor(self) -> None:
        """Fallback directions should mention floor numbers."""
        path = ["main_entrance", "lift_A", "floor_3_corridor_A", "cardiology_opd"]
        directions = _fallback_directions(path, self.graph)
        self.assertIn("Floor", directions)


if __name__ == "__main__":
    unittest.main()
