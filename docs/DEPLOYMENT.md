# Deployment Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [API Documentation](#api-documentation)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## System Overview

AI-Hackathon is a real-time video object detection and tracking system that processes multiple camera streams simultaneously using YOLO11 models. The system consists of four main components:

- **AI Service**: Processes video streams, performs object detection and tracking
- **API Service**: Provides REST API for monitoring and data access
- **Frontend**: React-based web interface for visualization
- **Nginx**: Reverse proxy and load balancer

### Key Features

- Multi-camera video processing with YOLO11 object detection
- Real-time object tracking and activity classification
- RESTful API for data access
- Web-based monitoring dashboard
- SQLite database for activity logging
- File-based state synchronization between processes

---

## Architecture

### Component Diagram

```
┌─────────────┐
│   Nginx     │ (Port 80/443)
│  Reverse    │
│    Proxy    │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
│  Frontend   │ │   API    │ │ AI Service │
│  (React)    │ │ (FastAPI)│ │  (YOLO11)  │
│  Port 5173  │ │ Port 8000│ │            │
└─────────────┘ └────┬─────┘ └─────┬──────┘
                     │              │
                     │              │
              ┌──────▼──────────────▼──────┐
              │   Shared State Sync        │
              │   (JSON file)              │
              └────────────────────────────┘
                     │
              ┌──────▼──────┐
              │   SQLite    │
              │  Database   │
              └─────────────┘
```

### Service Communication

- **AI Service** → **State Sync File**: Writes camera tracks and heartbeat
- **API Service** → **State Sync File**: Reads camera status and statistics
- **API Service** → **SQLite Database**: Reads activity logs
- **Frontend** → **API Service**: HTTP requests via Nginx proxy
- **Nginx** → **All Services**: Reverse proxy and routing

### Data Flow

1. AI Service processes video frames and detects objects
2. Detected objects are tracked across frames
3. Activity is classified (standing, moving, stopped)
4. Results are written to state sync file and database
5. API Service reads state and serves to frontend
6. Frontend displays real-time statistics and logs

---

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- GPU: Optional (CUDA-compatible for acceleration)

**Recommended:**
- CPU: 8+ cores
- RAM: 16 GB
- Storage: 50 GB SSD
- GPU: NVIDIA GPU with CUDA support (8GB+ VRAM)

### Software Requirements

- Docker: 20.10+
- Docker Compose: 2.0+
- Operating System: Linux (Ubuntu 20.04+, Debian 11+), Windows Server 2019+, or macOS
- Network: Ports 80, 443, 8000 available

### Dependencies

- Python 3.12
- Node.js 20+
- Nginx (included in Docker image)
- CUDA Toolkit 11.8+ (optional, for GPU acceleration)

---

## Installation

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Clone Repository

```bash
git clone <repository-url>
cd AI-Hackathon
```

### Prepare Configuration

```bash
# Create configuration directory
mkdir -p config

# Copy camera configuration template
cp config/cameras.json.example config/cameras.json

# Edit camera configuration
nano config/cameras.json
```

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build ai-service
docker-compose build api
docker-compose build frontend
```

### Verify Installation

```bash
# Check Docker images
docker images | grep ai-hackathon

# Verify configuration files
ls -la config/cameras.json
ls -la config.yaml

# Run setup verification script
python docs/test_camera_manager.py
```

The verification script checks:
- Module imports and dependencies
- Configuration file existence
- Video file availability
- Overall deployment readiness

---

## Configuration

### Camera Configuration (`config/cameras.json`)

```json
{
  "camera-1": {
    "source": "data/raw/video.mov",
    "name": "Camera 1",
    "device": "cuda",
    "det_model": "yolo11m",
    "conf_threshold": 0.25,
    "conf_person": 0.55,
    "conf_train": 0.65,
    "resize": [1280, 720],
    "max_frames": null,
    "output": null
  }
}
```

**Configuration Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `source` | string/int | Video file path or camera index (0, 1, 2...) | Required |
| `name` | string | Display name for camera | Required |
| `device` | string | "cuda", "cpu", or null (auto-detect) | null |
| `det_model` | string | "yolo11m", "yolo11x", or null | null |
| `conf_threshold` | float | General confidence threshold (0.0-1.0) | null |
| `conf_person` | float | Person detection threshold | null |
| `conf_train` | float | Vehicle detection threshold | null |
| `resize` | array | [width, height] or null | null |
| `max_frames` | int | Frame limit for processing or null | null |
| `output` | string | Output video path or null | null |

### Application Configuration (`config.yaml`)

```yaml
detection:
  model: "yolo11x"
  image_size: 640
  device: null

confidence:
  threshold: 0.25
  person: 0.55
  vehicle: 0.65

tracker:
  iou_threshold: 0.2
  max_lost: 45
  use_prediction: true

activity:
  window: 15
  person:
    speed_threshold: 15.0
  vehicle:
    displacement_threshold: 8.0
    min_history: 5

video:
  default_fps: 25.0
  resize: [640, 480]
```

### Environment Variables

Environment variables are configured in `docker-compose.yml` or can be set via `.env` file.

**Create environment file:**

```bash
cp .env.example .env
# Edit .env with your values
```

**Available Variables:**

**AI Service:**
- `PYTHONUNBUFFERED=1` - Disable Python output buffering
- `PYTHONPATH=/app` - Python module path

**API Service:**
- `PYTHONUNBUFFERED=1` - Disable Python output buffering
- `PYTHONPATH=/app` - Python module path

**Frontend (Build-time):**
- `VITE_API_URL=/api` - API endpoint URL
- `VITE_USE_MOCK=false` - Use mock data (development only)

**Optional:**
- `ULTRALYTICS_HOME` - Custom Ultralytics home directory

See `.env.example` for complete list and descriptions.

### Nginx Configuration

Nginx configuration is located at `web/nginx/nginx.conf`. Default settings:

- Worker processes: auto
- Worker connections: 1024
- Gzip compression: enabled
- Client max body size: 100M
- Proxy timeouts: 60s

---

## Deployment

### Docker Compose Deployment

**Start all services:**

```bash
docker-compose up -d
```

**Start specific service:**

```bash
docker-compose up -d ai-service
docker-compose up -d api
docker-compose up -d frontend
docker-compose up -d nginx
```

**View logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f nginx
```

**Stop services:**

```bash
docker-compose stop
```

**Stop and remove containers:**

```bash
docker-compose down
```

**Stop and remove containers with volumes:**

```bash
docker-compose down -v
```

### Health Checks

All services include health checks:

**AI Service:**
- Checks for existence of `/app/data/shared_state_sync.json`
- Interval: 60s
- Timeout: 10s
- Retries: 3
- Start period: 30s

**API Service:**
- HTTP GET to `http://localhost:8000/health`
- Interval: 30s
- Timeout: 10s
- Retries: 3
- Start period: 5s

**Frontend:**
- HTTP GET to `http://localhost:5173`
- Interval: 30s
- Timeout: 3s
- Retries: 3
- Start period: 5s

**Nginx:**
- HTTP GET to `http://localhost/health`
- Interval: 30s
- Timeout: 3s
- Retries: 3

### Verify Deployment

```bash
# Check service status
docker-compose ps

# Check health status
docker inspect --format='{{.State.Health.Status}}' ai-hackathon-ai
docker inspect --format='{{.State.Health.Status}}' ai-hackathon-api
docker inspect --format='{{.State.Health.Status}}' ai-hackathon-frontend
docker inspect --format='{{.State.Health.Status}}' ai-hackathon-nginx

# Test API endpoint
curl http://localhost:8000/health

# Test frontend
curl http://localhost/
```

### Production Deployment Considerations

1. **SSL/TLS Configuration:**
   - Configure SSL certificates in Nginx
   - Update `web/nginx/nginx.conf` with SSL settings
   - Use Let's Encrypt or commercial certificates

2. **Resource Limits:**
   - Add resource limits to `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

3. **Network Security:**
   - Use internal Docker networks
   - Restrict external port exposure
   - Implement firewall rules

4. **Data Persistence:**
   - Use named volumes for database
   - Implement backup strategy
   - Configure log rotation

---

## Monitoring and Logging

### Log Locations

**Container Logs:**
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Service-specific logs
docker-compose logs ai-service
docker-compose logs api
docker-compose logs frontend
docker-compose logs nginx
```

**Application Logs:**
- AI Service: stdout/stderr (captured by Docker)
- API Service: stdout/stderr (captured by Docker)
- Database: `data/database/logs.db`
- State Sync: `data/shared_state_sync.json`

**Nginx Logs:**
- Access log: `/var/log/nginx/access.log` (inside container)
- Error log: `/var/log/nginx/error.log` (inside container)

### Monitoring Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "YOLO Detection Monitoring API"
}
```

**API Information:**
```bash
curl http://localhost:8000/
```

**Camera Statistics:**
```bash
curl http://localhost:8000/cameras
curl http://localhost:8000/cameras/camera-1/stats
```

### Key Metrics to Monitor

1. **Service Health:**
   - Container status
   - Health check results
   - Resource usage (CPU, memory)

2. **Application Metrics:**
   - Active cameras count
   - Processing FPS per camera
   - Detection counts
   - Database query performance

3. **System Metrics:**
   - Disk usage (database, output files)
   - Network traffic
   - Error rates

### Log Rotation

Configure log rotation for Docker containers:

```bash
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## API Documentation

### Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com/api`

### Authentication

Currently no authentication is implemented. For production, implement:
- JWT tokens
- API keys
- OAuth2

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "YOLO Detection Monitoring API"
}
```

#### Get Detections

```http
GET /detections?limit=100&offset=0&class_filter=person&activity_filter=moving
```

**Query Parameters:**
- `limit` (int): Maximum records (1-1000, default: 100)
- `offset` (int): Skip records (default: 0)
- `class_filter` (string): Filter by class ("person", "train")
- `activity_filter` (string): Filter by activity ("standing", "moving", "stopped")
- `camera_id` (string): Filter by camera ID

**Response:**
```json
{
  "total": 1500,
  "limit": 100,
  "offset": 0,
  "detections": [
    {
      "id": 1,
      "track_id": 42,
      "class_name": "person",
      "activity": "moving",
      "confidence": 0.85,
      "timestamp": "2024-01-15 10:30:45",
      "camera_id": "camera-1"
    }
  ]
}
```

#### Get Current Statistics

```http
GET /stats/current
```

**Response:**
```json
{
  "person_count": 5,
  "train_count": 2,
  "total_tracks": 7,
  "timestamp": "2024-01-15 10:30:45"
}
```

#### Get Cameras

```http
GET /cameras
```

**Response:**
```json
{
  "cameras": [
    {
      "id": "camera-1",
      "name": "Camera 1",
      "status": "active",
      "stats": {
        "person_count": 3,
        "train_count": 1,
        "total_tracks": 4,
        "timestamp": "2024-01-15 10:30:45"
      }
    }
  ],
  "total": 1
}
```

#### Get Camera Statistics

```http
GET /cameras/{camera_id}/stats
```

**Response:**
```json
{
  "person_count": 3,
  "train_count": 1,
  "total_tracks": 4,
  "timestamp": "2024-01-15 10:30:45"
}
```

### Error Responses

**400 Bad Request:**
```json
{
  "error": "Invalid request parameters: ...",
  "status_code": 400
}
```

**404 Not Found:**
```json
{
  "error": "Camera camera-1 not found",
  "status_code": 404
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "status_code": 500
}
```

### API Documentation (Swagger)

Interactive API documentation available at:
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs ai-service
docker-compose logs api
```

**Common issues:**
- Missing configuration files
- Port conflicts
- Insufficient resources
- Docker daemon not running

### AI Service Not Processing

**Verify:**
1. Camera configuration exists: `config/cameras.json`
2. Video files are accessible: `ls -la data/raw/`
3. Models are present: `ls -la models/`
4. State sync file is created: `ls -la data/shared_state_sync.json`

**Check logs:**
```bash
docker-compose logs -f ai-service
```

**Common issues:**
- Invalid video source path
- Missing YOLO models
- CUDA/GPU issues
- Insufficient memory

### API Not Responding

**Verify:**
1. API container is running: `docker-compose ps api`
2. Health check passes: `curl http://localhost:8000/health`
3. Database is accessible: `ls -la data/database/logs.db`

**Check logs:**
```bash
docker-compose logs -f api
```

**Common issues:**
- Database file permissions
- Port 8000 already in use
- Missing dependencies

### Frontend Not Loading

**Verify:**
1. Frontend container is running: `docker-compose ps frontend`
2. Nginx is proxying correctly: `curl http://localhost/`
3. API is accessible: `curl http://localhost/api/health`

**Check logs:**
```bash
docker-compose logs -f frontend
docker-compose logs -f nginx
```

**Common issues:**
- Build artifacts missing
- Nginx configuration errors
- CORS issues

### Database Issues

**Check database:**
```bash
# Access database
sqlite3 data/database/logs.db

# Check tables
.tables

# Check records
SELECT COUNT(*) FROM logs;

# Check recent entries
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;
```

**Common issues:**
- Database file locked
- Insufficient disk space
- Corrupted database file

### Performance Issues

**Monitor resources:**
```bash
# Container resource usage
docker stats

# Disk usage
df -h
du -sh data/

# Process monitoring
docker-compose top
```

**Optimization:**
- Reduce video resolution
- Limit number of cameras
- Use GPU acceleration
- Increase container resources

---

## Maintenance

### Backup Procedures

**Database Backup:**
```bash
# Create backup
cp data/database/logs.db data/database/logs.db.backup.$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backup/ai-hackathon"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp data/database/logs.db $BACKUP_DIR/logs_$DATE.db
# Keep last 7 days
find $BACKUP_DIR -name "logs_*.db" -mtime +7 -delete
```

**Configuration Backup:**
```bash
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

### Database Maintenance

**Vacuum database:**
```bash
sqlite3 data/database/logs.db "VACUUM;"
```

**Remove old records:**
```sql
-- Remove records older than 30 days
DELETE FROM logs WHERE timestamp < datetime('now', '-30 days');
```

### Updates and Upgrades

**Update application:**
```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

**Rollback procedure:**
```bash
# Stop services
docker-compose down

# Restore previous version
git checkout <previous-commit>

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Log Rotation

**Application logs:**
- Configure Docker log rotation (see Monitoring section)
- Rotate Nginx logs via logrotate

**Database cleanup:**
- Implement retention policy
- Archive old records
- Regular database vacuum

---

## Security Considerations

### Current Security Status

- No authentication/authorization implemented
- CORS allows all origins
- No rate limiting
- HTTP only (no HTTPS in default configuration)

### Production Security Recommendations

1. **Implement Authentication:**
   - Add JWT token authentication
   - Implement API key validation
   - Use OAuth2 for user authentication

2. **Network Security:**
   - Configure HTTPS/TLS
   - Restrict CORS origins
   - Implement rate limiting
   - Use firewall rules

3. **Container Security:**
   - Run containers as non-root user
   - Use read-only file systems where possible
   - Limit container capabilities
   - Scan images for vulnerabilities

4. **Data Security:**
   - Encrypt sensitive data
   - Secure database access
   - Implement backup encryption
   - Regular security audits

---

## Support and Resources

### Documentation

- API Documentation: `http://localhost:8000/docs`
- Configuration Examples: `../config/cameras.json.example`
- Source Code: Repository root directory
- Main README: `../README.md`

### Logs and Debugging

- Service logs: `docker-compose logs`
- Application logs: Container stdout/stderr
- Database: `data/database/logs.db`
- State sync: `data/shared_state_sync.json`

### Contact

For deployment issues, check:
1. Service logs
2. Health check endpoints
3. Container status
4. Configuration files

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Maintained By:** DevOps Team

