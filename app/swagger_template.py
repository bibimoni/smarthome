"""Swagger/OpenAPI template configuration for YoloHome API."""

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "YoloHome IoT Smart Home API",
        "description": """
## YoloHome Backend API

A production-ready backend for the YoloHome IoT Smart Home system.

### Features
- **Real-time Monitoring** (UC-1): Monitor temperature, humidity, light levels, and motion detection
- **Threshold Configuration** (UC-2): Set automation rules based on sensor values
- **Manual Control** (UC-3): Control fans, LEDs, RGB lights, and LCD displays
- **Activity History** (UC-4): View logs of all device activities and sensor readings
- **Scene Creation** (UC-5): Create automation scenes with multiple conditions and actions

### Authentication
All protected endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

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
        """,
        "version": "1.0.0",
        "contact": {
            "name": "YoloHome Team",
            "email": "support@yolohome.com"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "security": [
        {"Bearer": []}
    ],
    "host": "localhost:5001",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "produces": ["application/json"],
    "consumes": ["application/json"],
    "tags": [
        {
            "name": "Authentication",
            "description": "User registration, login, and password management"
        },
        {
            "name": "Sensors",
            "description": "Real-time environment monitoring (UC-1)"
        },
        {
            "name": "Actuators",
            "description": "Device control operations (UC-3)"
        },
        {
            "name": "Thresholds",
            "description": "Automation rules configuration (UC-2)"
        },
        {
            "name": "Scenes",
            "description": "Scene management for automation (UC-5)"
        },
        {
            "name": "Logs",
            "description": "Activity history and event logs (UC-4)"
        },
        {
            "name": "Health",
            "description": "System health checks"
        }
    ],
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "email": {"type": "string", "example": "user@example.com"},
                "first_name": {"type": "string", "example": "John"},
                "last_name": {"type": "string", "example": "Doe"},
                "is_active": {"type": "boolean", "example": True},
                "is_verified": {"type": "boolean", "example": True},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "Sensor": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Living Room Temperature"},
                "type": {"type": "string", "enum": ["temperature", "humidity", "light", "pir"]},
                "unit": {"type": "string", "example": "°C"},
                "location": {"type": "string", "example": "Living Room"},
                "is_active": {"type": "boolean"},
                "min_value": {"type": "number", "example": 0},
                "max_value": {"type": "number", "example": 100}
            }
        },
        "Actuator": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Bedroom Fan"},
                "type": {"type": "string", "enum": ["fan", "led", "rgb", "lcd"]},
                "location": {"type": "string", "example": "Bedroom"},
                "is_active": {"type": "boolean"},
                "current_state": {"type": "string", "example": "on"},
                "current_value": {"type": "string", "example": "75"},
                "mode": {"type": "string", "enum": ["auto", "manual"]}
            }
        },
        "ThresholdRule": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "sensor_id": {"type": "integer"},
                "operator": {"type": "string", "enum": ["greater_than", "less_than", "equals"]},
                "threshold_value": {"type": "number"},
                "actuator_id": {"type": "integer"},
                "action_value": {"type": "string"},
                "is_active": {"type": "boolean"},
                "description": {"type": "string"}
            }
        },
        "Scene": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "example": "Good Night"},
                "description": {"type": "string"},
                "is_active": {"type": "boolean"},
                "conditions": {"type": "array", "items": {"$ref": "#/definitions/SceneCondition"}},
                "actions": {"type": "array", "items": {"$ref": "#/definitions/SceneAction"}}
            }
        },
        "SceneCondition": {
            "type": "object",
            "properties": {
                "sensor_id": {"type": "integer"},
                "condition": {"type": "string"},
                "value": {"type": "number"}
            }
        },
        "SceneAction": {
            "type": "object",
            "properties": {
                "actuator_id": {"type": "integer"},
                "action": {"type": "string"},
                "value": {"type": "string"}
            }
        },
        "SensorData": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "sensor_id": {"type": "integer"},
                "value": {"type": "number"},
                "recorded_at": {"type": "string", "format": "date-time"}
            }
        },
        "EventLog": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "event_type": {"type": "string"},
                "description": {"type": "string"},
                "actuator_id": {"type": "integer"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"}
            }
        },
        "LoginResponse": {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "refresh_token": {"type": "string"},
                "user": {"$ref": "#/definitions/User"}
            }
        }
    }
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
}