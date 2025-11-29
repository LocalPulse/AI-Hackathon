#!/bin/bash
# Script to start Docker containers for production
# Usage: ./scripts/start_docker.sh

echo "=== Docker Setup and Start ==="
echo ""

# 1. Check if Docker is running
echo "1. Checking Docker daemon..."
if docker version >/dev/null 2>&1; then
    echo "Docker is running"
    docker version --format "Docker version: {{.Server.Version}}" 2>&1 | head -n 1
    
    # Check Docker platform
    DOCKER_PLATFORM=$(docker version --format "{{.Server.Arch}}" 2>&1)
    if [ -n "$DOCKER_PLATFORM" ]; then
        echo "Docker platform: $DOCKER_PLATFORM"
        if [ "$IS_ARM" = true ] && [[ ! "$DOCKER_PLATFORM" =~ arm|aarch ]]; then
            echo "Warning: ARM system but Docker reports different platform"
            echo "         You may need to use --platform linux/arm64"
        fi
    fi
else
    echo "Docker daemon is not running!"
    echo ""
    echo "Please start Docker:"
    echo "  sudo systemctl start docker    # Linux"
    echo "  # Or start Docker Desktop application"
    exit 1
fi
echo ""

# 2. Check required directories
echo "2. Checking directories..."
REQUIRED_DIRS=("data" "config" "models")
for DIR in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        echo "Creating $DIR directory..."
        mkdir -p "$DIR"
    fi
done
echo "Directories ready"
echo ""

# 3. Check camera configuration
echo "3. Checking camera configuration..."
CONFIG_FILE="config/cameras.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Warning: $CONFIG_FILE not found"
    if [ -f "config/cameras.json.example" ]; then
        echo "Creating example config..."
        cp "config/cameras.json.example" "$CONFIG_FILE"
        echo "Created $CONFIG_FILE from example. Please edit it with your camera settings."
    else
        echo "Example config not found. Please create $CONFIG_FILE manually."
    fi
else
    echo "Camera configuration found: $CONFIG_FILE"
fi
echo ""

# 4. Build and start containers
echo "4. Building and starting containers..."
echo "Building all services in parallel..."
echo ""

docker-compose build --parallel
if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Services started successfully! ==="
    echo ""
    echo "Services:"
    echo "  Frontend:  http://localhost"
    echo "  API:       http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  docker-compose ps                    # Check container status"
    echo "  docker-compose logs -f               # View all logs"
    echo "  docker-compose logs -f api           # View API logs"
    echo "  docker-compose down                  # Stop all services"
    echo "  ./scripts/check_docker.sh            # Health check"
    echo ""
    echo "Waiting for services to be healthy..."
    sleep 5
    ./scripts/check_docker.sh
else
    echo ""
    echo "=== Failed to start services ==="
    echo "Check the error messages above"
    exit 1
fi

