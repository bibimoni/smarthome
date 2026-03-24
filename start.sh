#!/bin/bash

# YoloHome Backend - Production Startup Script
# This script sets up and runs the entire YoloHome IoT backend system

set -e

echo "=========================================="
echo "  YoloHome IoT Backend - Startup Script  "
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }

# Check if .env file exists
if [ ! -f .env ]; then
    print_info ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success ".env file created. Please edit it with your credentials."
    else
        print_error ".env.example not found. Creating default .env..."
        cat > .env << EOF
# YoloHome Environment Configuration
# Please update these values with your actual credentials

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=yolohome_super_secret_key_change_in_production

# Database Configuration
DB_NAME=yolohome
DB_USER=yolohome
DB_PASSWORD=yolohome_secret_2024
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=jwt_super_secret_key_change_in_production
JWT_ACCESS_TOKEN_EXPIRES=86400

# Adafruit IO Configuration (Required)
ADAFRUIT_IO_USERNAME=quanghung2405
ADAFRUIT_IO_KEY=aio_xWRU45vsUZKmCwgIJaTGqnnHgrmQ

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@yolohome.com
EOF
        print_success "Default .env created. Please update with your credentials."
    fi
fi

# Load environment variables
export $(grep -v '^#' .env | xargs 2>/dev/null || true)

# Check required environment variables
print_info "Checking required environment variables..."
REQUIRED_VARS=("ADAFRUIT_IO_USERNAME" "ADAFRUIT_IO_KEY")
MISSING_VARS=0

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [[ "${!var}" == "your_"* ]]; then
        print_error "$var is not set or has placeholder value"
        MISSING_VARS=1
    else
        print_success "$var is set"
    fi
done

if [ $MISSING_VARS -eq 1 ]; then
    print_error "Please update .env file with your actual Adafruit IO credentials."
    echo "  1. Go to https://io.adafruit.com/"
    echo "  2. Create an account or login"
    echo "  3. Go to 'My Key' to get your username and AIO key"
    echo "  4. Update ADAFRUIT_IO_USERNAME and ADAFRUIT_IO_KEY in .env"
    exit 1
fi

# Check if Docker is installed
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "  Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is available
print_info "Checking Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    print_success "Docker Compose (V2) is available"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    print_success "Docker Compose (V1) is available"
else
    print_error "Docker Compose is not installed."
    exit 1
fi

# Stop existing containers if running
print_info "Stopping existing containers (if any)..."
$COMPOSE_CMD down --remove-orphans 2>/dev/null || true

# Build and start containers
print_info "Building Docker images..."
$COMPOSE_CMD build

print_info "Starting services..."
$COMPOSE_CMD up -d

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 5

# Check if database is healthy
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec yolohome-db pg_isready -U yolohome -d yolohome &>/dev/null; then
        print_success "Database is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 1
done
echo ""

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Database failed to start"
    $COMPOSE_CMD logs db
    exit 1
fi

# Run database migrations
print_info "Running database migrations..."
$COMPOSE_CMD exec api flask db upgrade 2>/dev/null || {
    print_info "Initializing database..."
    $COMPOSE_CMD exec api flask db init 2>/dev/null || true
    $COMPOSE_CMD exec api flask db migrate -m "Initial migration" 2>/dev/null || true
    $COMPOSE_CMD exec api flask db upgrade 2>/dev/null || true
}

# Initialize default devices
print_info "Initializing default devices..."
$COMPOSE_CMD exec api python scripts/init_devices.py 2>/dev/null || true

print_success "YoloHome backend is running!"
echo ""
echo "=========================================="
echo "  Service URLs                           "
echo "=========================================="
echo "  API:           http://localhost:5000"
echo "  API Docs:      http://localhost:5000/api/docs"
echo "  Health Check:  http://localhost:5000/api/health"
echo ""
echo "=========================================="
echo "  Default Admin Account                  "
echo "=========================================="
echo "  Username: admin@yolohome.com"
echo "  Password: admin123"
echo ""
echo "=========================================="
echo "  Useful Commands                        "
echo "=========================================="
echo "  View logs:     $COMPOSE_CMD logs -f api"
echo "  Stop services: $COMPOSE_CMD down"
echo "  Restart:       $COMPOSE_CMD restart"
echo "  Shell access:  $COMPOSE_CMD exec api bash"
echo "=========================================="