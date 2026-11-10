"""pytest configuration — sets environment variables before any imports.

This must run before sentence-transformers is imported, otherwise
TensorFlow's import chain causes 30+ second startup delays on machines
that have TF installed.
"""

import os

# Block TensorFlow imports in transformers — we use PyTorch only.
# Must be set before any transformers/sentence-transformers import.
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
