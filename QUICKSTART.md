# Quick Start Guide

This guide helps you quickly set up and run the AI-Hackathon project for demonstration purposes.

## Prerequisites

Before running the setup script, ensure you have:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Docker Desktop** (optional, for containerized deployment) - [Download](https://www.docker.com/products/docker-desktop)

## Automated Setup

### Linux/macOS

```bash
# Clone the repository
git clone <repository-url>
cd AI-Hackathon

# Run setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

### Windows

```powershell
# Clone the repository
git clone <repository-url>
cd AI-Hackathon

# Run setup script
.\scripts\setup_dev.ps1
```

## What the Setup Script Does

1. **Checks Dependencies**
   - Verifies Python 3.10+ installation
   - Verifies Node.js 18+ installation
   - Checks for pip and npm

2. **Creates Required Directories**
   - `data/database/` - SQLite database storage
   - `data/raw/` - Video files
   - `output/` - Processed video output
   - `config/` - Configuration files
   - `models/` - YOLO model files

3. **Sets Up Configuration**
   - Creates `config/cameras.json` from example if missing
   - Validates configuration file structure

4. **Installs Dependencies**
   - Installs Python packages from `requirements.txt`
   - Installs Node.js packages for frontend

5. **Verifies Installation**
   - Tests Python module imports
   - Confirms all dependencies are available

## Running the Application

### Option 1: Docker (Recommended for Demo)

```bash
# Start all services with Docker
./scripts/start_docker.sh    # Linux/macOS
.\scripts\start_docker.ps1   # Windows
```

Access points:
- Frontend: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Terminal 1 - AI Service:**
```bash
python -m src.services.camera_manager --config config/cameras.json
```

**Terminal 2 - API Service:**
```bash
cd web/api
uvicorn main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd web/frontend
npm run dev
```

Access points:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Configuration

### Camera Configuration

Edit `config/cameras.json` to configure video sources:

```json
{
  "camera-1": {
    "source": "data/raw/sample.mov",
    "name": "Camera 1",
    "device": "cuda",
    "det_model": "yolo11m"
  }
}
```

**Video Source Options:**
- Local file: `"source": "data/raw/video.mov"`
- Webcam: `"source": 0` (0, 1, 2 for camera indices)
- RTSP stream: `"source": "rtsp://user:pass@ip:port/stream"`

### Environment Variables

Copy `.env.example` to `.env` if you need to customize:
```bash
cp .env.example .env
```

## Troubleshooting

### Python Dependencies Not Installing

```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Node.js Dependencies Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf web/frontend/node_modules
cd web/frontend
npm install
```

### Port Already in Use

If ports 8000 or 5173 are in use:

**API Service:**
```bash
uvicorn main:app --reload --port 8001
```

**Frontend:**
Edit `web/frontend/vite.config.ts` to change port

### Docker Issues

```bash
# Check Docker status
docker ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

## Verification

Run the verification script to check setup:

```bash
python docs/test_camera_manager.py
```

This checks:
- Module imports
- Configuration files
- Video file availability

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment
- Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture

## Support

For issues during setup:
1. Check error messages in the setup script output
2. Verify all prerequisites are installed
3. Review logs: `docker-compose logs` (if using Docker)
4. Run verification script: `python docs/test_camera_manager.py`

