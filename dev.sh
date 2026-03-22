#!/bin/bash

# YoloHome Backend - Development Startup Script
# This script sets up a local development environment without Docker

set -e

echo "=========================================="
echo "  YoloHome IoT Backend - Development    "
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_info "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements-dev.txt
print_success "Dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp .env.example .env
    print_success ".env created from template"
fi

# Create SQLite database directory
mkdir -p instance

# Set development environment
export FLASK_ENV=development
export FLASK_APP="app.main:create_app()"

# Run database migrations
print_info "Initializing database..."
flask db init 2>/dev/null || true
flask db migrate -m "Initial migration" 2>/dev/null || true
flask db upgrade 2>/dev/null || true
print_success "Database ready"

# Run dev setup script
print_info "Running development setup..."
python scripts/dev_setup.py

echo ""
echo "=========================================="
echo "  Starting Development Server           "
echo "=========================================="
echo ""

# Start Flask development server (port 5001 to avoid macOS AirPlay conflict)
flask run --host=0.0.0.0 --port=5001 --debug