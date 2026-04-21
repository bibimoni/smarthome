# YoloHome - IoT Smart Home Backend

A production-ready backend for the YoloHome IoT Smart Home system, built with Flask and designed for university class projects.

## 🏠 Overview

YoloHome is a smart home automation system that integrates with YoloBit microcontrollers and Adafruit IO for real-time monitoring and control of home devices.

### Features

- **Real-time Monitoring** (UC-1): Monitor temperature, humidity, light levels, and motion detection
- **Threshold Configuration** (UC-2): Set automation rules based on sensor values
- **Manual Control** (UC-3): Control fans, LEDs, RGB lights, and LCD displays
- **Activity History** (UC-4): View logs of all device activities and sensor readings
- **Scene Creation** (UC-5): Create automation scenes with multiple conditions and actions
- **User Authentication**: Register, login, and password reset functionality

### Supported Devices (YoloBit)

| Type | Device | Function |
|------|--------|----------|
| Sensor | DHT20 | Temperature & Humidity |
| Sensor | Light Sensor | Ambient light level |
| Sensor | PIR | Motion detection |
| Actuator | Fan | Speed control (0-100%) |
| Actuator | LED | On/Off control |
| Actuator | RGB LED | Color control (R, G, B) |
| Actuator | LCD1602 | Text display |

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Adafruit IO account (free at [io.adafruit.com](https://io.adafruit.com))

### Development Setup (Recommended)

The development setup uses Docker with PostgreSQL and includes hot-reload for code changes.

```bash
chmod +x dev-docker.sh
./dev-docker.sh
```

This will:
1. Build Docker images (PostgreSQL + Flask app)
2. Start containers in the background
3. Wait for PostgreSQL to be ready
4. Run database migrations
5. Run the interactive device setup script to create your account and devices

**Development URLs:**
- API: http://localhost:5001
- Database: localhost:5432 (yolohome_dev)

**Useful commands:**
```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f api

# Stop environment
docker-compose -f docker-compose.dev.yml down

# Restart API
docker-compose -f docker-compose.dev.yml restart api

# Access container shell
docker-compose -f docker-compose.dev.yml exec api bash
```

### Production Setup

```bash
chmod +x start.sh
./start.sh
```

The script will:
1. Create `.env` file from template
2. Build and start Docker containers
3. Initialize the database
4. Create default devices and threshold rules

### Manual Setup

1. **Clone and configure**
   ```bash
   cp .env.example .env
   # Edit .env with your Adafruit IO credentials
   ```

2. **Start with Docker Compose**
   ```bash
   docker compose up -d
   ```

3. **Initialize database**
   ```bash
   docker compose exec api flask db upgrade
   docker compose exec api python scripts/init_devices.py
   ```

## 📁 Project Structure

```
yolohome/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── main.py              # Entry point
│   ├── api/                 # REST API endpoints
│   │   ├── auth.py          # Authentication (UC-R, UC-L, UC-FP)
│   │   ├── sensors.py       # Sensor monitoring (UC-1)
│   │   ├── actuators.py     # Device control (UC-3)
│   │   ├── thresholds.py    # Threshold rules (UC-2)
│   │   ├── scenes.py        # Scene management (UC-5)
│   │   ├── logs.py          # Activity history (UC-4)
│   │   ├── iot.py           # IoT gateway
│   │   └── health.py        # Health checks
│   ├── models/              # Database models
│   │   ├── user.py          # User, Session models
│   │   ├── device.py        # Sensor, Actuator models
│   │   ├── data.py          # SensorData, EventLog models
│   │   └── automation.py    # Threshold, Scene models
│   └── services/            # Business logic layer
│       ├── auth_service.py
│       ├── mqtt_service.py
│       ├── device_service.py
│       ├── sensor_service.py
│       ├── actuator_service.py
│       ├── scene_service.py
│       ├── threshold_service.py
│       └── email_service.py
├── scripts/
│   └── init_devices.py      # Device initialization
├── Dockerfile
├── docker-compose.yml
├── start.sh                 # One-click startup
├── requirements.txt
└── README.md
```

## 🔌 API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication

All protected endpoints require JWT token:
```
Authorization: Bearer <access_token>
```

---

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "<reset_token>",
  "new_password": "newpassword123"
}
```

---

### Sensor Endpoints (UC-1: Real-time Monitoring)

#### Get All Sensors
```http
GET /api/sensors
Authorization: Bearer <token>
```

#### Get Sensor Data
```http
GET /api/sensors/{sensor_id}/data?hours=24
Authorization: Bearer <token>
```

#### Get Latest Reading
```http
GET /api/sensors/{sensor_id}/latest
Authorization: Bearer <token>
```

#### Get Statistics
```http
GET /api/sensors/{sensor_id}/stats?period=day
Authorization: Bearer <token>
```

---

### Actuator Endpoints (UC-3: Manual Control)

#### Get All Actuators
```http
GET /api/actuators
Authorization: Bearer <token>
```

#### Control Actuator
```http
POST /api/actuators/{actuator_id}/control
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "on",          // "on", "off", or value (0-100 for fan)
  "value": 75,             // Optional: for fan speed or RGB values
  "mode": "manual"         // "auto" or "manual"
}
```

#### Set Auto Mode
```http
POST /api/actuators/{actuator_id}/auto
Authorization: Bearer <token>
```

---

### Threshold Endpoints (UC-2: Threshold Configuration)

#### Get All Rules
```http
GET /api/thresholds
Authorization: Bearer <token>
```

#### Create Rule
```http
POST /api/thresholds
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Auto Fan on High Temp",
  "sensor_id": 1,
  "condition": "greater_than",
  "threshold_value": 30.0,
  "actuator_id": 1,
  "action": "on",
  "is_active": true
}
```

#### Update Rule
```http
PUT /api/thresholds/{rule_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "threshold_value": 28.0,
  "is_active": true
}
```

#### Delete Rule
```http
DELETE /api/thresholds/{rule_id}
Authorization: Bearer <token>
```

---

### Scene Endpoints (UC-5: Scene Creation)

#### Get All Scenes
```http
GET /api/scenes
Authorization: Bearer <token>
```

#### Create Scene
```http
POST /api/scenes
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Morning Routine",
  "description": "Turn on lights when motion detected in morning",
  "conditions": [
    {
      "type": "motion",
      "sensor_id": 4,
      "operator": "equals",
      "value": "1"
    },
    {
      "type": "time",
      "operator": "between",
      "value": "06:00",
      "value2": "09:00"
    }
  ],
  "actions": [
    {"actuator_id": 2, "action": "on"},
    {"actuator_id": 3, "action": "on", "value": "#FFA500"}
  ]
}
```

#### Execute Scene
```http
POST /api/scenes/{scene_id}/execute
Authorization: Bearer <token>
```

---

### Log Endpoints (UC-4: Activity History)

#### Get Event Logs
```http
GET /api/logs?event_type=sensor&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

#### Get Sensor History
```http
GET /api/logs/sensor/{sensor_id}?hours=48
Authorization: Bearer <token>
```

---

### IoT Gateway Endpoints

#### Receive Sensor Data (YoloBit)
```http
POST /api/iot/sensor-data
Content-Type: application/json

{
  "device_id": "yolobit_001",
  "sensor_type": "temperature",
  "value": 27.5,
  "unit": "°C"
}
```

#### Get Commands (YoloBit)
```http
GET /api/iot/commands/{device_id}
```

---

### Health Check
```http
GET /api/health
```

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| users | User accounts |
| sessions | Active user sessions |
| sensors | Sensor devices |
| actuators | Actuator devices |
| sensor_data | Sensor readings |
| event_logs | Activity history |
| threshold_rules | Automation rules |
| scenes | Scene definitions |
| scene_conditions | Scene trigger conditions |
| scene_actions | Scene actions |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Flask secret key | Yes |
| JWT_SECRET_KEY | JWT signing key | Yes |
| DATABASE_URL | PostgreSQL connection URL | Auto (Docker) |
| ADAFRUIT_IO_USERNAME | Adafruit IO username | Yes |
| ADAFRUIT_IO_KEY | Adafruit IO AIO key | Yes |
| SMTP_SERVER | Email SMTP server | Optional |
| SMTP_USERNAME | Email username | Optional |
| SMTP_PASSWORD | Email password | Optional |

## 🔌 Adafruit IO Integration

The system uses Adafruit IO as a cloud MQTT broker for communication between YoloBit devices and the backend.

### Architecture Overview

```
┌─────────────┐    MQTT Publish    ┌──────────────┐    Subscribe    ┌─────────────┐
│   YoloBit   │ ─────────────────► │ Adafruit IO  │ ◄─────────────► │  YoloHome   │
│  (Devices)  │                    │   Broker     │                 │  Backend    │
└─────────────┘                    └──────────────┘                 └─────────────┘
      │                                                                   │
      │                         ┌─────────────────────────────────────────┤
      │                         │                                         │
      │                    MQTT Subscribe                           PostgreSQL
      │                   (for actuator cmds)                        Database
      │                                                                   │
      └───────────────────────────────────────────────────────────────────┘
```

### Feed Structure

A "feed" is a MQTT topic that stores sensor data or sends commands:

```
{username}/feeds/{device_type}.{device_name}.{location}

Examples:
├── quanghung2405/feeds/temperature.living-room    # Temperature sensor
├── quanghung2405/feeds/humidity.living-room       # Humidity sensor
├── quanghung2405/feeds/light.living-room          # Light level sensor
├── quanghung2405/feeds/pir.entrance               # Motion sensor
├── quanghung2405/feeds/fan.living-room            # Fan control
├── quanghung2405/feeds/led.bedroom                # LED control
├── quanghung2405/feeds/rgb.living-room            # RGB LED control
└── quanghung2405/feeds/lcd.living-room            # LCD display
```

---

## 📱 Complete Device Setup Guide

### Prerequisites Checklist

Before using the system, you need:

1. ✅ **Adafruit IO Account** (free at [io.adafruit.com](https://io.adafruit.com))
2. ✅ **Physical YoloBit Device** with sensors and actuators
3. ✅ **WiFi Network** for YoloBit to connect
4. ✅ **YoloHome Backend** running (see Quick Start above)

---

### Step 1: Create Adafruit IO Account

1. Go to **https://io.adafruit.com**
2. Create a free account
3. Note your credentials:
   - **Username**: e.g., `quanghung2405`
   - **AIO Key**: Found at `My Profile` → `AIO Keys` → `View AIO Keys`

### Step 2: Create Feeds on Adafruit IO

A "feed" is a MQTT topic for data storage and messaging.

**Via Web Interface:**
1. Go to **My Feeds** → **New Feed**
2. Create feeds for each sensor and actuator:

| Feed Name | Description | Direction |
|-----------|-------------|-----------|
| `temperature.living-room` | Temperature readings | YoloBit → Backend |
| `humidity.living-room` | Humidity readings | YoloBit → Backend |
| `light.living-room` | Light level readings | YoloBit → Backend |
| `fan.living-room` | Fan control commands | Backend → YoloBit |
| `led.bedroom` | LED control commands | Backend → YoloBit |

### Step 3: Configure Backend Environment

Update `.env` with your Adafruit IO credentials:

```env
ADAFRUIT_IO_USERNAME=your_username
ADAFRUIT_IO_KEY=your_aio_key
```

### Step 4: Prepare YoloBit Firmware

Create/update the firmware file (based on `ohstem.py`):

```python
# firmware.py - Upload to YoloBit
import network
import umqtt.simple as mqtt
import time
from homebit3_dht20 import DHT20
from yolobit import *

# ===== WIFI SETUP =====
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD")

while not wifi.isconnected():
    pass

print("WiFi connected!")

# ===== ADAFRUIT IO CONFIG =====
ADAFRUIT_USER = "your_username"      # Your Adafruit username
ADAFRUIT_KEY = "your_aio_key"        # Your AIO key

# ===== MQTT CLIENT =====
client = mqtt.MQTTClient('yolobit', 'io.adafruit.com', 1883,
                          ADAFRUIT_USER, ADAFRUIT_KEY)

# ===== SENSORS =====
dht20 = DHT20()

# ===== ACTUATOR CALLBACKS =====
def on_message(topic, msg):
    """Called when command received from backend"""
    topic_str = topic.decode()
    value = msg.decode()

    if 'fan' in topic_str:
        pin1.write_digital(1 if value == 'ON' else 0)
    elif 'led' in topic_str:
        pin2.write_digital(1 if value == 'ON' else 0)
    elif 'rgb' in topic_str:
        # Parse RGB value (e.g., "255,0,0" for red)
        r, g, b = map(int, value.split(','))
        # Set RGB LED...

client.set_callback(on_message)
client.connect()

# ===== SUBSCRIBE TO ACTUATOR FEEDS =====
client.subscribe(f"{ADAFRUIT_USER}/feeds/fan.living-room")
client.subscribe(f"{ADAFRUIT_USER}/feeds/led.bedroom")

# ===== MAIN LOOP =====
last_send = 0

while True:
    # Check for commands (non-blocking)
    client.check_msg()

    # Send sensor data every 5 seconds
    if time.time() - last_send >= 5:
        last_send = time.time()

        # Read sensors
        dht20.read_dht20()
        temp = dht20.dht20_temperature()
        humi = dht20.dht20_humidity()
        light = pin0.read_analog()

        # Publish to Adafruit IO
        client.publish(f"{ADAFRUIT_USER}/feeds/temperature.living-room", str(temp))
        client.publish(f"{ADAFRUIT_USER}/feeds/humidity.living-room", str(humi))
        client.publish(f"{ADAFRUIT_USER}/feeds/light.living-room", str(light))

    time.sleep(0.1)
```

### Step 5: Flash Firmware to YoloBit

1. Connect YoloBit to computer via USB
2. Use a tool like `ampy` or Thonny IDE
3. Upload the firmware file
4. Reset the YoloBit

### Step 6: Register Devices in Backend

Use the API or the setup script to register devices:

**Via API:**
```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@yolohome.com","password":"dev1234"}' | jq -r '.access_token')

# Register sensor
curl -X POST http://localhost:5001/api/sensors/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room Temperature",
    "type": "temperature",
    "unit": "°C",
    "location": "Living Room",
    "feed_key": "your_username/feeds/temperature.living-room"
  }'

# Register actuator
curl -X POST http://localhost:5001/api/actuators/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room Fan",
    "type": "fan",
    "location": "Living Room",
    "feed_key": "your_username/feeds/fan.living-room"
  }'
```

**Via Script:**
```bash
docker-compose -f docker-compose.dev.yml exec api python scripts/init_devices.py
```

---

### How Data Flows

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  SENSOR DATA (YoloBit → Backend):                                        │
│  ┌─────────┐    read     ┌─────────┐   publish   ┌─────────┐   store    │
│  │ Sensor  │ ──────────► │ YoloBit │ ──────────► │ Adafruit│ ─────────► │
│  │ (DHT20) │             │         │             │   IO    │            │
│  └─────────┘             └─────────┘             └─────────┘            │
│                                                            │              │
│                                        subscribe           ▼              │
│  ┌─────────┐   check     ┌─────────┐   ◄─────────   ┌─────────┐         │
│  │Threshold│ ◄────────── │ Backend │                │PostgreSQL│        │
│  │  Rules  │   trigger   │   API   │                │ Database │        │
│  └─────────┘             └─────────┘                └─────────┘         │
│       │                                                                      │
│       │ if temp > 30°C                                                       │
│       ▼                                                                      │
│  ┌─────────┐   publish  ┌─────────┐   relay    ┌─────────┐               │
│  │ Backend │ ──────────►│ Adafruit│ ──────────►│ YoloBit │               │
│  │   API   │   "ON"     │   IO    │            │         │               │
│  └─────────┘             └─────────┘            └─────────┘               │
│                                                          │                  │
│                              subscribe                   ▼                  │
│                                                     ┌─────────┐            │
│                                                     │   Fan   │            │
│                                                     │  ON/OFF │            │
│                                                     └─────────┘            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### What Must Match

For data to flow correctly, these **must be identical**:

| Component | Value Example |
|-----------|---------------|
| Adafruit IO Feed Name | `temperature.living-room` |
| YoloBit Publish Topic | `{user}/feeds/temperature.living-room` |
| Backend `feed_key` | `{user}/feeds/temperature.living-room` |
| Backend MQTT Subscription | `{user}/feeds/temperature.living-room` |

**All four must use the same feed path!**

---

### Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No sensor data in backend | Check YoloBit WiFi + Adafruit credentials |
| Actuators not responding | Verify feed subscriptions match |
| MQTT connection failed | Check Adafruit IO credentials in `.env` |
| Device not found | Register device via API with correct `feed_key` |

---

### YoloBit Setup (Legacy)

For the original polling-based approach, see `ohstem.py` and `iotgateway.py`.

## 🧪 Development

### Run Locally (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export DATABASE_URL=postgresql://localhost/yolohome

# Run migrations
flask db upgrade

# Start server
flask run
```

### Run Tests
```bash
pytest
```

## 📦 Production Deployment

### Docker Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f api

# Stop services
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

### Scaling

For production scaling, consider:
- Use external PostgreSQL instance
- Add Redis for caching
- Use proper reverse proxy (nginx)
- Enable HTTPS

**YoloHome** - Smart Home Automation System 🏠✨
