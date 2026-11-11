FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including FFmpeg for voice audio conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-railway.txt .
# Install CPU-only PyTorch first so pip does not pull CUDA libraries into the
# CPU-only Railway image. sentence-transformers and Whisper reuse this wheel.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-railway.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p qdrant_storage logs data/hospitals/sample_hospital

# Expose API port
EXPOSE 8001

# Disable TF to avoid import conflicts (we use PyTorch only)
ENV TRANSFORMERS_NO_TF=1
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV PORT=8001
ENV OLLAMA_BASE_URL=http://localhost:11434
ENV TORCH_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false

# Run the API
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8001}"]

