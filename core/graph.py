"""Spatial graph operations using NetworkX.

Manages the topological graph for indoor navigation. The graph is loaded
from a JSON file and stored in memory. BFS computes shortest paths — the
LLM never decides paths, it only translates computed paths to language.

This directly addresses the research finding from "Lost in Aggregation"
(arxiv 2606.22219): 59% of LLM navigation failures happen at junction
choices. By using deterministic BFS, we eliminate that failure mode.
"""

import json
import logging
from typing import List, Dict, Optional

import networkx as nx

from core.config import Config

logger = logging.getLogger(__name__)


class SpatialGraph:
    """Manages the topological graph for indoor navigation.

    The graph is loaded from a JSON file containing node definitions
    with connectivity information. NetworkX provides BFS pathfinding,
    junction detection (degree >= 3), and node metadata access.

    Attributes:
        graph: NetworkX Graph object with nodes and edges.
    """

    def __init__(self) -> None:
        """Initialize an empty NetworkX graph."""
        self.graph: nx.Graph = nx.Graph()

    def load_from_json(self, json_path: str) -> None:
        """Load graph from a JSON file.

        The JSON format uses a "nodes" dict where each key is a node ID
        and the value contains node metadata including a "connects_to"
        list. Edges are created from each connects_to entry.

        Args:
            json_path: Path to graph.json file.

        Raises:
            FileNotFoundError: If file does not exist.
            json.JSONDecodeError: If file is not valid JSON.
            KeyError: If JSON lacks required "nodes" key.
        """
        logger.info(f"Loading graph from: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Graph file not found: {json_path}")
            raise FileNotFoundError(f"Graph file not found: {json_path}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in graph file: {json_path}")
            raise json.JSONDecodeError(
                f"Invalid JSON in graph file: {json_path}", e.doc, e.pos
            ) from e

        if "nodes" not in data:
            logger.error("Graph JSON missing 'nodes' key")
            raise KeyError("Graph JSON must contain 'nodes' key")

        nodes = data["nodes"]
        for node_id, node_data in nodes.items():
            self.graph.add_node(node_id, **node_data)
            for neighbor in node_data.get("connects_to", []):
                if neighbor in nodes:
                    self.graph.add_edge(node_id, neighbor)

        logger.info(
            f"Loaded {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )

    def find_shortest_path(self, start: str, end: str) -> List[str]:
        """Find shortest path between two nodes using BFS.

        BFS is deterministic — the path is mathematically optimal by hop
        count. The LLM never computes paths; this method does.

        Args:
            start: Starting node ID.
            end: Destination node ID.

        Returns:
            List of node IDs representing the shortest path.
            Returns empty list if no path exists.

        Raises:
            KeyError: If start or end node not in graph.
        """
        if start not in self.graph:
            logger.error(f"Start node not found: {start}")
            raise KeyError(f"Start node '{start}' not in graph")
        if end not in self.graph:
            logger.error(f"End node not found: {end}")
            raise KeyError(f"End node '{end}' not in graph")

        try:
            path = nx.shortest_path(self.graph, start, end)
            logger.info(f"Path found: {len(path)} steps from {start} to {end}")
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path from {start} to {end}")
            return []

    def get_junctions_in_path(self, path: List[str]) -> List[str]:
        """Identify junction nodes in a path (nodes with 3+ connections).

        Junctions are the critical decision points where 59% of LLM
        navigation failures occur. These nodes need landmark annotation
        so the direction generator can give grounded turn instructions.

        Args:
            path: List of node IDs in the path.

        Returns:
            List of node IDs that are junctions (degree >= 3).
        """
        junctions = []
        for node_id in path:
            if self.graph.degree(node_id) >= 3:
                junctions.append(node_id)
        logger.info(f"Found {len(junctions)} junctions in path")
        return junctions

    def get_node_data(self, node_id: str) -> Dict:
        """Get all metadata for a specific node.

        Args:
            node_id: Node identifier.

        Returns:
            Dictionary of node attributes (display_name, floor, wing,
            room_number, landmarks_nearby, etc.).

        Raises:
            KeyError: If node not in graph.
        """
        if node_id not in self.graph:
            raise KeyError(f"Node '{node_id}' not in graph")
        return dict(self.graph.nodes[node_id])

    def get_all_nodes(self) -> List[str]:
        """Get all node IDs in the graph.

        Returns:
            List of all node IDs.
        """
        return list(self.graph.nodes())

    def is_connected(self) -> bool:
        """Check if the graph is fully connected.

        Every node must be reachable from every other node for the
        navigation system to work correctly.

        Returns:
            True if all nodes are reachable from any other node.
        """
        return nx.is_connected(self.graph)

    def get_degree(self, node_id: str) -> int:
        """Get the degree (number of connections) of a node.

        Args:
            node_id: Node identifier.

        Returns:
            Number of edges connected to this node.

        Raises:
            KeyError: If node not in graph.
        """
        if node_id not in self.graph:
            raise KeyError(f"Node '{node_id}' not in graph")
        return self.graph.degree(node_id)

    def get_path_with_landmarks(
        self, path: List[str]
    ) -> List[Dict]:
        """Annotate each node in a path with its landmarks.

        Used by the direction generator to produce grounded directions.
        At each junction, the landmarks help the patient verify they're
        going the right way.

        Args:
            path: List of node IDs in the path.

        Returns:
            List of dicts, each with node_id, display_name, floor,
            landmarks_nearby, and is_junction.
        """
        annotated = []
        for node_id in path:
            data = self.get_node_data(node_id)
            annotated.append({
                "node_id": node_id,
                "display_name": data.get("display_name", node_id),
                "floor": data.get("floor", 0),
                "landmarks_nearby": data.get("landmarks_nearby", []),
                "is_junction": self.graph.degree(node_id) >= 3,
                "room_number": data.get("room_number"),
            })
        return annotated
