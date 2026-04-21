# Database diagram.

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        timestamp created_at
    }

    SESSIONS {
        int id PK
        int user_id FK
        string session_token UK
        timestamp expires_at
    }

    SENSORS {
        int id PK
        string name
        string type "temperature, humidity, light, pir"
        string feed_key "Adafruit feed"
    }

    ACTUATORS {
        int id PK
        string name
        string type "fan, led, servo, etc."
        string feed_key "Adafruit feed"
        string current_value
        string mode "AUTO or MANUAL"
    }

    SENSOR_DATA {
        int id PK
        int sensor_id FK
        float value
        timestamp recorded_at
    }

    EVENT_LOGS {
        int id PK
        string event_type "ALERT, AUTO, MANUAL, ERROR"
        int actuator_id FK "nullable"
        int user_id FK "nullable"
        string description
        timestamp created_at
    }

    THRESHOLD_RULES {
        int id PK
        int sensor_id FK
        string operator "\>, <, =="
        float threshold_value
        int actuator_id FK
        string action_value "ON, OFF, etc."
        boolean is_active
    }

    SCENES {
        int id PK
        int user_id FK
        string name
        boolean is_active
    }

    SCENE_CONDITIONS {
        int id PK
        int scene_id FK
        int sensor_id FK
        string operator ">, <, =="
        float threshold_value
    }

    SCENE_ACTIONS {
        int id PK
        int scene_id FK
        int actuator_id FK
        string action_value "ON, OFF, etc."
    }

    %% Relationships
    USERS ||--o{ SESSIONS : "has"
    USERS ||--o{ EVENT_LOGS : "triggers (manual)"
    USERS ||--o{ SCENES : "creates"

    SENSORS ||--o{ SENSOR_DATA : "records"
    SENSORS ||--o{ THRESHOLD_RULES : "monitored by"
    SENSORS ||--o{ SCENE_CONDITIONS : "checked in"

    ACTUATORS ||--o{ EVENT_LOGS : "involved in"
    ACTUATORS ||--o{ THRESHOLD_RULES : "controlled by"
    ACTUATORS ||--o{ SCENE_ACTIONS : "affected by"

    SCENES ||--|{ SCENE_CONDITIONS : "requires"
    SCENES ||--|{ SCENE_ACTIONS : "executes"
```

### 1. Identity
*Handles User Registration and Login.*

**`Users`**
* `id` (Primary Key)
* `email` (String, Unique) - For login and password recovery.
* `password_hash` (String)
* `full_name` (String)

---

### 2. Hardware Management
*Separates input devices from output devices for easier automation logic.*

**`Sensors`** (Inputs)
* `id` (Primary Key)
* `name` (String) - *e.g., "Nhiệt độ phòng khách"*
* `adafruit_feed` (String) - *The exact topic name to subscribe to on Adafruit IO.*

**`Actuators`** (Outputs)
* `id` (Primary Key)
* `name` (String) - *e.g., "Quạt máy"*
* `adafruit_feed` (String)
* `status` (String) - *e.g., "ON", "OFF", "90"*
* `is_auto_mode` (Boolean) - *If `true`, the system follows threshold rules. If `false`, the user has manually overridden it.*

---

### 3. Data & Logging
*Handles real-time metric storage and the system's activity history.*

**`Sensor_Data`** (For drawing charts)
* `id` (Primary Key)
* `sensor_id` (Foreign Key -> Sensors.id)
* `value` (Float) - *The reading from Adafruit.*
* `created_at` (Timestamp)

**`Activity_Logs`** (The system's audit trail)
* `id` (Primary Key)
* `device_name` (String) - *Stored as text so the log remains even if a device is deleted later.*
* `event_type` (String) - *"AUTO", "MANUAL", "ALERT", or "ERROR".*
* `description` (String) - *e.g., "User turned Fan ON" or "Temp > 30°C: Fan auto-started".*
* `created_at` (Timestamp)

---

### 4. Automation Engine
*Handles the environmental threshold configurations.*

**`Rules`** (The "If this, then that" logic)
* `id` (Primary Key)
* `sensor_id` (Foreign Key -> Sensors.id)
* `condition` (String) - *">", "<", or "==".*
* `threshold_value` (Float) - *e.g., 30.5*
* `actuator_id` (Foreign Key -> Actuators.id)
* `action_command` (String) - *What to send to Adafruit (e.g., "ON").*
* `is_active` (Boolean) - *Allows the user to temporarily pause a specific rule.*