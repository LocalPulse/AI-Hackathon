# Docker Setup

Multi-platform Docker images for YOLO detection and tracking pipeline.

## Requirements

- Docker 20.10+
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

### Build

```bash
# CPU version (all platforms)
docker build -t ai-hackathon -f docker/Dockerfile ..

# CUDA version (Linux/Windows WSL2 with NVIDIA GPU)
docker build -t ai-hackathon:cuda -f docker/Dockerfile --build-arg TARGET=cuda ..
```

### Run

```bash
# Process video (CPU)
docker run -v $(pwd)/data:/app/data ai-hackathon \
    --source /app/data/raw/video.mp4 \
    --output /app/data/output.mp4 \
    --det-model yolo11x

# Process video (CUDA)
docker run --gpus all -v $(pwd)/data:/app/data ai-hackathon:cuda \
    --source /app/data/raw/video.mp4 \
    --det-model yolo11x \
    --pose-model yolo11x-pose
```

### Docker Compose

```bash
# CPU
docker-compose up --build

# CUDA
docker-compose -f docker-compose.yml -f docker-compose.cuda.yml up --build
```

## Troubleshooting

### GPU not detected

```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### Out of memory

Reduce image size or batch size:
```bash
docker run --gpus all ai-hackathon:cuda \
    --source /app/data/video.mp4 \
    --imgsz 320
```
