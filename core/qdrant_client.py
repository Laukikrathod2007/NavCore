"""Qdrant Edge client wrapper for offline vector storage.

Provides create_collection, upsert, search, and payload update operations
using Qdrant in file-based mode (no server required).
"""

import logging
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from core.config import Config

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant Edge collections for topological and semantic memory.

    Uses file-based Qdrant (path mode) so the system runs fully offline
    with no server process or network dependency.
    """

    def __init__(self) -> None:
        """Initialize the Qdrant Edge client in local file mode.

        Raises:
            RuntimeError: If Qdrant fails to initialize.
        """
        logger.info(f"Connecting to Qdrant Edge at: {Config.QDRANT_PATH}")
        try:
            self.client = QdrantClient(path=Config.QDRANT_PATH)
        except Exception as e:
            logger.error(f"Qdrant initialization failed: {e}")
            raise RuntimeError(f"Qdrant init failed: {e}") from e

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = Config.EMBEDDING_DIM,
    ) -> None:
        """Create a collection if it does not already exist.

        Args:
            collection_name: Name of the Qdrant collection.
            vector_size: Dimension of vectors to store.
        """
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size, distance=Distance.COSINE
                ),
            )
            logger.info(f"Created collection: {collection_name}")
        else:
            logger.info(f"Collection already exists: {collection_name}")

    def upsert_point(
        self,
        collection_name: str,
        point_id: int,
        vector: List[float],
        payload: Dict,
    ) -> None:
        """Insert or update a single point.

        Args:
            collection_name: Target collection name.
            point_id: Unique integer identifier for the point.
            vector: Embedding vector.
            payload: Metadata to store alongside the vector.

        Raises:
            RuntimeError: If upsert fails.
        """
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(id=point_id, vector=vector, payload=payload)
                ],
            )
        except Exception as e:
            logger.error(f"Upsert failed for {collection_name}:{point_id} | {e}")
            raise RuntimeError(f"Upsert failed: {e}") from e

    def upsert_batch(
        self,
        collection_name: str,
        points: List[PointStruct],
    ) -> None:
        """Insert or update multiple points in one call.

        Args:
            collection_name: Target collection name.
            points: List of PointStruct objects to upsert.

        Raises:
            RuntimeError: If batch upsert fails.
        """
        try:
            self.client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            logger.error(f"Batch upsert failed for {collection_name} | {e}")
            raise RuntimeError(f"Batch upsert failed: {e}") from e

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = Config.MAX_RETRIEVAL_CANDIDATES,
    ) -> List[Dict]:
        """Search for the nearest vectors to a query vector.

        Uses the query_points API (Qdrant client >=1.10) which replaces
        the deprecated search method.

        Args:
            collection_name: Collection to search.
            query_vector: Query embedding vector.
            limit: Maximum number of results to return.

        Returns:
            List of dicts with keys 'id', 'score', and 'payload'.

        Raises:
            RuntimeError: If search fails.
        """
        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
            )
            return [
                {"id": p.id, "score": p.score, "payload": p.payload}
                for p in response.points
            ]
        except Exception as e:
            logger.error(f"Search failed in {collection_name} | {e}")
            raise RuntimeError(f"Search failed: {e}") from e

    def update_payload(
        self,
        collection_name: str,
        point_id: int,
        payload_update: Dict,
    ) -> None:
        """Update payload fields of an existing point.

        Used for real-time availability changes from the admin panel.

        Args:
            collection_name: Target collection name.
            point_id: Point ID to update.
            payload_update: New payload values to merge.
        """
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload_update,
                points=[point_id],
            )
            logger.info(
                f"Updated payload for point {point_id} in {collection_name}"
            )
        except Exception as e:
            logger.error(f"Payload update failed: {e}")
            raise RuntimeError(f"Payload update failed: {e}") from e

    def get_point(
        self,
        collection_name: str,
        point_id: int,
    ) -> Optional[Dict]:
        """Retrieve a single point's payload by ID.

        Args:
            collection_name: Collection name.
            point_id: Point ID to retrieve.

        Returns:
            Point payload dict, or None if not found.
        """
        try:
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=True,
            )
            return points[0].payload if points else None
        except Exception as e:
            logger.error(f"Failed to retrieve point {point_id}: {e}")
            return None

    def count_points(self, collection_name: str) -> int:
        """Count the total number of points in a collection.

        Args:
            collection_name: Collection name.

        Returns:
            Number of points in the collection.
        """
        try:
            result = self.client.count(
                collection_name=collection_name, exact=True
            )
            return result.count
        except Exception as e:
            logger.error(f"Count failed for {collection_name}: {e}")
            return 0
