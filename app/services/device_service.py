
from typing import List, Optional, Tuple
from datetime import datetime
from app.extensions import db
from app.models.device import Sensor, Actuator
from app.models.data import SensorData, EventLog
from app.services.mqtt_service import mqtt_service


class DeviceService:


    DEFAULT_SENSORS = [
        {
            'name': 'Temperature',
            'type': Sensor.TYPE_TEMPERATURE,
            'feed_key': 'temperature',
            'unit': '°C',
            'min_value': -40,
            'max_value': 80,
            'description': 'DHT20 Temperature Sensor'
        },
        {
            'name': 'Humidity',
            'type': Sensor.TYPE_HUMIDITY,
            'feed_key': 'humidity',
            'unit': '%',
            'min_value': 0,
            'max_value': 100,
            'description': 'DHT20 Humidity Sensor'
        },
        {
            'name': 'Light',
            'type': Sensor.TYPE_LIGHT,
            'feed_key': 'light',
            'unit': 'lux',
            'min_value': 0,
            'max_value': 4095,
            'description': 'Analog Light Sensor'
        }
    ]

    DEFAULT_ACTUATORS = [
        {
            'name': 'Fan',
            'type': Actuator.TYPE_FAN,
            'feed_key': 'fan',
            'description': 'PWM Controlled Fan'
        },
        {
            'name': 'LED',
            'type': Actuator.TYPE_LED,
            'feed_key': 'led',
            'description': 'On/Off LED'
        }
    ]

    @staticmethod
    def create_default_devices(user_id=None):

        for sensor_config in DeviceService.DEFAULT_SENSORS:
            existing = Sensor.query.filter_by(feed_key=sensor_config['feed_key']).first()
            if not existing:
                sensor = Sensor(user_id=user_id, **sensor_config)
                db.session.add(sensor)

        for actuator_config in DeviceService.DEFAULT_ACTUATORS:
            existing = Actuator.query.filter_by(feed_key=actuator_config['feed_key']).first()
            if not existing:
                actuator = Actuator(user_id=user_id, **actuator_config)
                db.session.add(actuator)

        db.session.commit()


    @staticmethod
    def get_all_sensors() -> List[Sensor]:

        return Sensor.query.filter_by(is_active=True).all()

    @staticmethod
    def get_sensor_by_id(sensor_id: int) -> Optional[Sensor]:

        return Sensor.query.get(sensor_id)

    @staticmethod
    def create_sensor(name: str, sensor_type: str, feed_key: str,
                      user_id: int = None, unit: str = None, min_value: float = None,
                      max_value: float = None, description: str = None) -> Tuple[Optional[Sensor], str]:


        if sensor_type not in Sensor.VALID_TYPES:
            return None, f"Invalid sensor type. Must be one of: {Sensor.VALID_TYPES}"

        existing = Sensor.query.filter_by(feed_key=feed_key).first()
        if existing:
            return None, "Feed key already in use"

        sensor = Sensor(
            user_id=user_id,
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

        if mqtt_service:
            mqtt_service.subscribe(feed_key)

        return sensor, ""

    @staticmethod
    def update_sensor(sensor_id: int, name: str = None, unit: str = None,
                      min_value: float = None, max_value: float = None,
                      description: str = None) -> Tuple[Optional[Sensor], str]:

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

        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return False, "Sensor not found"

        sensor.is_active = False
        db.session.commit()
        return True, ""


    @staticmethod
    def get_all_actuators() -> List[Actuator]:

        return Actuator.query.filter_by(is_active=True).all()

    @staticmethod
    def get_actuator_by_id(actuator_id: int) -> Optional[Actuator]:

        return Actuator.query.get(actuator_id)

    @staticmethod
    def create_actuator(name: str, actuator_type: str, feed_key: str,
                        user_id: int = None, description: str = None) -> Tuple[Optional[Actuator], str]:


        if actuator_type not in Actuator.VALID_TYPES:
            return None, f"Invalid actuator type. Must be one of: {Actuator.VALID_TYPES}"

        existing = Actuator.query.filter_by(feed_key=feed_key).first()
        if existing:
            return None, "Feed key already in use"

        actuator = Actuator(
            user_id=user_id,
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

        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"

        actuator.is_active = False
        db.session.commit()
        return True, ""

    @staticmethod
    def control_actuator(actuator_id: int, action: str, user_id: int = None,
                         manual_override: bool = True) -> Tuple[bool, str]:


        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"

        if not actuator.is_active:
            return False, "Actuator is not active"

        actuator.current_value = action

        if manual_override:
            actuator.mode = Actuator.MODE_MANUAL

        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, action)

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


        sensor = Sensor.query.filter_by(feed_key=feed_key, is_active=True).first()
        if not sensor:
            return False, "Sensor not found"

        sensor_data = SensorData(
            sensor_id=sensor.id,
            value=value
        )

        db.session.add(sensor_data)
        db.session.commit()

        return True, ""

    @staticmethod
    def get_device_status() -> dict:


        sensors = Sensor.query.filter_by(is_active=True).all()
        actuators = Actuator.query.filter_by(is_active=True).all()

        return {
            'sensors': [s.to_dict() for s in sensors],
            'actuators': [a.to_dict() for a in actuators],
            'total_sensors': len(sensors),
            'total_actuators': len(actuators)
        }
