<#
.SYNOPSIS
    Complete setup script for AI-Hackathon on Windows with NVIDIA GPU.

.DESCRIPTION
    This script:
    1. Checks Python version (requires 3.10-3.12, NOT 3.13+)
    2. Creates virtual environment
    3. Installs PyTorch with CUDA support
    4. Installs all dependencies
    5. Downloads YOLO models

.PARAMETER PythonPath
    Path to Python 3.12 executable if not in PATH

.PARAMETER NoCuda
    Install CPU-only version (for testing without GPU)

.PARAMETER Models
    Models to download (default: yolo11m,yolo11x,yolo11x-pose)

.EXAMPLE
    .\scripts\setup_windows.ps1
    .\scripts\setup_windows.ps1 -PythonPath "C:\Python312\python.exe"
    .\scripts\setup_windows.ps1 -NoCuda
#>

[CmdletBinding()]
param(
    [string]$PythonPath = "",
    [switch]$NoCuda,
    [string]$Models = "yolo11m,yolo11x,yolo11x-pose"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-PythonVersion {
    param([string]$Python)
    
    try {
        $version = & $Python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        $major, $minor = $version -split '\.'
        
        if ([int]$major -eq 3 -and [int]$minor -ge 10 -and [int]$minor -le 12) {
            return @{ Valid = $true; Version = $version }
        }
        return @{ Valid = $false; Version = $version }
    }
    catch {
        return @{ Valid = $false; Version = "not found" }
    }
}

function Find-Python312 {
    # Check common locations
    $candidates = @(
        "python3.12",
        "python312",
        "python",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
    )
    
    foreach ($py in $candidates) {
        $result = Test-PythonVersion -Python $py
        if ($result.Valid) {
            return $py
        }
    }
    return $null
}

function Test-NvidiaGpu {
    try {
        $nvs = & nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>$null
        if ($LASTEXITCODE -eq 0 -and $nvs) {
            return @{ Available = $true; Info = $nvs.Trim() }
        }
    }
    catch {}
    return @{ Available = $false; Info = "Not detected" }
}

# ============ MAIN ============

Push-Location $ProjectRoot

try {
    # Step 1: Find Python
    Write-Step "Checking Python version"
    
    $python = if ($PythonPath) { $PythonPath } else { Find-Python312 }
    
    if (-not $python) {
        Write-Error "Python 3.10-3.12 not found!"
        Write-Host @"

PyTorch does NOT support Python 3.13+
Please install Python 3.12 from: https://www.python.org/downloads/release/python-3129/

After installation, run:
    .\scripts\setup_windows.ps1 -PythonPath "C:\Python312\python.exe"
"@
        exit 1
    }
    
    $pyVersion = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    Write-Success "Found Python $pyVersion at: $python"

    # Step 2: Check GPU
    Write-Step "Checking NVIDIA GPU"
    $gpu = Test-NvidiaGpu
    
    if ($gpu.Available -and -not $NoCuda) {
        Write-Success "GPU detected: $($gpu.Info)"
        $useCuda = $true
    }
    else {
        if ($NoCuda) {
            Write-Warning "CPU mode requested"
        }
        else {
            Write-Warning "No NVIDIA GPU detected, using CPU mode"
        }
        $useCuda = $false
    }

    # Step 3: Create venv
    Write-Step "Creating virtual environment"
    
    $venvPath = Join-Path $ProjectRoot ".venv"
    
    if (Test-Path $venvPath) {
        Write-Warning "Removing existing .venv..."
        Remove-Item -Recurse -Force $venvPath
    }
    
    & $python -m venv $venvPath
    Write-Success "Created .venv"

    # Activate and get pip path
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    $venvPip = Join-Path $venvPath "Scripts\pip.exe"

    # Step 4: Upgrade pip
    Write-Step "Upgrading pip"
    & $venvPython -m pip install --upgrade pip setuptools wheel --quiet
    Write-Success "pip upgraded"

    # Step 5: Install PyTorch
    Write-Step "Installing PyTorch"
    
    if ($useCuda) {
        Write-Host "Installing PyTorch with CUDA 12.4 support..."
        & $venvPip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu124
    }
    else {
        Write-Host "Installing CPU PyTorch..."
        & $venvPip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyTorch installation failed!"
        exit 1
    }
    Write-Success "PyTorch installed"

    # Step 6: Verify CUDA
    Write-Step "Verifying PyTorch installation"
    $cudaCheck = & $venvPython -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
    Write-Host $cudaCheck
    
    if ($useCuda) {
        $cudaAvail = & $venvPython -c "import torch; print(torch.cuda.is_available())"
        if ($cudaAvail -ne "True") {
            Write-Warning "CUDA not available in PyTorch! Check NVIDIA drivers."
        }
        else {
            $gpuName = & $venvPython -c "import torch; print(torch.cuda.get_device_name(0))"
            Write-Success "CUDA enabled: $gpuName"
        }
    }

    # Step 7: Install other dependencies
    Write-Step "Installing dependencies"
    & $venvPip install --no-cache-dir ultralytics opencv-python-headless numpy
    Write-Success "Dependencies installed"

    # Step 8: Download models
    Write-Step "Downloading YOLO models"
    
    $modelsDir = Join-Path $ProjectRoot "models"
    if (-not (Test-Path $modelsDir)) {
        New-Item -ItemType Directory -Path $modelsDir | Out-Null
    }
    
    $modelList = $Models -split ","
    foreach ($model in $modelList) {
        $model = $model.Trim()
        $modelFile = Join-Path $modelsDir "$model.pt"
        
        if (Test-Path $modelFile) {
            Write-Host "  [skip] $model.pt already exists"
            continue
        }
        
        Write-Host "  Downloading $model..."
        try {
            # Set ULTRALYTICS_HOME to models directory
            $env:ULTRALYTICS_HOME = $modelsDir
            Push-Location $ProjectRoot
            
            & $venvPython -c "from ultralytics import YOLO; YOLO('$model')" 2>$null
            
            # Check multiple possible locations where model might be downloaded
            $defaultPaths = @(
                "$model.pt",  # Current directory
                (Join-Path $ProjectRoot "$model.pt"),  # Project root
                (Join-Path $env:USERPROFILE ".ultralytics\weights\$model.pt")  # Default ultralytics location
            )
            
            $found = $false
            foreach ($defaultPath in $defaultPaths) {
                if (Test-Path $defaultPath) {
                    Move-Item $defaultPath $modelFile -Force
                    Write-Host "  [OK] $model.pt (moved from $defaultPath)"
                    $found = $true
                    break
                }
            }
            
            # Also check if model was already downloaded to models/ by ultralytics
            if (-not $found -and (Test-Path $modelFile)) {
                Write-Host "  [OK] $model.pt (already in models/)"
                $found = $true
            }
            
            if (-not $found) {
                Write-Warning "  Model file not found after download. Check ultralytics cache."
            }
            
            Pop-Location
        }
        catch {
            Pop-Location
            Write-Warning "  Failed to download $model`: $_"
        }
        finally {
            # Clean up environment variable
            if ($env:ULTRALYTICS_HOME) {
                Remove-Item Env:\ULTRALYTICS_HOME
            }
        }
    }

    # Step 9: Clear pycache
    Write-Step "Cleaning up"
    Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue | 
        ForEach-Object { Remove-Item -Recurse -Force (Join-Path $ProjectRoot $_) -ErrorAction SilentlyContinue }
    Write-Success "Cache cleared"

    Write-Host "To activate the environment:" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "To run the pipeline:" -ForegroundColor Yellow
    Write-Host "    python -m src.services.video_stream --det-model yolo11x --pose-model yolo11x-pose --show --source data/raw/ремонты.mov" -ForegroundColor White
    Write-Host ""
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
finally {
    Pop-Location
}

