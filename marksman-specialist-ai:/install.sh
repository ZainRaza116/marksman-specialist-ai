#!/bin/bash
# Complete Installation Script for Markdown LSP Analyzer
# Fixes all structural issues and installs GUI interface

set -e  # Exit on any error

echo "🚀 MARKDOWN LSP ANALYZER - COMPLETE INSTALLATION"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
check_python() {
    log_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python 3 found: $PYTHON_VERSION"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python version is compatible (3.8+)"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    log_info "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
    else
        log_error "pip3 not found. Please install pip"
        exit 1
    fi
}

# Create proper project structure
setup_project_structure() {
    log_info "Setting up proper project structure..."
    
    # Run the structure setup script
    python3 -c "
import sys
sys.path.insert(0, '.')

# Create the project structure setup inline
exec('''
import os
from pathlib import Path

def create_structure():
    directories = [
        \"src\", \"src/marksman_analyzer\", \"src/marksman_analyzer/gui\",
        \"src/marksman_analyzer/core\", \"src/marksman_analyzer/api\",
        \"assets\", \"assets/icons\", \"assets/themes\", 
        \"tests\", \"docs\", \"examples\", \"workspace\"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True,