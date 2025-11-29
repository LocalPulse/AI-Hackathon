#!/bin/bash
# Docker container health check script
# Usage: ./scripts/check_docker.sh

echo "=== Docker Container Health Check ==="
echo ""

# 1. Check container status
echo "1. Checking container status..."
# Try to find CPU or CUDA container
CONTAINER_ID=$(docker ps -q --filter "name=docker-pipeline" | head -n 1)
if [ -z "$CONTAINER_ID" ]; then
    CONTAINER_ID=$(docker ps -q --filter "ancestor=ai-hackathon:cpu" | head -n 1)
fi
if [ -z "$CONTAINER_ID" ]; then
    CONTAINER_ID=$(docker ps -q --filter "ancestor=ai-hackathon:cuda" | head -n 1)
fi

if [ -n "$CONTAINER_ID" ]; then
    echo "Found containers:"
    docker ps -a --filter "name=docker-pipeline" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"
    
    # Check which image is being used
    IMAGE_NAME=$(docker inspect --format='{{.Config.Image}}' "$CONTAINER_ID" 2>/dev/null)
    if echo "$IMAGE_NAME" | grep -q "cuda"; then
        echo "Container mode: CUDA (GPU)"
    else
        echo "Container mode: CPU"
    fi
else
    echo "No containers found. Run: docker-compose up"
    exit 1
fi
echo ""

# 2. Check healthcheck status
echo "2. Checking healthcheck status..."
if [ -n "$CONTAINER_ID" ]; then
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null)
    if [ -n "$HEALTH_STATUS" ]; then
        if [ "$HEALTH_STATUS" = "healthy" ]; then
            echo "Healthcheck: $HEALTH_STATUS" | grep --color=always "healthy"
        elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
            echo "Healthcheck: $HEALTH_STATUS" | grep --color=always "unhealthy"
        else
            echo "Healthcheck: $HEALTH_STATUS (starting...)"
        fi
    else
        echo "Healthcheck not available"
    fi
else
    echo "No active container found"
fi
echo ""

# 3. Check logs (last 20 lines)
echo "3. Checking container logs (last 20 lines)..."
if [ -n "$CONTAINER_ID" ]; then
    echo "Logs for container $CONTAINER_ID:"
    docker logs --tail 20 "$CONTAINER_ID"
else
    echo "No active container found"
fi
echo ""

# 4. Check Python environment and dependencies
echo "4. Checking Python environment..."
if [ -n "$CONTAINER_ID" ]; then
    echo "Checking torch import..."
    docker exec "$CONTAINER_ID" python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA device count:', torch.cuda.device_count() if torch.cuda.is_available() else 0); print('Current device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>&1
    
    echo "Checking ultralytics import..."
    docker exec "$CONTAINER_ID" python -c "import ultralytics; print('Ultralytics installed')" 2>&1
    
    echo "Checking model files..."
    docker exec "$CONTAINER_ID" ls -lh /app/models/ 2>&1
else
    echo "No active container found"
fi
echo ""

# 5. Check data mounts
echo "5. Checking data mounts..."
if [ -n "$CONTAINER_ID" ]; then
    echo "Checking /app/data:"
    docker exec "$CONTAINER_ID" ls -lh /app/data/ 2>&1
    
    echo "Checking /app/output:"
    docker exec "$CONTAINER_ID" ls -lh /app/output/ 2>&1
else
    echo "No active container found"
fi
echo ""

# 6. Check resource usage
echo "6. Checking resource usage..."
if [ -n "$CONTAINER_ID" ]; then
    docker stats "$CONTAINER_ID" --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
else
    echo "No active container found"
fi
echo ""

echo "=== Health check completed ==="
echo ""
echo "Useful commands:"
echo "  docker ps -a                          # All containers"
echo "  docker logs <container_id>            # Full logs"
echo "  docker exec -it <container_id> bash   # Enter container"
echo "  docker inspect <container_id>         # Detailed info"

