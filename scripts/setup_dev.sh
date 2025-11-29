#!/bin/bash
# Development Environment Setup Script
# Supports Linux and macOS (x86_64 and ARM64)
# Usage: ./scripts/setup_dev.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "AI-Hackathon Development Setup"
echo "=========================================="
echo ""

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "[INFO] Detected platform: $OS $ARCH"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python found: $PYTHON_VERSION"
    
    # Check Python version (3.10+)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 3.10+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found"
    echo "  Install Python 3.10+ from: https://www.python.org/downloads/"
    exit 1
fi
echo ""

# Check pip
echo "2. Checking pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip found"
else
    print_warning "pip not found, installing..."
    python3 -m ensurepip --upgrade
fi
echo ""

# Check Node.js
echo "3. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
    
    # Check Node.js version (18+)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -lt 18 ]; then
        print_warning "Node.js 18+ recommended, found $NODE_VERSION"
    fi
else
    print_error "Node.js not found"
    echo "  Install Node.js 18+ from: https://nodejs.org/"
    exit 1
fi
echo ""

# Check npm
echo "4. Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm found: $NPM_VERSION"
else
    print_error "npm not found"
    exit 1
fi
echo ""

# Create required directories
echo "5. Creating required directories..."
REQUIRED_DIRS=("data/database" "data/raw" "output" "config" "models")
for DIR in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        mkdir -p "$DIR"
        print_info "Created directory: $DIR"
    fi
done
print_success "Directories ready"
echo ""

# Setup camera configuration
echo "6. Setting up camera configuration..."
CONFIG_FILE="config/cameras.json"
if [ ! -f "$CONFIG_FILE" ]; then
    if [ -f "config/cameras.json.example" ]; then
        cp "config/cameras.json.example" "$CONFIG_FILE"
        print_success "Created $CONFIG_FILE from example"
    else
        print_warning "$CONFIG_FILE not found, creating default..."
        python3 -m src.services.camera_manager --create-config "$CONFIG_FILE" 2>/dev/null || true
    fi
else
    print_success "Camera configuration exists: $CONFIG_FILE"
fi
echo ""

# Install Python dependencies
echo "7. Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    pip3 install --user -q -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found"
fi
echo ""

# Install Node.js dependencies
echo "8. Installing Node.js dependencies..."
if [ -f "web/frontend/package.json" ]; then
    cd web/frontend
    print_info "Installing frontend dependencies..."
    npm install --silent
    print_success "Frontend dependencies installed"
    cd "$PROJECT_ROOT"
else
    print_warning "web/frontend/package.json not found"
fi
echo ""

# Verify installation
echo "9. Verifying installation..."
if python3 -c "import fastapi, ultralytics, cv2" 2>/dev/null; then
    print_success "Python modules import successfully"
else
    print_warning "Some Python modules may be missing"
fi
echo ""

# Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the development environment:"
echo ""
echo "  Option 1: Docker (Recommended)"
echo "    ./scripts/start_docker.sh"
echo ""
echo "  Option 2: Local development"
echo "    # Terminal 1: AI Service"
echo "    python3 -m src.services.camera_manager --config config/cameras.json"
echo ""
echo "    # Terminal 2: API Service"
echo "    cd web/api && uvicorn main:app --reload"
echo ""
echo "    # Terminal 3: Frontend"
echo "    cd web/frontend && npm run dev"
echo ""
echo "Access points:"
echo "  Frontend:  http://localhost:5173"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""

