# YoloHome API Documentation

Complete API reference for the YoloHome IoT Smart Home Backend.

## Table of Contents

1. [Authentication](#authentication)
2. [Sensors](#sensors)
3. [Actuators](#actuators)
4. [Thresholds](#thresholds)
5. [Scenes](#scenes)
6. [Activity Logs](#activity-logs)
7. [IoT Gateway](#iot-gateway)
8. [Health](#health)

---

## Authentication

### Register User

**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `409 Conflict` - Email already exists

---

### Login

**POST** `/api/auth/login`

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

### Google OAuth Login

**POST** `/api/auth/google`

Authenticate using Google OAuth token.

**Request Body:**
```json
{
  "id_token": "google_oauth_id_token"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@gmail.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

---

### Forgot Password

**POST** `/api/auth/forgot-password`

Request a password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

---

### Reset Password

**POST** `/api/auth/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful"
}
```

---

### Refresh Token

**POST** `/api/auth/refresh`

Get a new access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Get Current User

**GET** `/api/auth/me`

Get the authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Sensors

### List All Sensors

**GET** `/api/sensors`

Get all sensors for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sensors": [
    {
      "id": 1,
      "name": "Temperature Sensor",
      "sensor_type": "temperature",
      "unit": "°C",
      "location": "Living Room",
      "is_active": true,
      "last_value": 27.5,
      "last_reading": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Get Sensor by ID

**GET** `/api/sensors/{sensor_id}`

Get detailed information about a specific sensor.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Temperature Sensor",
  "sensor_type": "temperature",
  "unit": "°C",
  "location": "Living Room",
  "is_active": true,
  "min_threshold": 18.0,
  "max_threshold": 35.0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Sensor Data

**GET** `/api/sensors/{sensor_id}/data`

Get historical sensor readings.

**Query Parameters:**
- `hours` (int, optional): Hours of data to retrieve (default: 24)
- `limit` (int, optional): Maximum number of records (default: 100)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sensor_id": 1,
  "data": [
    {
      "id": 1,
      "value": 27.5,
      "recorded_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "value": 27.8,
      "recorded_at": "2024-01-15T10:25:00Z"
    }
  ],
  "count": 2
}
```

---

### Get Latest Reading

**GET** `/api/sensors/{sensor_id}/latest`

Get the most recent sensor reading.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sensor_id": 1,
  "value": 27.5,
  "unit": "°C",
  "recorded_at": "2024-01-15T10:30:00Z"
}
```

---

### Get Sensor Statistics

**GET** `/api/sensors/{sensor_id}/stats`

Get statistical analysis of sensor data.

**Query Parameters:**
- `period` (str, optional): `hour`, `day`, `week`, `month` (default: day)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sensor_id": 1,
  "period": "day",
  "statistics": {
    "min": 22.5,
    "max": 29.8,
    "avg": 26.2,
    "count": 288
  },
  "trend": "increasing"
}
```

---

## Actuators

### List All Actuators

**GET** `/api/actuators`

Get all actuators for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "actuators": [
    {
      "id": 1,
      "name": "Living Room Fan",
      "actuator_type": "fan",
      "location": "Living Room",
      "is_active": true,
      "mode": "auto",
      "current_state": "on",
      "current_value": 75
    }
  ]
}
```

---

### Get Actuator by ID

**GET** `/api/actuators/{actuator_id}`

Get detailed information about a specific actuator.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Living Room Fan",
  "actuator_type": "fan",
  "location": "Living Room",
  "is_active": true,
  "mode": "auto",
  "current_state": "on",
  "current_value": 75,
  "min_value": 0,
  "max_value": 100,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Control Actuator

**POST** `/api/actuators/{actuator_id}/control`

Control an actuator (turn on/off, set value).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "action": "on",
  "value": 75,
  "mode": "manual"
}
```

**Action Values:**
- `on` - Turn on the device
- `off` - Turn off the device
- `toggle` - Toggle current state
- Numeric value (0-100) - For fan speed or brightness

**Response (200 OK):**
```json
{
  "message": "Actuator controlled successfully",
  "actuator": {
    "id": 1,
    "current_state": "on",
    "current_value": 75,
    "mode": "manual"
  }
}
```

---

### Set Auto Mode

**POST** `/api/actuators/{actuator_id}/auto`

Set actuator to automatic mode (controlled by thresholds).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Actuator set to auto mode",
  "actuator": {
    "id": 1,
    "mode": "auto"
  }
}
```

---

## Thresholds

### List All Threshold Rules

**GET** `/api/thresholds`

Get all threshold rules.

**Query Parameters:**
- `is_active` (bool, optional): Filter by active status

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "rules": [
    {
      "id": 1,
      "name": "Auto Fan on High Temp",
      "description": "Turn on fan when temperature exceeds 30°C",
      "sensor_id": 1,
      "sensor_name": "Temperature Sensor",
      "condition": "greater_than",
      "threshold_value": 30.0,
      "actuator_id": 1,
      "actuator_name": "Living Room Fan",
      "action": "on",
      "is_active": true,
      "last_triggered": "2024-01-15T09:30:00Z"
    }
  ]
}
```

---

### Create Threshold Rule

**POST** `/api/thresholds`

Create a new threshold rule.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Auto Fan on High Temp",
  "description": "Turn on fan when temperature exceeds 30°C",
  "sensor_id": 1,
  "condition": "greater_than",
  "threshold_value": 30.0,
  "actuator_id": 1,
  "action": "on",
  "is_active": true
}
```

**Condition Values:**
- `greater_than` - Value > threshold
- `less_than` - Value < threshold
- `equals` - Value == threshold
- `not_equals` - Value != threshold
- `between` - Value in range (requires `value2`)

**Response (201 Created):**
```json
{
  "message": "Threshold rule created successfully",
  "rule": {
    "id": 1,
    "name": "Auto Fan on High Temp",
    "is_active": true
  }
}
```

---

### Update Threshold Rule

**PUT** `/api/thresholds/{rule_id}`

Update an existing threshold rule.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "threshold_value": 28.0,
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "message": "Threshold rule updated successfully",
  "rule": {
    "id": 1,
    "threshold_value": 28.0
  }
}
```

---

### Delete Threshold Rule

**DELETE** `/api/thresholds/{rule_id}`

Delete a threshold rule.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Threshold rule deleted successfully"
}
```

---

## Scenes

### List All Scenes

**GET** `/api/scenes`

Get all scenes for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "scenes": [
    {
      "id": 1,
      "name": "Morning Routine",
      "description": "Turn on lights when motion detected in morning",
      "is_active": true,
      "trigger_count": 15,
      "last_triggered": "2024-01-15T07:30:00Z"
    }
  ]
}
```

---

### Get Scene Details

**GET** `/api/scenes/{scene_id}`

Get detailed scene information including conditions and actions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Morning Routine",
  "description": "Turn on lights when motion detected in morning",
  "is_active": true,
  "conditions": [
    {
      "id": 1,
      "type": "motion",
      "sensor_id": 4,
      "operator": "equals",
      "value": "1"
    },
    {
      "id": 2,
      "type": "time",
      "operator": "between",
      "value": "06:00",
      "value2": "09:00"
    }
  ],
  "actions": [
    {
      "id": 1,
      "actuator_id": 2,
      "action": "on"
    },
    {
      "id": 2,
      "actuator_id": 3,
      "action": "on",
      "value": "#FFA500"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Create Scene

**POST** `/api/scenes`

Create a new scene with conditions and actions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
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
    {
      "actuator_id": 2,
      "action": "on"
    },
    {
      "actuator_id": 3,
      "action": "on",
      "value": "#FFA500"
    }
  ]
}
```

**Condition Types:**
- `sensor` - Based on sensor reading
- `motion` - Motion detection
- `time` - Time-based trigger
- `schedule` - Scheduled execution

**Response (201 Created):**
```json
{
  "message": "Scene created successfully",
  "scene": {
    "id": 1,
    "name": "Morning Routine",
    "is_active": true
  }
}
```

---

### Update Scene

**PUT** `/api/scenes/{scene_id}`

Update an existing scene.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Morning Routine",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "message": "Scene updated successfully",
  "scene": {
    "id": 1,
    "name": "Updated Morning Routine"
  }
}
```

---

### Delete Scene

**DELETE** `/api/scenes/{scene_id}`

Delete a scene.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Scene deleted successfully"
}
```

---

### Execute Scene

**POST** `/api/scenes/{scene_id}/execute`

Manually execute a scene's actions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Scene executed successfully",
  "actions_executed": 2
}
```

---

## Activity Logs

### Get Event Logs

**GET** `/api/logs`

Get paginated event logs.

**Query Parameters:**
- `event_type` (str, optional): Filter by type (`sensor`, `actuator`, `system`, `automation`)
- `start_date` (str, optional): Start date (ISO format)
- `end_date` (str, optional): End date (ISO format)
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "logs": [
    {
      "id": 1,
      "event_type": "sensor",
      "event_source": "Temperature Sensor",
      "event_description": "Temperature reading: 27.5°C",
      "old_value": null,
      "new_value": "27.5",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "event_type": "actuator",
      "event_source": "Living Room Fan",
      "event_description": "Fan turned on at 75%",
      "old_value": "off",
      "new_value": "75",
      "created_at": "2024-01-15T10:25:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

---

### Get Sensor History

**GET** `/api/logs/sensor/{sensor_id}`

Get historical data for a specific sensor.

**Query Parameters:**
- `hours` (int, optional): Hours of data (default: 24)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sensor_id": 1,
  "sensor_name": "Temperature Sensor",
  "data": [
    {
      "value": 27.5,
      "recorded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## IoT Gateway

### Receive Sensor Data

**POST** `/api/iot/sensor-data`

Endpoint for YoloBit devices to send sensor data.

**Request Body:**
```json
{
  "device_id": "yolobit_001",
  "sensor_type": "temperature",
  "value": 27.5,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "message": "Sensor data received",
  "data_id": 123
}
```

---

### Get Commands

**GET** `/api/iot/commands/{device_id}`

Get pending commands for a YoloBit device.

**Response (200 OK):**
```json
{
  "device_id": "yolobit_001",
  "commands": [
    {
      "actuator_type": "fan",
      "action": "on",
      "value": 75
    },
    {
      "actuator_type": "led",
      "action": "on"
    }
  ]
}
```

---

### Register Device

**POST** `/api/iot/register`

Register a new YoloBit device.

**Request Body:**
```json
{
  "device_id": "yolobit_001",
  "device_name": "Living Room YoloBit",
  "sensors": ["temperature", "humidity", "light", "pir"],
  "actuators": ["fan", "led", "rgb", "lcd"]
}
```

**Response (201 Created):**
```json
{
  "message": "Device registered successfully",
  "device": {
    "device_id": "yolobit_001",
    "sensors": [1, 2, 3, 4],
    "actuators": [1, 2, 3, 4]
  }
}
```

---

## Health

### Health Check

**GET** `/api/health`

Check the health status of the API and its services.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "mqtt": "healthy"
  },
  "version": "1.0.0",
  "environment": "production"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "services": {
    "database": "healthy",
    "mqtt": "unhealthy: Connection refused"
  }
}
```

---

### Readiness Check

**GET** `/api/ready`

Check if the service is ready to accept traffic.

**Response (200 OK):**
```json
{
  "status": "ready"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "not ready",
  "error": "Database connection failed"
}
```

---

## Error Responses

All endpoints follow a consistent error format:

```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated endpoints

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705315800