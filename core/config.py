"""NavCore configuration constants.

All paths, model names, collection names, and thresholds live here.
Never hardcode any of these values in other modules.
"""

import os
import logging
import sys
from pathlib import Path
from datetime import datetime

# Disable TensorFlow imports in transformers — we use PyTorch only.
# This prevents conflicts when TF is installed on the system.
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


class Config:
    """Central configuration for NavCore.

    Attributes:
        PROJECT_ROOT: Root directory of the navcore package.
        QDRANT_PATH: Local file-based Qdrant storage directory.
        DATA_DIR: Path to sample hospital data files.
        LOG_DIR: Directory for structured log files.
        EMBEDDING_MODEL: HuggingFace model ID for multilingual embeddings.
        EMBEDDING_DIM: Output dimension of the embedding model.
        TOPOLOGICAL_COLLECTION: Qdrant collection name for graph node descriptions.
        SEMANTIC_COLLECTION: Qdrant collection name for alias vectors.
        OLLAMA_MODEL: Local LLM model identifier for direction generation.
        OLLAMA_URL: Ollama server endpoint URL.
        WHISPER_MODEL: Whisper ASR model size for voice transcription.
        DISAMBIGUATION_THRESHOLD: Minimum cosine score to auto-resolve a candidate.
        LOW_CONFIDENCE_THRESHOLD: Score below which retrieval is considered failed.
        DEFAULT_START_NODE: Fallback starting node when no QR/location is provided.
        MAX_RETRIEVAL_CANDIDATES: Maximum number of Qdrant search results.
        TTS_RATE: Words per minute for pyttsx3 text-to-speech.
        API_HOST: FastAPI bind address.
        API_PORT: FastAPI listen port.
    """

    # --- Paths ---
    PROJECT_ROOT = Path(__file__).parent.parent
    # Allow isolated runs (for example benchmarks) while the navcore/API owns
    # the normal local Qdrant directory.
    QDRANT_PATH = os.environ.get(
        "NAVCORE_QDRANT_PATH", str(PROJECT_ROOT / "qdrant_storage")
    )
    DATA_DIR = str(PROJECT_ROOT / "data" / "hospitals" / "sample_hospital")
    LOG_DIR = str(PROJECT_ROOT / "logs")

    # --- Embedding ---
    EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM = 384

    # --- Qdrant Collections ---
    TOPOLOGICAL_COLLECTION = "topological_nodes"
    SEMANTIC_COLLECTION = "semantic_aliases"

    # --- Ollama ---
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_URL = "http://localhost:11434"

    # --- Whisper ---
    # "tiny"   ~1-2s  on CPU, 39MB  — recommended for navcore
    # "base"   ~2-4s  on CPU, 74MB
    # "medium" ~10-20s on CPU, 1.5GB — too slow for walk-up navcore
    WHISPER_MODEL = "tiny"

    # --- Navigation ---
    DISAMBIGUATION_THRESHOLD = 0.85
    LOW_CONFIDENCE_THRESHOLD = 0.40
    DEFAULT_START_NODE = "main_entrance"
    MAX_RETRIEVAL_CANDIDATES = 3
    DISAMBIGUATION_GAP = 0.15

    # --- LLM ---
    # How long to wait for Llama before falling back to template directions.
    # On CPU: 2.5s guarantees fast response but uses fallback often.
    # On GPU: reduce to 1.0s — GPU generates in <1s.
    LLM_TIMEOUT_SECONDS = 2.5

    # --- TTS ---
    TTS_RATE = 150

    # --- API ---
    API_HOST = "0.0.0.0"
    API_PORT = 8001


def setup_logging() -> None:
    """Configure structured logging for the entire application.

    Creates the log directory if it does not exist and attaches both
    a stdout stream handler and a rotating file handler.
    """
    Path(Config.LOG_DIR).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                f"{Config.LOG_DIR}/navcore_{datetime.now().strftime('%Y%m%d')}.log"
            ),
        ],
    )
