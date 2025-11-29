#!/bin/bash
# Docker container health check script for production
# Usage: ./scripts/check_docker.sh

echo "=== Docker Container Health Check ==="
echo ""

# 1. Check all service containers
echo "1. Checking container status..."
CONTAINERS=$(docker ps -a --filter "name=ai-hackathon" --format "{{.Names}}")

if [ -n "$CONTAINERS" ]; then
    echo "Found containers:"
    docker ps -a --filter "name=ai-hackathon" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
else
    echo "No containers found. Run: docker-compose up -d"
    exit 1
fi
echo ""

# 2. Check healthcheck status for all services
echo "2. Checking healthcheck status..."
SERVICES=("ai-hackathon-ai" "ai-hackathon-api" "ai-hackathon-frontend" "ai-hackathon-nginx")
for SERVICE in "${SERVICES[@]}"; do
    CONTAINER_ID=$(docker ps -q --filter "name=$SERVICE" | head -n 1)
    if [ -n "$CONTAINER_ID" ]; then
        HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null)
        if [ -n "$HEALTH_STATUS" ]; then
            if [ "$HEALTH_STATUS" = "healthy" ]; then
                echo "  $SERVICE : $HEALTH_STATUS" | grep --color=always "healthy"
            elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
                echo "  $SERVICE : $HEALTH_STATUS" | grep --color=always "unhealthy"
            else
                echo "  $SERVICE : $HEALTH_STATUS (starting...)"
            fi
        else
            STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER_ID" 2>/dev/null)
            echo "  $SERVICE : $STATUS (no healthcheck)"
        fi
    else
        echo "  $SERVICE : not running"
    fi
done
echo ""

# 3. Check service endpoints
echo "3. Checking service endpoints..."
if curl -s -f -m 2 http://localhost:8000/health >/dev/null 2>&1; then
    echo "  API (http://localhost:8000): OK"
else
    echo "  API (http://localhost:8000): Not responding"
fi

if curl -s -f -m 2 http://localhost/health >/dev/null 2>&1; then
    echo "  Nginx (http://localhost): OK"
else
    echo "  Nginx (http://localhost): Not responding"
fi
echo ""

# 4. Check resource usage
echo "4. Checking resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker ps -q --filter "name=ai-hackathon") 2>/dev/null
echo ""

echo "=== Health check completed ==="
echo ""
echo "Useful commands:"
echo "  docker-compose ps                    # All containers"
echo "  docker-compose logs -f               # All logs"
echo "  docker-compose logs -f api           # API logs"
echo "  docker-compose logs -f ai-service   # AI service logs"
echo "  docker-compose down                  # Stop all services"

