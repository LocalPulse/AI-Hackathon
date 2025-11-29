# AI-Hackathon

Real-time video object detection and tracking system using YOLO11 models.

## Overview

AI-Hackathon is a production-ready system for processing multiple camera streams simultaneously, performing object detection, tracking, and activity classification. The system consists of four main services:

- **AI Service**: Video processing with YOLO11 object detection and tracking
- **API Service**: RESTful API for monitoring and data access
- **Frontend**: React-based web dashboard
- **Nginx**: Reverse proxy and load balancer

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- CUDA-compatible GPU (optional, for acceleration)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd AI-Hackathon

# Create camera configuration
cp config/cameras.json.example config/cameras.json
# Edit config/cameras.json with your camera settings

# Start all services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Access Services

- **Web Dashboard**: http://localhost
- **API**: http://localhost/api
- **API Documentation**: http://localhost/api/docs

## Configuration

### Camera Configuration

**Camera Configuration:**

Edit `config/cameras.json`:

```json
{
  "camera-1": {
    "source": "data/raw/video.mov",
    "name": "Camera 1",
    "device": "cuda",
    "det_model": "yolo11m",
    "resize": [1280, 720]
  }
}
```

**Environment Variables:**

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

Most variables have sensible defaults. See `.env.example` for available options.

**Application Configuration:**

Edit `config.yaml` for detection and tracking parameters.

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete deployment and operations documentation for DevOps engineers
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (available when API service is running)
- **[Documentation Index](docs/README.md)** - Complete documentation index

## Project Structure

```
AI-Hackathon/
├── config/              # Configuration files
│   ├── cameras.json     # Camera configuration
│   └── config.yaml      # Application settings
├── data/                # Runtime data
│   ├── database/        # SQLite database
│   └── raw/             # Video files
├── docs/                # Documentation
├── models/              # YOLO model files
├── output/              # Processed video output
├── scripts/             # Utility scripts
├── src/                 # Python source code
│   ├── services/        # Core services
│   └── utils/           # Utilities
├── web/                 # Web services
│   ├── api/             # FastAPI backend
│   └── frontend/        # React frontend
└── docker-compose.yml   # Docker orchestration
```

## Services

### AI Service

Processes video streams, performs object detection using YOLO11, tracks objects across frames, and classifies activity.

**Entry Point**: `src/services/camera_manager.py`

### API Service

Provides REST API for:
- Real-time camera statistics
- Detection logs
- Camera management

**Entry Point**: `web/api/main.py`  
**Port**: 8000

### Frontend

React-based dashboard for:
- Camera monitoring
- Real-time statistics
- Detection logs viewer
- Metrics visualization

**Port**: 5173 (internal), 80 (via Nginx)

## Development

### Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd web/frontend
npm install

# Run services locally
# AI Service
python -m src.services.camera_manager --config config/cameras.json

# API Service
cd web/api
uvicorn main:app --reload

# Frontend
cd web/frontend
npm run dev
```

### Building Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build ai-service
docker-compose build api
docker-compose build frontend
```

## Monitoring

### Health Checks

All services include health check endpoints:

```bash
# API health
curl http://localhost:8000/health

# Check container health
docker inspect --format='{{.State.Health.Status}}' ai-hackathon-api
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-service
docker-compose logs -f api
```

## Troubleshooting

### Common Issues

**Service won't start:**
- Check Docker daemon is running
- Verify ports are not in use
- Check configuration files exist

**AI Service not processing:**
- Verify camera configuration
- Check video files are accessible
- Ensure YOLO models are present

**API not responding:**
- Check database file permissions
- Verify API container is healthy
- Check logs for errors

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed troubleshooting.


## Support

For deployment and operations questions, see [Deployment Guide](docs/DEPLOYMENT.md).

