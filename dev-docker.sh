#!/bin/bash

# YoloHome Backend - Docker Development Startup Script
# This script sets up a development environment using Docker with PostgreSQL

set -e

echo "=========================================="
echo "  YoloHome IoT Backend - Docker Dev    "
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Stop any existing containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true

# Build and start containers
print_info "Building Docker images..."
docker-compose -f docker-compose.dev.yml build

print_info "Starting containers..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 5

# Run database migrations
print_info "Running database migrations..."
docker-compose -f docker-compose.dev.yml exec -T api flask db init 2>/dev/null || true
docker-compose -f docker-compose.dev.yml exec -T api flask db migrate -m "Initial migration" 2>/dev/null || true
docker-compose -f docker-compose.dev.yml exec -T api flask db upgrade 2>/dev/null || true

print_success "Database ready"

# Run dev setup script interactively
print_info "Running device setup..."
echo ""
echo "=========================================="
echo "  Device Setup                           "
echo "=========================================="
docker-compose -f docker-compose.dev.yml exec -it api python scripts/dev_setup.py

echo ""
echo "=========================================="
echo "  Development Environment Ready!         "
echo "=========================================="
echo ""
echo "API Server: http://localhost:5001"
echo "Database:   localhost:5432 (yolohome_dev)"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.dev.yml logs -f api"
echo "  Stop:         docker-compose -f docker-compose.dev.yml down"
echo "  Restart:      docker-compose -f docker-compose.dev.yml restart api"
echo "  Shell:        docker-compose -f docker-compose.dev.yml exec api bash"
echo ""