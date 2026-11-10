"""Node 6: BFS path planning on the topological graph.

The LLM never computes paths. BFS does. This is the architectural
principle from "Lost in Aggregation" (arxiv 2606.22219): 59% of LLM
navigation failures happen at junction choices. By using deterministic
BFS, we eliminate that failure mode entirely.

v2: Adds no-path-found handling with specific error messages, and
multi-destination sequential path stitching.
"""

import logging
from typing import Dict

from agents.state import NavigationState
from core.graph import SpatialGraph
from core.config import Config

logger = logging.getLogger(__name__)

# Injected at startup
_spatial_graph: SpatialGraph = None


def init_path_planner(graph: SpatialGraph) -> None:
    """Initialize with a loaded spatial graph.

    Called once during FastAPI lifespan startup.

    Args:
        graph: A SpatialGraph instance loaded with graph.json.
    """
    global _spatial_graph
    _spatial_graph = graph
    logger.info("Path planner initialized")


def path_planner_node(state: NavigationState) -> Dict:
    """Compute the shortest path from current location to resolved destination.

    For multi-destination queries (Fix 5), stitches two paths:
        start → destination_1 → destination_2

    For single-destination queries:
        start → destination

    If no path can be found, sets path_error with a clear reason.

    Args:
        state: Navigation state with candidate_nodes or resolved_node_id.

    Returns:
        State update with path_nodes, junction_nodes_in_path, warnings,
        resolved_node_id, path_error (if failed).
    """
    logger.info("Node 6: Path planning")

    if _spatial_graph is None:
        logger.error("Path planner not initialized")
        return {
            "path_nodes": [],
            "junction_nodes_in_path": [],
            "warnings": ["Path planner not initialized"],
            "resolved_node_id": None,
            "path_error": "Path planner not initialized",
            "is_multi_destination": False,
        }

    # Short-circuit if low-confidence (Fix 4) — no path needed
    if state.get("low_confidence", False):
        return {
            "path_nodes": [],
            "junction_nodes_in_path": [],
            "warnings": [],
            "resolved_node_id": None,
            "path_error": None,
            "is_multi_destination": False,
        }

    # Resolve destination: explicit resolution or top candidate
    destination = state.get("resolved_node_id")
    if not destination:
        candidates = state.get("candidate_nodes", [])
        if candidates:
            destination = candidates[0]["payload"].get("canonical_node_id")
            logger.info(f"Using top candidate as destination: {destination}")

    if not destination:
        logger.error("No destination resolved")
        return {
            "path_nodes": [],
            "junction_nodes_in_path": [],
            "warnings": ["No destination resolved"],
            "resolved_node_id": None,
            "path_error": "No destination could be identified from your query.",
            "is_multi_destination": False,
        }

    start = state.get("current_location") or Config.DEFAULT_START_NODE
    logger.info(f"Planning path from {start} to {destination}")

    # ── Single path ────────────────────────────────────────────────────
    try:
        path = _spatial_graph.find_shortest_path(start, destination)
    except KeyError as e:
        logger.error(f"Path planning failed — node not in graph: {e}")
        return {
            "path_nodes": [],
            "junction_nodes_in_path": [],
            "warnings": [],
            "resolved_node_id": destination,
            "path_error": f"Location not found in map: {e}",
            "is_multi_destination": False,
        }

    if not path:
        logger.warning(f"No path from {start} to {destination}")
        return {
            "path_nodes": [],
            "junction_nodes_in_path": [],
            "warnings": [],
            "resolved_node_id": destination,
            "path_error": f"No route found from {start} to {destination}.",
            "is_multi_destination": False,
        }

    # ── Multi-destination stitching (Fix 5) ───────────────────────────
    is_multi = state.get("multi_destination", False)
    secondary = state.get("secondary_node_id")

    if is_multi and secondary:
        logger.info(f"Multi-destination: adding path to {secondary}")
        try:
            path_2 = _spatial_graph.find_shortest_path(destination, secondary)
            if path_2:
                # Stitch: remove duplicate junction node at join
                full_path = path + path_2[1:]
                logger.info(f"Combined path: {len(full_path)} steps")
            else:
                # Secondary not reachable — just use primary path
                logger.warning(f"Secondary {secondary} not reachable")
                full_path = path
                is_multi = False
        except KeyError:
            full_path = path
            is_multi = False
    else:
        full_path = path
        is_multi = False

    junctions = _spatial_graph.get_junctions_in_path(full_path)
    logger.info(f"Path: {full_path}, Junctions: {junctions}")

    # Check destination availability with smart fallback message
    warnings = []
    try:
        dest_data = _spatial_graph.get_node_data(destination)
        if not dest_data.get("is_available", True):
            dest_name = dest_data.get("display_name", "Destination")
            reason = dest_data.get(
                "unavailability_reason", "temporarily unavailable"
            )
            doctors = dest_data.get("doctors", [])
            if doctors:
                warning = (
                    f"{dest_name} is {reason}. "
                    f"Other doctors here: {', '.join(doctors)}. "
                    f"Check with reception for current availability."
                )
            else:
                warning = (
                    f"{dest_name} is {reason}. "
                    f"Please check with reception for alternatives."
                )
            warnings.append(warning)
            logger.warning(f"Destination unavailable: {dest_name} — {reason}")
    except KeyError:
        pass

    return {
        "path_nodes": full_path,
        "junction_nodes_in_path": junctions,
        "warnings": warnings,
        "resolved_node_id": destination,
        "path_error": None,
        "is_multi_destination": is_multi,
    }
