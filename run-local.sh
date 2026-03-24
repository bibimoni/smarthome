#!/bin/bash

# YoloHome Backend - Local Development Script (No Docker)
# This script sets up and runs the YoloHome IoT backend with SQLite database

set -e

echo "=========================================="
echo "  YoloHome IoT Backend - Local Setup    "
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ====================
# Step 1: Check Python
# ====================
print_step "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    echo "  Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# ====================
# Step 2: Virtual Environment
# ====================
print_step "Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# ====================
# Step 3: Install Dependencies
# ====================
print_step "Step 3: Installing dependencies..."
print_info "Upgrading pip..."
pip install --upgrade pip

print_info "Installing requirements..."
pip install -r requirements-dev.txt

# Install additional packages for local development
pip install flasgger 2>/dev/null || true

print_success "Dependencies installed"

# ====================
# Step 4: Environment Configuration
# ====================
print_step "Step 4: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        # Create a minimal .env for local development
        cat > .env << EOF
# YoloHome Local Development Configuration

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=local_dev_secret_key_not_for_production
FLASK_APP=app.main:create_app()

# Database - SQLite for local development
DATABASE_URL=sqlite:///instance/yolohome.db

# JWT Configuration
JWT_SECRET_KEY=local_jwt_secret_not_for_production
JWT_ACCESS_TOKEN_EXPIRES=86400

# Adafruit IO Configuration
ADAFRUIT_IO_USERNAME=quanghung2405
ADAFRUIT_IO_KEY=aio_anJO06oMkhLtJbAYhp4yRGMmoFoe

# Email (optional - leave empty for local dev)
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF
    fi
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Load environment variables but override DATABASE_URL for SQLite
export $(grep -v '^#' .env | grep -v 'DATABASE_URL' | xargs 2>/dev/null || true)
# Force SQLite for local development (use absolute path)
export DATABASE_URL="sqlite:///$SCRIPT_DIR/instance/yolohome.db"

# ====================
# Step 5: Database Setup
# ====================
print_step "Step 5: Setting up SQLite database..."

# Create instance directory for SQLite
mkdir -p instance

# Set Flask app
export FLASK_APP="app.main:create_app()"
export FLASK_ENV=development

# Check if database exists
DB_PATH="instance/yolohome.db"
if [ ! -f "$DB_PATH" ]; then
    print_info "Creating new SQLite database..."
    
    # Initialize migrations if not exists
    if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
        print_info "Initializing database migrations..."
        flask db init 2>/dev/null || true
        flask db migrate -m "Initial migration" 2>/dev/null || true
    fi
    
    # Apply migrations
    flask db upgrade 2>/dev/null || true
    
    # Create tables directly as fallback
    print_info "Creating database tables..."
    python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')
from app.main import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
PYTHON_SCRIPT
    
    print_success "Database created at $DB_PATH"
else
    print_success "Database already exists at $DB_PATH"
    
    # Run any pending migrations
    print_info "Checking for pending migrations..."
    flask db upgrade 2>/dev/null || true
fi

# ====================
# Step 6: Initialize Default Data
# ====================
print_step "Step 6: Initializing default devices and data..."

# Create a setup script to initialize devices
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')

from app.main import create_app
from app.extensions import db
from app.models.device import Sensor, Actuator
from app.services.device_service import DeviceService

app = create_app()
with app.app_context():
    # Check if devices already exist
    sensor_count = Sensor.query.count()
    actuator_count = Actuator.query.count()
    
    if sensor_count == 0 and actuator_count == 0:
        print("Creating default sensors and actuators...")
        DeviceService.create_default_devices()
        print("✓ Default devices created successfully")
    else:
        print(f"✓ Database already has {sensor_count} sensors and {actuator_count} actuators")
PYTHON_SCRIPT

print_success "Default data initialized"

# ====================
# Step 7: Create Default User (Optional)
# ====================
print_step "Step 7: Checking for default user account..."

python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')

from app.main import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if any user exists
    user = User.query.first()
    
    if not user:
        print("Creating default admin user...")
        user = User(
            email='admin@yolohome.local',
            first_name='Admin',
            last_name='User',
            is_active=True,
            is_verified=True
        )
        user.password_hash = generate_password_hash('admin123')
        db.session.add(user)
        db.session.commit()
        print("✓ Default user created:")
        print("  Email: admin@yolohome.local")
        print("  Password: admin123")
        print("  ⚠️  Please change the password after first login!")
    else:
        print(f"✓ User account exists: {user.email}")
PYTHON_SCRIPT

# ====================
# Step 8: Start Server
# ====================
echo ""
echo "=========================================="
echo "  Starting Development Server            "
echo "=========================================="
echo ""
echo "📋 Server Information:"
echo "   • API URL: http://localhost:5001"
echo "   • Swagger UI: http://localhost:5001/apidocs"
echo "   • Database: SQLite at instance/yolohome.db"
echo ""
echo "🔑 Default Login (if created):"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "📚 Press Ctrl+C to stop the server"
echo ""

# Start Flask development server
# Using port 5001 to avoid macOS AirPlay Receiver conflict on port 5000
flask run --host=0.0.0.0 --port=5001 --debug