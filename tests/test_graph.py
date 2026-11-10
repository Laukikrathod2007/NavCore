"""Tests for Step 2: SpatialGraph and graph.json.

Verifies:
- Graph loads correctly from JSON with 20 nodes
- BFS finds correct shortest path from main_entrance to cardiology_opd
- Junction detection identifies high-degree nodes
- Graph is fully connected
- Path annotation includes landmarks at junctions
"""

import unittest

from core.config import Config
from core.graph import SpatialGraph


class TestSpatialGraph(unittest.TestCase):
    """Test the SpatialGraph class with the sample hospital data."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the graph from the sample hospital data."""
        cls.graph = SpatialGraph()
        cls.graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

    def test_graph_has_20_nodes(self) -> None:
        """Graph should contain exactly 20 nodes."""
        nodes = self.graph.get_all_nodes()
        self.assertEqual(len(nodes), 20)

    def test_graph_is_connected(self) -> None:
        """Every node should be reachable from every other node."""
        self.assertTrue(self.graph.is_connected())

    def test_path_main_entrance_to_cardiology(self) -> None:
        """BFS should find the shortest path to cardiology OPD."""
        path = self.graph.find_shortest_path("main_entrance", "cardiology_opd")
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], "main_entrance")
        self.assertEqual(path[-1], "cardiology_opd")
        # Expected: main_entrance -> lift_A -> floor_3_corridor_A -> cardiology_opd
        self.assertEqual(len(path), 4)

    def test_path_main_entrance_to_emergency(self) -> None:
        """Emergency should be directly adjacent to main entrance."""
        path = self.graph.find_shortest_path("main_entrance", "emergency")
        self.assertEqual(len(path), 2)
        self.assertEqual(path, ["main_entrance", "emergency"])

    def test_path_main_entrance_to_pharmacy(self) -> None:
        """Pharmacy path goes through reception and corridor_ground."""
        path = self.graph.find_shortest_path("main_entrance", "pharmacy")
        self.assertEqual(path[0], "main_entrance")
        self.assertEqual(path[-1], "pharmacy")
        # Could be main_entrance -> reception -> pharmacy (2 hops)
        # or main_entrance -> reception -> corridor_ground -> pharmacy (3 hops)
        # BFS finds shortest by hop count
        self.assertLessEqual(len(path), 4)

    def test_junctions_in_cardiology_path(self) -> None:
        """floor_3_corridor_A should be a junction in the cardiology path."""
        path = self.graph.find_shortest_path("main_entrance", "cardiology_opd")
        junctions = self.graph.get_junctions_in_path(path)
        self.assertIn("floor_3_corridor_A", junctions)

    def test_lift_A_is_junction(self) -> None:
        """Lift A connects to 5 nodes, so it should be a junction."""
        self.assertEqual(self.graph.get_degree("lift_A"), 5)

    def test_floor_3_corridor_is_junction(self) -> None:
        """Floor 3 corridor connects to 5 nodes (lift, staircase, 3 OPDs)."""
        self.assertEqual(self.graph.get_degree("floor_3_corridor_A"), 5)

    def test_emergency_is_not_junction(self) -> None:
        """Emergency only connects to main_entrance (degree 1)."""
        self.assertEqual(self.graph.get_degree("emergency"), 1)

    def test_node_data_cardiology(self) -> None:
        """Cardiology OPD should have correct metadata."""
        data = self.graph.get_node_data("cardiology_opd")
        self.assertEqual(data["display_name"], "Cardiology OPD")
        self.assertEqual(data["floor"], 3)
        self.assertEqual(data["room_number"], "312")
        self.assertIn("nurse_station_3", data["landmarks_nearby"])

    def test_path_with_landmarks(self) -> None:
        """Path annotation should include landmarks for each step."""
        path = self.graph.find_shortest_path("main_entrance", "cardiology_opd")
        annotated = self.graph.get_path_with_landmarks(path)
        self.assertEqual(len(annotated), len(path))

        # First step should be main_entrance
        self.assertEqual(annotated[0]["node_id"], "main_entrance")
        self.assertEqual(annotated[0]["display_name"], "Main Entrance")

        # Last step should be cardiology_opd
        self.assertEqual(annotated[-1]["node_id"], "cardiology_opd")
        self.assertEqual(annotated[-1]["display_name"], "Cardiology OPD")

        # floor_3_corridor_A should be marked as junction
        for step in annotated:
            if step["node_id"] == "floor_3_corridor_A":
                self.assertTrue(step["is_junction"])

    def test_nonexistent_node_raises_keyerror(self) -> None:
        """Finding a path with a nonexistent node should raise KeyError."""
        with self.assertRaises(KeyError):
            self.graph.find_shortest_path("main_entrance", "nonexistent_room")

    def test_all_destinations_reachable(self) -> None:
        """Every node should be reachable from main_entrance."""
        for node_id in self.graph.get_all_nodes():
            path = self.graph.find_shortest_path("main_entrance", node_id)
            self.assertGreater(len(path), 0, f"No path to {node_id}")


if __name__ == "__main__":
    unittest.main()
