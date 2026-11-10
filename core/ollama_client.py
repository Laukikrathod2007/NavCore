"""Ollama client wrapper for local Llama 3.2 direction generation.

Ollama runs Llama 3.2 3B locally — no API key, no cloud, no rate limits.
The LLM only translates computed paths to natural language; it never
computes the path itself (BFS does that).
"""

import logging
from typing import Optional

import ollama

from core.config import Config

logger = logging.getLogger(__name__)


class OllamaManager:
    """Wraps the Ollama Python client for local LLM inference.

    The LLM is used exclusively for direction generation (Node 7).
    It receives a structured spatial context (computed path + landmarks)
    and outputs natural language directions in the detected language.

    Attributes:
        model: The Ollama model identifier from Config.
    """

    def __init__(self) -> None:
        """Initialize the Ollama client.

        Raises:
            RuntimeError: If Ollama is not running or model unavailable.
        """
        self.model = Config.OLLAMA_MODEL
        logger.info(f"OllamaManager initialized with model: {self.model}")
        self._client: Optional[ollama.Client] = None

    @property
    def client(self) -> ollama.Client:
        """Lazy-initialize the Ollama client.

        Returns:
            Configured Ollama Client instance.
        """
        if self._client is None:
            self._client = ollama.Client(host=Config.OLLAMA_URL)
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """Generate a response from the local LLM.

        Args:
            system_prompt: System instructions for the LLM.
            user_message: User query or content for the LLM.

        Returns:
            Generated text from the LLM.

        Raises:
            RuntimeError: If generation fails or Ollama is unreachable.
        """
        logger.info(
            f"Generating with {self.model}, "
            f"system: {system_prompt[:50]}..., user: {user_message[:50]}..."
        )
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            result = response["message"]["content"]
            logger.info(f"Generated: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"LLM generation failed: {e}") from e

    def check_health(self) -> bool:
        """Check if Ollama is running and the model is available.

        Returns:
            True if Ollama responds and the model is available.
        """
        try:
            self.client.list()
            logger.info("Ollama health check passed")
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
