"""CollegePlugin — future plugin for college campus navigation.

Stub implementation for future extension. The plugin architecture
makes NavCore a framework, not a single application.
"""

from typing import Optional

from plugins.base import LocationPlugin


class CollegePlugin(LocationPlugin):
    """Plugin for college campus navigation (future)."""

    def get_default_entry_node(self) -> str:
        """Return the college's main gate as default start."""
        return "college_main_gate"

    def check_availability(self, node_id: str) -> bool:
        """Check if a lecture hall is currently available (time-aware)."""
        return True

    def get_special_instructions(self, node_id: str) -> Optional[str]:
        """Return special instructions for college-specific nodes."""
        return None
