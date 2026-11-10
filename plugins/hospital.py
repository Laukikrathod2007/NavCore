"""HospitalPlugin — domain-specific behavior for hospital navigation.

Checks doctor availability from graph node metadata, provides special
instructions for emergency department, and uses hospital-specific
defaults.
"""

import logging
from typing import Optional

from plugins.base import LocationPlugin

logger = logging.getLogger(__name__)


class HospitalPlugin(LocationPlugin):
    """Plugin for hospital-specific navigation behavior.

    Handles doctor availability schedules, emergency department
    special instructions, and hospital entrance defaults.
    """

    def __init__(self, graph=None) -> None:
        """Initialize with optional spatial graph reference.

        Args:
            graph: Optional SpatialGraph for node metadata access.
        """
        self._graph = graph

    def get_default_entry_node(self) -> str:
        """Return the hospital's main entrance as default start.

        Returns:
            "main_entrance" node ID.
        """
        return "main_entrance"

    def check_availability(self, node_id: str) -> bool:
        """Check if a hospital department/doctor is currently available.

        Uses node metadata is_available field.

        Args:
            node_id: Node ID to check.

        Returns:
            True if the department is available, False otherwise.
        """
        if self._graph is None:
            return True

        try:
            data = self._graph.get_node_data(node_id)
            return data.get("is_available", True)
        except KeyError:
            logger.warning(f"Node {node_id} not in graph")
            return True

    def get_special_instructions(self, node_id: str) -> Optional[str]:
        """Return special instructions for hospital-specific nodes.

        Emergency department gets a priority instruction.

        Args:
            node_id: Node ID to check.

        Returns:
            Special instruction string, or None.
        """
        if "emergency" in node_id.lower():
            return (
                "Emergency department — please inform staff immediately "
                "on arrival"
            )

        if self._graph is not None:
            try:
                data = self._graph.get_node_data(node_id)
                timing = data.get("timing", "")
                if timing and "24/7" not in timing:
                    return f"Operating hours: {timing}"
            except KeyError:
                pass

        return None
