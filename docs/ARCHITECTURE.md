# System Architecture

## Overview

AI-Hackathon is a microservices-based system for real-time video object detection and tracking. The architecture follows a modular design with clear separation of concerns.

## Component Architecture

### Services

#### AI Service (`ai-service`)

**Purpose**: Video processing, object detection, and tracking

**Technology Stack**:
- Python 3.12
- YOLO11 (Ultralytics)
- OpenCV
- Multiprocessing

**Responsibilities**:
- Load and process video streams from configured cameras
- Perform object detection using YOLO11 models
- Track objects across video frames
- Classify object activity (standing, moving, stopped)
- Write detection results to state sync file
- Log activities to SQLite database

**Entry Point**: `src/services/camera_manager.py`

**Configuration**: `config/cameras.json`

**State Management**: File-based synchronization via `data/shared_state_sync.json`

#### API Service (`api`)

**Purpose**: RESTful API for monitoring and data access

**Technology Stack**:
- Python 3.12
- FastAPI
- Uvicorn
- SQLite

**Responsibilities**:
- Provide REST API endpoints for camera statistics
- Serve detection logs from database
- Read camera state from sync file
- Health check endpoint
- CORS handling

**Entry Point**: `web/api/main.py`

**Port**: 8000 (internal), proxied via Nginx

**Endpoints**:
- `GET /health` - Health check
- `GET /cameras` - List all cameras
- `GET /cameras/{id}/stats` - Camera statistics
- `GET /detections` - Detection logs
- `GET /stats/current` - Current statistics

#### Frontend Service (`frontend`)

**Purpose**: Web-based monitoring dashboard

**Technology Stack**:
- React 19
- TypeScript
- Vite
- Tailwind CSS
- React Query
- Zustand

**Responsibilities**:
- Display real-time camera statistics
- Show detection logs with filtering
- Visualize metrics and charts
- Provide user interface for monitoring

**Build**: Static files served via Nginx

**Port**: 5173 (internal), proxied via Nginx

#### Nginx Service (`nginx`)

**Purpose**: Reverse proxy and load balancer

**Technology Stack**:
- Nginx Alpine

**Responsibilities**:
- Route requests to appropriate services
- Serve static frontend files
- Proxy API requests
- SSL/TLS termination (when configured)
- Gzip compression
- CORS headers

**Port**: 80 (HTTP), 443 (HTTPS)

## Data Flow

### Video Processing Flow

```
Video Source
    ↓
AI Service (camera_manager)
    ↓
Pipeline (processor)
    ↓
Detection Worker (async)
    ↓
YOLO11 Model → Detections
    ↓
Tracker → Tracked Objects
    ↓
Activity Classifier → Activity Labels
    ↓
Track Processor
    ├─→ State Sync File (real-time)
    └─→ Database (persistent)
```

### API Request Flow

```
Client Request
    ↓
Nginx (port 80)
    ↓
API Service (port 8000)
    ├─→ Read State Sync File
    ├─→ Query SQLite Database
    └─→ Return JSON Response
    ↓
Nginx
    ↓
Client
```

### Frontend Request Flow

```
Browser
    ↓
Nginx (port 80)
    ├─→ Static Files (React build)
    └─→ API Proxy (/api/*)
        ↓
    API Service
```

## State Management

### File-Based Synchronization

**File**: `data/shared_state_sync.json`

**Purpose**: Real-time state sharing between AI Service processes and API Service

**Structure**:
```json
{
  "camera-1": {
    "tracks": [...],
    "heartbeat": 1234567890.0,
    "start_time": 1234567890.0,
    "status": "running"
  }
}
```

**Update Frequency**: Every 2 seconds (heartbeat), on track updates

**Access Pattern**: Read-heavy (API), write-heavy (AI Service)

### Database

**Type**: SQLite

**Location**: `data/database/logs.db`

**Schema**:
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    class TEXT NOT NULL,
    activity TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL,
    camera_id TEXT
);
```

**Access Pattern**: Write from AI Service, read from API Service

## Inter-Process Communication

### AI Service → API Service

- **Method**: File-based (shared_state_sync.json)
- **Frequency**: Real-time (every frame processing cycle)
- **Data**: Camera tracks, statistics, heartbeat

### AI Service → Database

- **Method**: SQLite direct connection
- **Frequency**: On activity changes, periodic (every 30s)
- **Data**: Detection logs with metadata

### API Service → Frontend

- **Method**: HTTP REST API
- **Frequency**: On-demand (polling/real-time updates)
- **Data**: JSON responses with camera stats and logs

## Resource Management

### CPU

- AI Service: CPU-intensive (video processing, detection)
- API Service: Low CPU usage (I/O bound)
- Frontend: Static files (no CPU usage at runtime)

### Memory

- AI Service: High (video frames, model weights, tracking data)
- API Service: Low (request handling, database queries)
- Frontend: Static files served by Nginx

### GPU (Optional)

- AI Service: CUDA acceleration for YOLO11 inference
- Other services: No GPU usage

### Storage

- Models: `models/` directory (YOLO model files)
- Data: `data/` directory (database, sync file, raw videos)
- Output: `output/` directory (processed videos)

## Scalability Considerations

### Horizontal Scaling

**Current Limitation**: File-based state sync does not scale horizontally

**Recommendations for Production**:
- Replace file sync with Redis or message queue
- Use PostgreSQL instead of SQLite
- Implement load balancing for API service
- Use CDN for frontend static files

### Vertical Scaling

- Increase container resources for AI Service
- Add GPU resources for faster processing
- Increase database connection pool size

## Security Architecture

### Current State

- No authentication/authorization
- CORS allows all origins
- HTTP only (no HTTPS)
- No rate limiting

### Production Recommendations

- Implement JWT authentication
- Configure HTTPS/TLS
- Restrict CORS origins
- Add rate limiting
- Use secrets management
- Implement network policies
- Run containers as non-root

## Monitoring Points

### Application Metrics

- Camera processing FPS
- Detection counts per camera
- Track counts
- Activity classifications
- API request latency
- Database query performance

### System Metrics

- Container CPU/memory usage
- Disk I/O
- Network traffic
- Health check status
- Error rates

### Logging

- Application logs: Container stdout/stderr
- Access logs: Nginx access.log
- Error logs: Nginx error.log, application exceptions
- Database: SQLite logs table

## Deployment Architecture

### Container Orchestration

- **Orchestrator**: Docker Compose
- **Network**: Bridge network (`ai-hackathon-network`)
- **Volumes**: Host-mounted volumes for data persistence
- **Health Checks**: Built into all services

### Service Dependencies

```
nginx
  ├─→ api (depends_on: service_healthy)
  └─→ frontend (depends_on: service_healthy)

api
  └─→ ai-service (depends_on: service_started)

ai-service
  └─→ (no dependencies)
```

### Volume Mounts

- `./data` → `/app/data` (AI Service, API Service)
- `./models` → `/app/models` (AI Service)
- `./output` → `/app/output` (AI Service)
- `./config` → `/app/config` (AI Service)

## Failure Handling

### AI Service Failure

- Health check detects missing sync file
- Container restart policy: `unless-stopped`
- API Service continues to serve cached data
- Frontend shows camera as inactive

### API Service Failure

- Health check fails
- Nginx returns 502 Bad Gateway
- Frontend shows error state
- AI Service continues processing

### Database Failure

- API Service returns error responses
- Logging continues in AI Service
- State sync file remains available
- Requires manual intervention

### Network Partition

- Services continue independently
- State sync file may become stale
- API may serve outdated data
- Requires reconciliation on recovery

