#!/bin/bash
# Script to start Docker and build/run containers
# Usage: ./scripts/start_docker.sh [cpu|cuda]

MODE=${1:-cpu}

echo "=== Docker Setup and Start ==="
echo ""

# 0. Check system architecture
echo "0. Checking system architecture..."
ARCH=$(uname -m)
OS=$(uname -s)
IS_ARM=false
IS_APPLE_SILICON=false

case "$ARCH" in
    arm64|aarch64)
        IS_ARM=true
        echo "Architecture: ARM64 detected" | grep --color=always "ARM64"
        
        # Check if it's macOS (Apple Silicon)
        if [ "$OS" = "Darwin" ]; then
            IS_APPLE_SILICON=true
            echo "Detected: macOS on Apple Silicon (M1/M2/M3)" | grep --color=always "Apple Silicon"
        else
            echo "Architecture: ARM64 (Linux/Other)"
        fi
        ;;
    x86_64|amd64)
        echo "Architecture: x86_64"
        ;;
    *)
        echo "Architecture: $ARCH (unknown)"
        ;;
esac

if [ "$IS_APPLE_SILICON" = true ]; then
    echo ""
    echo "Warning: Apple Silicon detected!"
    echo "   CUDA is not supported on Apple Silicon."
    echo "   Using CPU mode with optimized builds."
    if [ "$MODE" = "cuda" ]; then
        echo "   Switching from CUDA to CPU mode..."
        MODE="cpu"
    fi
    echo ""
    echo "   Note: For better performance on Apple Silicon, consider:"
    echo "   - Using Metal Performance Shaders (MPS) backend"
    echo "   - Building with platform: linux/arm64"
elif [ "$IS_ARM" = true ]; then
    echo ""
    echo "Warning: ARM architecture detected!"
    echo "   CUDA is not supported on ARM."
    if [ "$MODE" = "cuda" ]; then
        echo "   Switching from CUDA to CPU mode..."
        MODE="cpu"
    fi
fi
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

# 2. Create output directory if it doesn't exist
echo "2. Checking directories..."
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output
    echo "Output directory created"
else
    echo "Output directory exists"
fi
echo ""

# 3. Check if video file exists
echo "3. Checking video file..."
VIDEO_FILE="data/raw/video.mp4"
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Warning: $VIDEO_FILE not found"
    echo "Available files in data/raw:"
    ls -1 data/raw/ 2>/dev/null | sed 's/^/  - /'
    echo ""
    echo "Note: Update docker-compose.yml to use the correct video file"
else
    echo "Video file found: $VIDEO_FILE"
fi
echo ""

# 4. Build and start containers
echo "4. Building and starting containers..."
echo "Mode: $MODE"
echo ""

cd docker

# Build with platform specification for ARM
BUILD_ARGS=""
if [ "$IS_ARM" = true ] || [ "$IS_APPLE_SILICON" = true ]; then
    BUILD_ARGS="--platform linux/arm64"
    echo "Building for ARM64 platform..."
fi

if [ "$MODE" = "cuda" ]; then
    echo "Building CUDA version..."
    if [ "$IS_ARM" = true ] || [ "$IS_APPLE_SILICON" = true ]; then
        echo "Warning: CUDA not supported on ARM, but continuing with build..."
    fi
    docker-compose -f docker-compose.yml -f docker-compose.cuda.yml up --build -d
else
    echo "Building CPU version..."
    if [ "$IS_ARM" = true ] || [ "$IS_APPLE_SILICON" = true ]; then
        # For ARM, set platform via environment variable
        export DOCKER_DEFAULT_PLATFORM="linux/arm64"
        docker-compose up --build -d
        unset DOCKER_DEFAULT_PLATFORM
    else
        docker-compose up --build -d
    fi
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Containers started successfully! ==="
    echo ""
    echo "Useful commands:"
    echo "  docker-compose ps              # Check container status"
    echo "  docker-compose logs -f         # View logs"
    echo "  docker-compose down            # Stop containers"
    echo "  ./scripts/check_docker.sh      # Health check"
else
    echo ""
    echo "=== Failed to start containers ==="
    echo "Check the error messages above"
fi

cd ..

