# Script to start Docker containers for production
# Usage: .\scripts\start_docker.ps1

$ErrorActionPreference = "Continue"

Write-Host "=== Docker Setup and Start ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check if Docker is running
Write-Host "1. Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker is running" -ForegroundColor Green
        docker version --format "Docker version: {{.Server.Version}}" 2>&1 | Select-Object -First 1
        
        # Check Docker platform
        $dockerPlatform = docker version --format "{{.Server.Arch}}" 2>&1
        if ($dockerPlatform) {
            Write-Host "Docker platform: $dockerPlatform" -ForegroundColor Cyan
        }
    } else {
        Write-Host "Docker daemon is not running!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please start Docker Desktop:" -ForegroundColor Yellow
        Write-Host "  1. Open Docker Desktop application" -ForegroundColor Gray
        Write-Host "  2. Wait for it to start (whale icon in system tray)" -ForegroundColor Gray
        Write-Host "  3. Run this script again" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Or start Docker Desktop from command line:" -ForegroundColor Yellow
        Write-Host "  Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "Docker is not installed or not accessible!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host ""


# 2. Check required directories
Write-Host "2. Checking directories..." -ForegroundColor Yellow
$requiredDirs = @("data", "config", "models")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        Write-Host "Creating $dir directory..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "Directories ready" -ForegroundColor Green
Write-Host ""

# 3. Check camera configuration
Write-Host "3. Checking camera configuration..." -ForegroundColor Yellow
$configFile = "config\cameras.json"
if (-not (Test-Path $configFile)) {
    Write-Host "Warning: $configFile not found" -ForegroundColor Yellow
    Write-Host "Creating example config..." -ForegroundColor Cyan
    if (Test-Path "config\cameras.json.example") {
        Copy-Item "config\cameras.json.example" $configFile
        Write-Host "Created $configFile from example. Please edit it with your camera settings." -ForegroundColor Yellow
    } else {
        Write-Host "Example config not found. Please create $configFile manually." -ForegroundColor Red
    }
} else {
    Write-Host "Camera configuration found: $configFile" -ForegroundColor Green
}
Write-Host ""

# 4. Build and start containers
Write-Host "4. Building and starting containers..." -ForegroundColor Yellow
Write-Host "Building all services in parallel..." -ForegroundColor Cyan
Write-Host ""

docker-compose build --parallel
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Starting services..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Services started successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    Write-Host "  Frontend:  http://localhost" -ForegroundColor Gray
    Write-Host "  API:       http://localhost:8000" -ForegroundColor Gray
    Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  docker-compose ps                    # Check container status" -ForegroundColor Gray
    Write-Host "  docker-compose logs -f               # View all logs" -ForegroundColor Gray
    Write-Host "  docker-compose logs -f api           # View API logs" -ForegroundColor Gray
    Write-Host "  docker-compose down                  # Stop all services" -ForegroundColor Gray
    Write-Host "  .\scripts\check_docker.ps1          # Health check" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Waiting for services to be healthy..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5
    .\scripts\check_docker.ps1
} else {
    Write-Host ""
    Write-Host "=== Failed to start services ===" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
    exit 1
}

