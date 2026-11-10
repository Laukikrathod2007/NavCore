"""TrainStationPlugin — future plugin for train station navigation.

Stub implementation for future extension.
"""

from typing import Optional

from plugins.base import LocationPlugin


class TrainStationPlugin(LocationPlugin):
    """Plugin for train station navigation (future)."""

    def get_default_entry_node(self) -> str:
        """Return the station's main entrance as default start."""
        return "station_main_entrance"

    def check_availability(self, node_id: str) -> bool:
        """Check if a platform is currently accessible."""
        return True

    def get_special_instructions(self, node_id: str) -> Optional[str]:
        """Return special instructions for station-specific nodes."""
        return None
