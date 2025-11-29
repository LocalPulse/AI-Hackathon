# Development Environment Setup Script for Windows
# Supports x86_64 and ARM64
# Usage: .\scripts\setup_dev.ps1

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Set-Location $PROJECT_ROOT

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI-Hackathon Development Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Detect platform
$OS = "Windows"
$ARCH = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
$PROCESSOR_ARCH = $env:PROCESSOR_ARCHITECTURE

Write-Host "[INFO] Detected platform: $OS $ARCH ($PROCESSOR_ARCH)" -ForegroundColor Blue
Write-Host ""

function Print-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Python found: $pythonVersion"
        
        # Check Python version
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Print-Error "Python 3.10+ required, found $pythonVersion"
                exit 1
            }
        }
    } else {
        throw "Python not found"
    }
} catch {
    Print-Error "Python 3 not found"
    Write-Host "  Install Python 3.10+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check pip
Write-Host "2. Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Success "pip found"
    } else {
        throw "pip not found"
    }
} catch {
    Print-Warning "pip not found, installing..."
    python -m ensurepip --upgrade
}
Write-Host ""

# Check Node.js
Write-Host "3. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Node.js found: $nodeVersion"
        
        # Check Node.js version
        $versionMatch = $nodeVersion -match "v(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            if ($major -lt 18) {
                Print-Warning "Node.js 18+ recommended, found $nodeVersion"
            }
        }
    } else {
        throw "Node.js not found"
    }
} catch {
    Print-Error "Node.js not found"
    Write-Host "  Install Node.js 18+ from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check npm
Write-Host "4. Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Success "npm found: $npmVersion"
    } else {
        throw "npm not found"
    }
} catch {
    Print-Error "npm not found"
    exit 1
}
Write-Host ""

# Create required directories
Write-Host "5. Creating required directories..." -ForegroundColor Yellow
$requiredDirs = @(
    "data\database",
    "data\raw",
    "output",
    "config",
    "models"
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Print-Info "Created directory: $dir"
    }
}
Print-Success "Directories ready"
Write-Host ""

# Setup camera configuration
Write-Host "6. Setting up camera configuration..." -ForegroundColor Yellow
$configFile = "config\cameras.json"
if (-not (Test-Path $configFile)) {
    if (Test-Path "config\cameras.json.example") {
        Copy-Item "config\cameras.json.example" $configFile
        Print-Success "Created $configFile from example"
    } else {
        Print-Warning "$configFile not found, creating default..."
        try {
            python -m src.services.camera_manager --create-config $configFile 2>$null
        } catch {
            # Ignore errors if module not fully available
        }
    }
} else {
    Print-Success "Camera configuration exists: $configFile"
}
Write-Host ""

# Install Python dependencies
Write-Host "7. Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Print-Info "Installing from requirements.txt..."
    pip install --quiet -r requirements.txt
    Print-Success "Python dependencies installed"
} else {
    Print-Warning "requirements.txt not found"
}
Write-Host ""

# Install Node.js dependencies
Write-Host "8. Installing Node.js dependencies..." -ForegroundColor Yellow
if (Test-Path "web\frontend\package.json") {
    Set-Location "web\frontend"
    Print-Info "Installing frontend dependencies..."
    npm install --silent
    Print-Success "Frontend dependencies installed"
    Set-Location $PROJECT_ROOT
} else {
    Print-Warning "web\frontend\package.json not found"
}
Write-Host ""

# Verify installation
Write-Host "9. Verifying installation..." -ForegroundColor Yellow
try {
    python -c "import fastapi, ultralytics, cv2" 2>$null
    Print-Success "Python modules import successfully"
} catch {
    Print-Warning "Some Python modules may be missing"
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the development environment:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option 1: Docker (Recommended)" -ForegroundColor Cyan
Write-Host "    .\scripts\start_docker.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  Option 2: Local development" -ForegroundColor Cyan
Write-Host "    # Terminal 1: AI Service" -ForegroundColor Gray
Write-Host "    python -m src.services.camera_manager --config config\cameras.json" -ForegroundColor Gray
Write-Host ""
Write-Host "    # Terminal 2: API Service" -ForegroundColor Gray
Write-Host "    cd web\api" -ForegroundColor Gray
Write-Host "    uvicorn main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "    # Terminal 3: Frontend" -ForegroundColor Gray
Write-Host "    cd web\frontend" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Access points:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor Gray
Write-Host "  API:       http://localhost:8000" -ForegroundColor Gray
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

