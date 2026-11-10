"""LocationPlugin abstract base class.

Plugins handle domain-specific behavior for different location types.
The core system doesn't know what type of location it's serving.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class LocationPlugin(ABC):
    """Abstract base class for location-specific behavior.

    Subclasses override methods to provide domain-specific rules
    for hospitals, colleges, malls, train stations, etc.
    """

    @abstractmethod
    def get_default_entry_node(self) -> str:
        """Return the default starting node for this location type.

        Returns:
            Node ID string for the default entrance.
        """
        ...

    @abstractmethod
    def check_availability(self, node_id: str) -> bool:
        """Check if a location/doctor is currently available.

        Args:
            node_id: Node ID to check.

        Returns:
            True if available, False otherwise.
        """
        ...

    def get_special_instructions(self, node_id: str) -> Optional[str]:
        """Return special navigation instructions for a node.

        Override in subclasses for location-specific guidance.

        Args:
            node_id: Node ID to get instructions for.

        Returns:
            Special instruction string, or None if no special instructions.
        """
        return None

    def get_disambiguation_threshold(self) -> float:
        """Return the disambiguation confidence threshold for this location.

        Override in subclasses to adjust sensitivity.

        Returns:
            Float threshold between 0 and 1.
        """
        return 0.85
