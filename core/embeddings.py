"""Multilingual embedding wrapper using sentence-transformers.

Wraps the intfloat/multilingual-e5-small model (384-dim) for offline
semantic search across Hindi, Marathi, English, and code-mixed text.
"""

import logging
from typing import List

from sentence_transformers import SentenceTransformer

from core.config import Config

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages multilingual-e5-small model for semantic embeddings.

    This class is a thin wrapper around SentenceTransformer that ensures
    consistent configuration (normalization, model name) across all modules.
    """

    def __init__(self) -> None:
        """Load the embedding model into memory.

        Raises:
            RuntimeError: If the model fails to download or load.
        """
        logger.info(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
        try:
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
            self._dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Dimension: {self._dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Embedding model load failed: {e}") from e

    @property
    def dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self._dim

    def encode(self, text: str) -> List[float]:
        """Embed a single text string.

        Args:
            text: Input text in any supported language.

        Returns:
            Normalized embedding vector of Config.EMBEDDING_DIM dimensions.

        Raises:
            RuntimeError: If encoding fails.
        """
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Encoding failed for text: {text[:50]}... | {e}")
            raise RuntimeError(f"Encoding failed: {e}") from e

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently in a single forward pass.

        Args:
            texts: List of input strings.

        Returns:
            List of normalized embedding vectors.

        Raises:
            RuntimeError: If batch encoding fails.
        """
        try:
            embeddings = self.model.encode(
                texts, normalize_embeddings=True, batch_size=32
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch encoding failed: {e}")
            raise RuntimeError(f"Batch encoding failed: {e}") from e
