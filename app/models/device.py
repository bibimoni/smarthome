"""Sensor and Actuator models for device management."""
from datetime import datetime
from app.extensions import db
from app.models.data import SensorData


class Sensor(db.Model):
    """Sensor model for input devices (temperature, humidity, light, PIR)."""

    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    feed_key = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(20), nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = db.relationship('User', backref='sensors')
    sensor_data = db.relationship('SensorData', backref='sensor', lazy=True, cascade='all, delete-orphan')
    threshold_rules = db.relationship('ThresholdRule', backref='sensor', lazy=True)
    scene_conditions = db.relationship('SceneCondition', backref='sensor', lazy=True)

    TYPE_TEMPERATURE = 'temperature'
    TYPE_HUMIDITY = 'humidity'
    TYPE_LIGHT = 'light'
    TYPE_PIR = 'pir'

    VALID_TYPES = [TYPE_TEMPERATURE, TYPE_HUMIDITY, TYPE_LIGHT, TYPE_PIR]

    @staticmethod
    def get_unit_for_type(sensor_type: str) -> str:
        """Get the default unit for a sensor type."""
        units = {
            Sensor.TYPE_TEMPERATURE: '°C',
            Sensor.TYPE_HUMIDITY: '%',
            Sensor.TYPE_LIGHT: 'lux',
            Sensor.TYPE_PIR: '',
        }
        return units.get(sensor_type, '')

    @staticmethod
    def get_range_for_type(sensor_type: str) -> tuple:
        """Get the default min/max range for a sensor type."""
        ranges = {
            Sensor.TYPE_TEMPERATURE: (-40, 80),
            Sensor.TYPE_HUMIDITY: (0, 100),
            Sensor.TYPE_LIGHT: (0, 4095),
            Sensor.TYPE_PIR: (0, 1),
        }
        return ranges.get(sensor_type, (None, None))

    def get_latest_data(self) -> 'SensorData':
        """Get the latest sensor data reading."""
        return SensorData.query.filter_by(sensor_id=self.id).order_by(SensorData.recorded_at.desc()).first()

    def get_data_in_range(self, start_time: datetime, end_time: datetime) -> list:
        """Get sensor data within a time range."""
        return SensorData.query.filter(
            SensorData.sensor_id == self.id,
            SensorData.recorded_at >= start_time,
            SensorData.recorded_at <= end_time
        ).order_by(SensorData.recorded_at.asc()).all()

    def to_dict(self) -> dict:
        """Convert sensor to dictionary."""
        latest = self.get_latest_data()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'feed_key': self.feed_key,
            'unit': self.unit,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'description': self.description,
            'is_active': self.is_active,
            'latest_value': latest.value if latest else None,
            'latest_recorded_at': latest.recorded_at.isoformat() if latest and latest.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Sensor {self.name} ({self.type})>'


class Actuator(db.Model):
    """Actuator model for output devices (fan, LED, RGB, servo)."""

    __tablename__ = 'actuators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    feed_key = db.Column(db.String(255), nullable=False)
    current_value = db.Column(db.String(50), nullable=True)
    mode = db.Column(db.String(20), default='AUTO', nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = db.relationship('User', backref='actuators')
    event_logs = db.relationship('EventLog', backref='actuator', lazy=True)
    threshold_rules = db.relationship('ThresholdRule', backref='actuator', lazy=True)
    scene_actions = db.relationship('SceneAction', backref='actuator', lazy=True)

    TYPE_FAN = 'fan'
    TYPE_LED = 'led'
    TYPE_RGB = 'rgb'
    TYPE_SERVO = 'servo'
    TYPE_LCD = 'lcd'

    MODE_AUTO = 'AUTO'
    MODE_MANUAL = 'MANUAL'

    ACTION_ON = 'ON'
    ACTION_OFF = 'OFF'

    VALID_TYPES = [TYPE_FAN, TYPE_LED, TYPE_RGB, TYPE_SERVO, TYPE_LCD]
    VALID_MODES = [MODE_AUTO, MODE_MANUAL]
    VALID_ACTIONS = [ACTION_ON, ACTION_OFF]

    def turn_on(self, value: str = None):
        """Turn the actuator on."""
        self.current_value = value or self.ACTION_ON
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def turn_off(self):
        """Turn the actuator off."""
        self.current_value = self.ACTION_OFF
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def set_mode(self, mode: str):
        """Set the actuator mode (AUTO or MANUAL)."""
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.VALID_MODES}")
        self.mode = mode
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def is_on(self) -> bool:
        """Check if the actuator is on."""
        return self.current_value and self.current_value.upper() != self.ACTION_OFF

    def to_dict(self) -> dict:
        """Convert actuator to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'feed_key': self.feed_key,
            'current_value': self.current_value,
            'mode': self.mode,
            'is_on': self.is_on(),
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Actuator {self.name} ({self.type})>'
