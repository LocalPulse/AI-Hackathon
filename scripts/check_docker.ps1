# Docker container health check script for production
# Usage: .\scripts\check_docker.ps1

$ErrorActionPreference = "Continue"

Write-Host "=== Docker Container Health Check ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check all service containers
Write-Host "1. Checking container status..." -ForegroundColor Yellow
$containers = docker ps -a --filter "name=ai-hackathon" --format "{{.Names}}" | Where-Object { $_ }

if ($containers) {
    Write-Host "Found containers:" -ForegroundColor Green
    docker ps -a --filter "name=ai-hackathon" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
} else {
    Write-Host "No containers found. Run: docker-compose up -d" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Check healthcheck status for all services
Write-Host "2. Checking healthcheck status..." -ForegroundColor Yellow
$services = @("ai-hackathon-ai", "ai-hackathon-api", "ai-hackathon-frontend", "ai-hackathon-nginx")
foreach ($service in $services) {
    $containerId = docker ps -q --filter "name=$service" | Select-Object -First 1
    if ($containerId) {
        $healthStatus = docker inspect --format='{{.State.Health.Status}}' $containerId 2>$null
        if ($healthStatus) {
            $color = if ($healthStatus -eq "healthy") { "Green" } elseif ($healthStatus -eq "unhealthy") { "Red" } else { "Yellow" }
            Write-Host "  $service : $healthStatus" -ForegroundColor $color
        } else {
            $status = docker inspect --format='{{.State.Status}}' $containerId 2>$null
            Write-Host "  $service : $status (no healthcheck)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  $service : not running" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Check service endpoints
Write-Host "3. Checking service endpoints..." -ForegroundColor Yellow
try {
    $apiHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($apiHealth.StatusCode -eq 200) {
        Write-Host "  API (http://localhost:8000): OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  API (http://localhost:8000): Not responding" -ForegroundColor Red
}

try {
    $nginxHealth = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($nginxHealth.StatusCode -eq 200) {
        Write-Host "  Nginx (http://localhost): OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  Nginx (http://localhost): Not responding" -ForegroundColor Red
}
Write-Host ""

# 4. Check resource usage
Write-Host "4. Checking resource usage..." -ForegroundColor Yellow
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker ps -q --filter "name=ai-hackathon") 2>$null
Write-Host ""

Write-Host "=== Health check completed ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  docker-compose ps                    # All containers" -ForegroundColor Gray
Write-Host "  docker-compose logs -f               # All logs" -ForegroundColor Gray
Write-Host "  docker-compose logs -f api           # API logs" -ForegroundColor Gray
Write-Host "  docker-compose logs -f ai-service    # AI service logs" -ForegroundColor Gray
Write-Host "  docker-compose down                  # Stop all services" -ForegroundColor Gray
