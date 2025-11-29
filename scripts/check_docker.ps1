# Docker container health check script
# Usage: .\scripts\check_docker.ps1

$ErrorActionPreference = "Continue"

Write-Host "=== Docker Container Health Check ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check container status
Write-Host "1. Checking container status..." -ForegroundColor Yellow
# Try to find CPU or CUDA container
$containerId = docker ps -q --filter "name=docker-pipeline" | Select-Object -First 1
if (-not $containerId) {
    $containerId = docker ps -q --filter "ancestor=ai-hackathon:cpu" | Select-Object -First 1
}
if (-not $containerId) {
    $containerId = docker ps -q --filter "ancestor=ai-hackathon:cuda" | Select-Object -First 1
}

if ($containerId) {
    Write-Host "Found containers:" -ForegroundColor Green
    docker ps -a --filter "name=docker-pipeline" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"
    
    # Check which image is being used
    $imageName = docker inspect --format='{{.Config.Image}}' $containerId 2>$null
    if ($imageName -like "*cuda*") {
        Write-Host "Container mode: CUDA (GPU)" -ForegroundColor Cyan
    } else {
        Write-Host "Container mode: CPU" -ForegroundColor Yellow
    }
} else {
    Write-Host "No containers found. Run: docker-compose up" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Check healthcheck status
Write-Host "2. Checking healthcheck status..." -ForegroundColor Yellow
if ($containerId) {
    $healthStatus = docker inspect --format='{{.State.Health.Status}}' $containerId 2>$null
    if ($healthStatus) {
        if ($healthStatus -eq "healthy") {
            Write-Host "Healthcheck: $healthStatus" -ForegroundColor Green
        } elseif ($healthStatus -eq "unhealthy") {
            Write-Host "Healthcheck: $healthStatus" -ForegroundColor Red
        } else {
            Write-Host "Healthcheck: $healthStatus (starting...)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Healthcheck not available" -ForegroundColor Yellow
    }
} else {
    Write-Host "No active container found" -ForegroundColor Red
}
Write-Host ""

# 3. Check logs (last 20 lines)
Write-Host "3. Checking container logs (last 20 lines)..." -ForegroundColor Yellow
if ($containerId) {
    Write-Host "Logs for container ${containerId}:" -ForegroundColor Cyan
    docker logs --tail 20 $containerId
} else {
    Write-Host "No active container found" -ForegroundColor Red
}
Write-Host ""

# 4. Check Python environment and dependencies
Write-Host "4. Checking Python environment..." -ForegroundColor Yellow
if ($containerId) {
    Write-Host "Checking torch import..." -ForegroundColor Cyan
    $torchCmd = "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA device count:', torch.cuda.device_count() if torch.cuda.is_available() else 0); print('Current device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
    docker exec $containerId python -c $torchCmd 2>&1
    
    Write-Host "Checking ultralytics import..." -ForegroundColor Cyan
    $ultralyticsCmd = "import ultralytics; print('Ultralytics installed')"
    docker exec $containerId python -c $ultralyticsCmd 2>&1
    
    Write-Host "Checking model files..." -ForegroundColor Cyan
    docker exec $containerId ls -lh /app/models/ 2>&1
} else {
    Write-Host "No active container found" -ForegroundColor Red
}
Write-Host ""

# 5. Check data mounts
Write-Host "5. Checking data mounts..." -ForegroundColor Yellow
if ($containerId) {
    Write-Host "Checking /app/data:" -ForegroundColor Cyan
    docker exec $containerId ls -lh /app/data/ 2>&1
    
    Write-Host "Checking /app/output:" -ForegroundColor Cyan
    docker exec $containerId ls -lh /app/output/ 2>&1
} else {
    Write-Host "No active container found" -ForegroundColor Red
}
Write-Host ""

# 6. Check resource usage
Write-Host "6. Checking resource usage..." -ForegroundColor Yellow
if ($containerId) {
    docker stats $containerId --no-stream --format "table {{.Container}}`t{{.CPUPerc}}`t{{.MemUsage}}`t{{.NetIO}}`t{{.BlockIO}}"
} else {
    Write-Host "No active container found" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Health check completed ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  docker ps -a                          # All containers" -ForegroundColor Gray
Write-Host "  docker logs <container_id>            # Full logs" -ForegroundColor Gray
Write-Host "  docker exec -it <container_id> bash   # Enter container" -ForegroundColor Gray
Write-Host "  docker inspect <container_id>         # Detailed info" -ForegroundColor Gray
