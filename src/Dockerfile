FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (models copied last as they change less frequently)
COPY src/ /app/src/
COPY config.yaml /app/
COPY models/ /app/models/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/data/shared_state_sync.json') else 1)" || exit 1

ENTRYPOINT ["python", "-m", "src.services.camera_manager"]
CMD ["--config", "/app/config/cameras.json"]

