"""MallPlugin — future plugin for shopping mall navigation.

Stub implementation for future extension.
"""

from typing import Optional

from plugins.base import LocationPlugin


class MallPlugin(LocationPlugin):
    """Plugin for shopping mall navigation (future)."""

    def get_default_entry_node(self) -> str:
        """Return the mall's main entrance as default start."""
        return "mall_main_entrance"

    def check_availability(self, node_id: str) -> bool:
        """Check if a store is currently open."""
        return True

    def get_special_instructions(self, node_id: str) -> Optional[str]:
        """Return special instructions for mall-specific nodes."""
        return None
