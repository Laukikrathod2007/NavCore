FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including FFmpeg for voice audio conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p qdrant_storage logs data/hospitals/sample_hospital

# Expose API port
EXPOSE 8001

# Disable TF to avoid import conflicts (we use PyTorch only)
ENV TRANSFORMERS_NO_TF=1
ENV TF_CPP_MIN_LOG_LEVEL=3

# Run the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
