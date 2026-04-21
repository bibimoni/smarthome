"""Device service for managing sensors and actuators."""
from typing import List, Optional, Tuple
from datetime import datetime
from app.extensions import db
from app.models.device import (
    Sensor,
    Actuator,
    normalize_actuator_description,
    normalize_actuator_name,
    normalize_sensor_description,
    normalize_sensor_name,
)
from app.models.data import SensorData, EventLog
from app.services.mqtt_service import mqtt_service


class DeviceService:
    """Service class for device management operations."""
    
    # Default sensor configurations for YoloBit
    DEFAULT_SENSORS = [
        {
            'name': 'Nhiệt độ',
            'type': Sensor.TYPE_TEMPERATURE,
            'feed_key': 'temperature',
            'unit': '°C',
            'min_value': -40,
            'max_value': 80,
            'description': 'Cảm biến nhiệt độ DHT20'
        },
        {
            'name': 'Độ ẩm',
            'type': Sensor.TYPE_HUMIDITY,
            'feed_key': 'humidity',
            'unit': '%',
            'min_value': 0,
            'max_value': 100,
            'description': 'Cảm biến độ ẩm DHT20'
        },
        {
            'name': 'Ánh sáng',
            'type': Sensor.TYPE_LIGHT,
            'feed_key': 'light',
            'unit': 'lux',
            'min_value': 0,
            'max_value': 4095,
            'description': 'Cảm biến ánh sáng'
        },
        {
            'name': 'Chuyển động PIR',
            'type': Sensor.TYPE_PIR,
            'feed_key': 'pir',
            'unit': '',
            'min_value': 0,
            'max_value': 1,
            'description': 'Cảm biến chuyển động PIR'
        }
    ]
    
    # Default actuator configurations for YoloBit
    DEFAULT_ACTUATORS = [
        {
            'name': 'Quạt',
            'type': Actuator.TYPE_FAN,
            'feed_key': 'fan',
            'description': 'Thiết bị quạt'
        },
        {
            'name': 'Đèn LED',
            'type': Actuator.TYPE_LED,
            'feed_key': 'led',
            'description': 'Thiết bị đèn LED'
        }
    ]
    
    @staticmethod
    def create_default_devices():
        """Create default sensors and actuators for YoloBit."""
        # Create default sensors
        for sensor_config in DeviceService.DEFAULT_SENSORS:
            existing = Sensor.query.filter_by(feed_key=sensor_config['feed_key']).first()
            if not existing:
                sensor = Sensor(**sensor_config)
                db.session.add(sensor)
        
        # Create default actuators
        for actuator_config in DeviceService.DEFAULT_ACTUATORS:
            existing = Actuator.query.filter_by(feed_key=actuator_config['feed_key']).first()
            if not existing:
                actuator = Actuator(**actuator_config)
                db.session.add(actuator)

        db.session.flush()

        # Chuẩn hóa tên và mô tả để frontend luôn hiển thị tiếng Việt thống nhất
        for sensor in Sensor.query.all():
            sensor.name = normalize_sensor_name(sensor.name, sensor.type, sensor.feed_key)
            sensor.description = normalize_sensor_description(sensor.name, sensor.type, sensor.feed_key)

        for actuator in Actuator.query.all():
            actuator.name = normalize_actuator_name(actuator.name, actuator.type, actuator.feed_key)
            actuator.description = normalize_actuator_description(actuator.name, actuator.type, actuator.feed_key)

        db.session.commit()
    
    # ==================== Sensor Operations ====================
    
    @staticmethod
    def get_all_sensors() -> List[Sensor]:
        """Get all active sensors, dedupe theo loại cảm biến."""
        sensors = Sensor.query.filter_by(is_active=True).all()
        return DeviceService._dedupe_sensors(sensors)
    
    @staticmethod
    def get_sensor_by_id(sensor_id: int) -> Optional[Sensor]:
        """Get sensor by ID."""
        return Sensor.query.get(sensor_id)
    
    @staticmethod
    def create_sensor(name: str, sensor_type: str, feed_key: str,
                      unit: str = None, min_value: float = None,
                      max_value: float = None, description: str = None) -> Tuple[Optional[Sensor], str]:
        """
        Create a new sensor.
        
        Args:
            name: Sensor name
            sensor_type: Sensor type (temperature, humidity, light, pir)
            feed_key: Adafruit IO feed key
            unit: Unit of measurement
            min_value: Minimum value
            max_value: Maximum value
            description: Sensor description
            
        Returns:
            Tuple of (Sensor or None, error message)
        """
        if sensor_type not in Sensor.VALID_TYPES:
            return None, f"Invalid sensor type. Must be one of: {Sensor.VALID_TYPES}"
        
        # Check if feed_key already exists
        existing = Sensor.query.filter_by(feed_key=feed_key).first()
        if existing:
            return None, "Feed key already in use"
        
        sensor = Sensor(
            name=name,
            type=sensor_type,
            feed_key=feed_key,
            unit=unit or Sensor.get_unit_for_type(sensor_type),
            min_value=min_value,
            max_value=max_value,
            description=description
        )
        
        db.session.add(sensor)
        db.session.commit()
        
        # Subscribe to MQTT feed
        if mqtt_service:
            mqtt_service.subscribe(feed_key)
        
        return sensor, ""
    
    @staticmethod
    def update_sensor(sensor_id: int, name: str = None, unit: str = None,
                      min_value: float = None, max_value: float = None,
                      description: str = None) -> Tuple[Optional[Sensor], str]:
        """Update sensor properties."""
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return None, "Sensor not found"
        
        if name is not None:
            sensor.name = name
        if unit is not None:
            sensor.unit = unit
        if min_value is not None:
            sensor.min_value = min_value
        if max_value is not None:
            sensor.max_value = max_value
        if description is not None:
            sensor.description = description
        
        db.session.commit()
        return sensor, ""
    
    @staticmethod
    def delete_sensor(sensor_id: int) -> Tuple[bool, str]:
        """Delete a sensor."""
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return False, "Sensor not found"
        
        sensor.is_active = False
        db.session.commit()
        return True, ""
    

    @staticmethod
    def _sensor_canonical_key(sensor: Sensor) -> str:
        """Chuẩn hóa khóa để gom sensor trùng logic."""
        if sensor.type:
            return sensor.type.strip().lower()

        if sensor.feed_key:
            return sensor.feed_key.split('.')[0].strip().lower()

        return normalize_sensor_name(sensor.name, sensor.type, sensor.feed_key).strip().lower()

    @staticmethod
    def _dedupe_sensors(sensors: List[Sensor]) -> List[Sensor]:
        """Chỉ giữ 1 sensor cho mỗi loại thiết bị. Ưu tiên bản ghi mới nhất."""
        unique = {}
        ordered = sorted(
            sensors,
            key=lambda s: (
                s.updated_at or datetime.min,
                s.created_at or datetime.min,
                s.id or 0,
            ),
            reverse=True,
        )

        for sensor in ordered:
            key = DeviceService._sensor_canonical_key(sensor)
            if key not in unique:
                unique[key] = sensor

        return list(unique.values())

    # ==================== Actuator Operations ====================
    
    @staticmethod
    def get_all_actuators() -> List[Actuator]:
        """Get all active actuators, dedupe theo loại thiết bị."""
        actuators = Actuator.query.filter_by(is_active=True).all()
        return DeviceService._dedupe_actuators(actuators)
    
    @staticmethod
    def get_actuator_by_id(actuator_id: int) -> Optional[Actuator]:
        """Get actuator by ID."""
        return Actuator.query.get(actuator_id)
    
    @staticmethod
    def create_actuator(name: str, actuator_type: str, feed_key: str,
                        description: str = None) -> Tuple[Optional[Actuator], str]:
        """
        Create a new actuator.
        
        Args:
            name: Actuator name
            actuator_type: Actuator type (fan, led, rgb, servo, lcd)
            feed_key: Adafruit IO feed key
            description: Actuator description
            
        Returns:
            Tuple of (Actuator or None, error message)
        """
        if actuator_type not in Actuator.VALID_TYPES:
            return None, f"Invalid actuator type. Must be one of: {Actuator.VALID_TYPES}"
        
        # Check if feed_key already exists
        existing = Actuator.query.filter_by(feed_key=feed_key).first()
        if existing:
            return None, "Feed key already in use"
        
        actuator = Actuator(
            name=name,
            type=actuator_type,
            feed_key=feed_key,
            description=description
        )
        
        db.session.add(actuator)
        db.session.commit()
        
        return actuator, ""
    
    @staticmethod
    def update_actuator(actuator_id: int, name: str = None,
                        description: str = None) -> Tuple[Optional[Actuator], str]:
        """Update actuator properties."""
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None, "Actuator not found"
        
        if name is not None:
            actuator.name = name
        if description is not None:
            actuator.description = description
        
        db.session.commit()
        return actuator, ""
    
    @staticmethod
    def delete_actuator(actuator_id: int) -> Tuple[bool, str]:
        """Delete an actuator."""
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        actuator.is_active = False
        db.session.commit()
        return True, ""
    
    @staticmethod
    def control_actuator(actuator_id: int, action: str, user_id: int = None,
                         manual_override: bool = True) -> Tuple[bool, str]:
        """
        Control an actuator.
        
        Args:
            actuator_id: Actuator ID
            action: Action to perform (ON, OFF, or specific value)
            user_id: User ID performing the action
            manual_override: If True, switch to MANUAL mode
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        if not actuator.is_active:
            return False, "Actuator is not active"
        
        # Update actuator state
        actuator.current_value = action
        
        if manual_override:
            actuator.mode = Actuator.MODE_MANUAL
        
        # Send command via MQTT
        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, action)
        
        # Log the event
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL,
            description=f"User set {actuator.name} to {action}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
            metadata={'action': action}
        )
        
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def set_actuator_mode(actuator_id: int, mode: str) -> Tuple[bool, str]:
        """
        Set actuator mode (AUTO or MANUAL).
        
        Args:
            actuator_id: Actuator ID
            mode: Mode to set (AUTO or MANUAL)
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        if mode not in Actuator.VALID_MODES:
            return False, f"Invalid mode. Must be one of: {Actuator.VALID_MODES}"
        
        actuator.mode = mode
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def record_sensor_data(feed_key: str, value: float) -> Tuple[bool, str]:
        """
        Record sensor data from a feed.
        """
        normalized_key = str(feed_key or '').split('.')[0].strip().lower()

        sensors = Sensor.query.filter_by(is_active=True).all()
        sensor = None

        for item in sensors:
            item_key = str(item.feed_key or '').split('.')[0].strip().lower()
            item_type = str(item.type or '').strip().lower()

            if item_key == normalized_key or item_type == normalized_key:
                sensor = item
                break

        if not sensor:
            return False, "Sensor not found"

        sensor_data = SensorData(
            sensor_id=sensor.id,
            value=value
        )

        sensor.updated_at = datetime.utcnow()

        db.session.add(sensor_data)
        db.session.add(sensor)
        db.session.commit()

        return True, ""
    
    @staticmethod
    def get_device_status() -> dict:
        """
        Get overall device status summary.
        
        Returns:
            Dict with sensor and actuator status
        """
        sensors = DeviceService.get_all_sensors()
        actuators = DeviceService.get_all_actuators()
        
        return {
            'sensors': [s.to_dict() for s in sensors],
            'actuators': [a.to_dict() for a in actuators],
            'total_sensors': len(sensors),
            'total_actuators': len(actuators)
        }
    @staticmethod
    def _actuator_canonical_key(actuator: Actuator) -> str:
        """Chuẩn hóa khóa để gom các actuator trùng logic."""
        if actuator.type:
            return actuator.type.strip().lower()

        if actuator.feed_key:
            return actuator.feed_key.split('.')[0].strip().lower()

        return normalize_actuator_name(actuator.name, actuator.type, actuator.feed_key).strip().lower()


    @staticmethod
    def _dedupe_actuators(actuators: List[Actuator]) -> List[Actuator]:
        """
        Chỉ giữ 1 actuator cho mỗi loại thiết bị.
        Ưu tiên bản ghi mới nhất.
        """
        unique = {}
        ordered = sorted(
            actuators,
            key=lambda a: (
                a.updated_at or datetime.min,
                a.created_at or datetime.min,
                a.id or 0,
            ),
            reverse=True,
        )

        for actuator in ordered:
            key = DeviceService._actuator_canonical_key(actuator)
            if key not in unique:
                unique[key] = actuator

        return list(unique.values())