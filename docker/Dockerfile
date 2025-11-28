# Build:
#   CPU:  docker build -t ai-hackathon .
#   CUDA: docker build -t ai-hackathon:cuda --build-arg TARGET=cuda .
#
# Run:
#   CPU:  docker run -v ./data:/app/data ai-hackathon python -m src.services.video_stream --source /app/data/video.mp4
#   CUDA: docker run --gpus all -v ./data:/app/data ai-hackathon:cuda python -m src.services.video_stream --source /app/data/video.mp4

ARG PYTHON_VERSION=3.12
ARG TARGET=cpu

# Base stage
FROM python:${PYTHON_VERSION}-slim AS base

LABEL maintainer="AI-Hackathon Team"
LABEL description="YOLO detection and tracking pipeline"

WORKDIR /app

# System dependencies for OpenCV and video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# CPU stage
FROM base AS cpu

RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# CUDA stage 
FROM base AS cuda

ARG CUDA_VERSION=cu124

RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/${CUDA_VERSION}

# Select based on TARGET
FROM ${TARGET} AS final

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY models/ ./models/ 

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; import ultralytics" || exit 1

# Default command
ENTRYPOINT ["python", "-m", "src.services.video_stream"]
CMD ["--help"]
