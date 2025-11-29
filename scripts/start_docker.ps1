# Script to start Docker and build/run containers
# Usage: .\scripts\start_docker.ps1 [cpu|cuda]

param(
    [string]$Mode = "cpu"
)

$ErrorActionPreference = "Continue"

Write-Host "=== Docker Setup and Start ===" -ForegroundColor Cyan
Write-Host ""

# 0. Check system architecture
Write-Host "0. Checking system architecture..." -ForegroundColor Yellow
$arch = $env:PROCESSOR_ARCHITECTURE
$archW6432 = $env:PROCESSOR_ARCHITEW6432
$isArm = $false
$isAppleSilicon = $false

# Check for ARM architecture
if ($arch -eq "ARM64" -or $archW6432 -eq "ARM64") {
    $isArm = $true
    Write-Host "Architecture: ARM64 detected" -ForegroundColor Cyan
    # On Windows, ARM64 usually means Surface Pro X or similar, not Apple Silicon
    # Apple Silicon would be on macOS
} else {
    Write-Host "Architecture: $arch (x86/x64)" -ForegroundColor Green
}

# Check OS for macOS (which could be Apple Silicon)
$osInfo = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
if (-not $osInfo) {
    # Try to detect if running on macOS via WSL or other means
    $uname = bash -c "uname -m" 2>$null
    if ($uname -eq "arm64" -or $uname -eq "aarch64") {
        $isArm = $true
        $macVersion = bash -c "sw_vers -productVersion" 2>$null
        if ($macVersion) {
            $isAppleSilicon = $true
            Write-Host "Detected: macOS on Apple Silicon (M1/M2/M3)" -ForegroundColor Cyan
        }
    }
}

if ($isAppleSilicon) {
    Write-Host ""
    Write-Host "Warning: Apple Silicon detected!" -ForegroundColor Yellow
    Write-Host "   CUDA is not supported on Apple Silicon." -ForegroundColor Yellow
    Write-Host "   Using CPU mode with optimized builds." -ForegroundColor Yellow
    if ($Mode -eq "cuda") {
        Write-Host "   Switching from CUDA to CPU mode..." -ForegroundColor Yellow
        $Mode = "cpu"
    }
    Write-Host ""
    Write-Host "   Note: For better performance on Apple Silicon, consider:" -ForegroundColor Cyan
    Write-Host "   - Using Metal Performance Shaders (MPS) backend" -ForegroundColor Gray
    Write-Host "   - Building with platform: linux/arm64" -ForegroundColor Gray
} elseif ($isArm) {
    Write-Host ""
    Write-Host "Warning: ARM architecture detected!" -ForegroundColor Yellow
    Write-Host "   CUDA is not supported on ARM." -ForegroundColor Yellow
    if ($Mode -eq "cuda") {
        Write-Host "   Switching from CUDA to CPU mode..." -ForegroundColor Yellow
        $Mode = "cpu"
    }
}
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
            if ($isArm -and $dockerPlatform -notlike "*arm*" -and $dockerPlatform -notlike "*aarch*") {
                Write-Host "Warning: ARM system but Docker reports different platform" -ForegroundColor Yellow
                Write-Host "         You may need to use --platform linux/arm64" -ForegroundColor Yellow
            }
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

# 1.5. Check for GPU support
Write-Host "1.5. Checking GPU support..." -ForegroundColor Yellow
try {
    $nvidiaSmi = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        $gpuName = ($nvidiaSmi | Select-String "NVIDIA.*GeForce|NVIDIA.*RTX|NVIDIA.*GTX|NVIDIA.*Quadro" | Select-Object -First 1).ToString()
        if ($gpuName) {
            Write-Host "NVIDIA GPU detected: $gpuName" -ForegroundColor Green
        } else {
            Write-Host "NVIDIA GPU detected" -ForegroundColor Green
        }
        
        # Check if Docker can access GPU
        $dockerGpuTest = docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi 2>&1 | Select-String "NVIDIA-SMI"
        if ($dockerGpuTest) {
            Write-Host "Docker GPU support: Available" -ForegroundColor Green
            if ($Mode -eq "cpu") {
                Write-Host ""
                Write-Host "Note: GPU detected but running in CPU mode." -ForegroundColor Yellow
                Write-Host "      To use GPU, run: .\scripts\start_docker.ps1 cuda" -ForegroundColor Cyan
            }
        } else {
            Write-Host "Docker GPU support: Not available (NVIDIA Container Toolkit may be missing)" -ForegroundColor Yellow
            if ($Mode -eq "cuda") {
                Write-Host "Warning: CUDA mode requested but GPU not accessible in Docker!" -ForegroundColor Red
                Write-Host "         Falling back to CPU mode or install NVIDIA Container Toolkit" -ForegroundColor Yellow
                $Mode = "cpu"
            }
        }
    } else {
        Write-Host "No NVIDIA GPU detected" -ForegroundColor Yellow
        if ($Mode -eq "cuda") {
            Write-Host "Warning: CUDA mode requested but no GPU found. Using CPU mode instead." -ForegroundColor Yellow
            $Mode = "cpu"
        }
    }
} catch {
    Write-Host "Could not check for GPU (nvidia-smi not found)" -ForegroundColor Yellow
    if ($Mode -eq "cuda") {
        Write-Host "Warning: CUDA mode requested but GPU check failed. Using CPU mode instead." -ForegroundColor Yellow
        $Mode = "cpu"
    }
}
Write-Host ""

# 2. Create output directory if it doesn't exist
Write-Host "2. Checking directories..." -ForegroundColor Yellow
if (-not (Test-Path "output")) {
    Write-Host "Creating output directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "output" | Out-Null
    Write-Host "Output directory created" -ForegroundColor Green
} else {
    Write-Host "Output directory exists" -ForegroundColor Green
}
Write-Host ""

# 3. Check if video file exists
Write-Host "3. Checking video file..." -ForegroundColor Yellow
$videoFile = "data\raw\video.mp4"
if (-not (Test-Path $videoFile)) {
    Write-Host "Warning: $videoFile not found" -ForegroundColor Yellow
    Write-Host "Available files in data\raw:" -ForegroundColor Cyan
    Get-ChildItem "data\raw\" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "Note: Update docker-compose.yml to use the correct video file" -ForegroundColor Yellow
} else {
    Write-Host "Video file found: $videoFile" -ForegroundColor Green
}
Write-Host ""

# 4. Build and start containers
Write-Host "4. Building and starting containers..." -ForegroundColor Yellow
Write-Host "Mode: $Mode" -ForegroundColor Cyan
Write-Host ""

Set-Location docker

# Build with platform specification for ARM
$buildArgs = @()
if ($isArm -or $isAppleSilicon) {
    $buildArgs += "--platform", "linux/arm64"
    Write-Host "Building for ARM64 platform..." -ForegroundColor Cyan
}

if ($Mode -eq "cuda") {
    Write-Host "Building CUDA version..." -ForegroundColor Cyan
    if ($isArm -or $isAppleSilicon) {
        Write-Host "Warning: CUDA not supported on ARM, but continuing with build..." -ForegroundColor Yellow
    }
    docker-compose -f docker-compose.yml -f docker-compose.cuda.yml up --build -d
} else {
    Write-Host "Building CPU version..." -ForegroundColor Cyan
    if ($buildArgs.Count -gt 0) {
        # For ARM, we need to specify platform in docker-compose
        $env:DOCKER_DEFAULT_PLATFORM = "linux/arm64"
        docker-compose up --build -d
        Remove-Item Env:\DOCKER_DEFAULT_PLATFORM -ErrorAction SilentlyContinue
    } else {
        docker-compose up --build -d
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Containers started successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  docker-compose ps              # Check container status" -ForegroundColor Gray
    Write-Host "  docker-compose logs -f         # View logs" -ForegroundColor Gray
    Write-Host "  docker-compose down           # Stop containers" -ForegroundColor Gray
    Write-Host "  .\scripts\check_docker.ps1    # Health check" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "=== Failed to start containers ===" -ForegroundColor Red
    Write-Host "Check the error messages above" -ForegroundColor Yellow
}

Set-Location ..

