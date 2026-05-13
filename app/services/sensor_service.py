
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from app.extensions import db
from app.models.device import Sensor
from app.models.data import SensorData


class SensorService:


    @staticmethod
    def get_all_sensors() -> List[Sensor]:

        return Sensor.query.filter_by(is_active=True).all()

    @staticmethod
    def get_sensor_by_id(sensor_id: int) -> Optional[Sensor]:

        return Sensor.query.get(sensor_id)

    @staticmethod
    def get_sensor_by_feed_key(feed_key: str) -> Optional[Sensor]:

        return Sensor.query.filter_by(feed_key=feed_key).first()

    @staticmethod
    def get_sensors_by_type(sensor_type: str) -> List[Sensor]:

        return Sensor.query.filter_by(type=sensor_type, is_active=True).all()

    @staticmethod
    def record_sensor_data(sensor_id: int, value: float) -> Tuple[Optional[SensorData], str]:


        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return None, "Sensor not found"

        if sensor.min_value is not None and value < sensor.min_value:
            return None, f"Value {value} is below minimum {sensor.min_value}"
        if sensor.max_value is not None and value > sensor.max_value:
            return None, f"Value {value} is above maximum {sensor.max_value}"

        sensor_data = SensorData(
            sensor_id=sensor_id,
            value=value
        )

        db.session.add(sensor_data)
        db.session.commit()

        return sensor_data, ""

    @staticmethod
    def get_latest_sensor_data(sensor_id: int) -> Optional[SensorData]:

        return SensorData.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorData.recorded_at.desc()).first()

    @staticmethod
    def get_sensor_data_history(sensor_id: int, hours: int = 24) -> List[SensorData]:


        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return SensorData.query.filter(
            SensorData.sensor_id == sensor_id,
            SensorData.recorded_at >= cutoff
        ).order_by(SensorData.recorded_at.asc()).all()

    @staticmethod
    def get_sensor_data_range(sensor_id: int, start_time: datetime,
                              end_time: datetime) -> List[SensorData]:


        return SensorData.query.filter(
            SensorData.sensor_id == sensor_id,
            SensorData.recorded_at >= start_time,
            SensorData.recorded_at <= end_time
        ).order_by(SensorData.recorded_at.asc()).all()

    @staticmethod
    def get_current_readings() -> dict:


        sensors = Sensor.query.filter_by(is_active=True).all()
        readings = {}

        for sensor in sensors:
            latest = sensor.get_latest_data()
            readings[sensor.type] = {
                'sensor_id': sensor.id,
                'name': sensor.name,
                'value': latest.value if latest else None,
                'unit': sensor.unit,
                'recorded_at': latest.recorded_at.isoformat() if latest else None
            }

        return readings

    @staticmethod
    def get_sensor_statistics(sensor_id: int, hours: int = 24) -> dict:


        data = SensorService.get_sensor_data_history(sensor_id, hours)

        if not data:
            return {
                'min': None,
                'max': None,
                'avg': None,
                'count': 0
            }

        values = [d.value for d in data]

        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }

    @staticmethod
    def cleanup_old_data(days: int = 90) -> int:


        return SensorData.cleanup_old_data(days)
