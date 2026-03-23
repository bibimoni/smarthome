"""API package for REST endpoints."""
from app.api.auth import auth_bp
from app.api.sensors import sensors_bp
from app.api.actuators import actuators_bp
from app.api.scenes import scenes_bp
from app.api.thresholds import thresholds_bp
from app.api.logs import logs_bp
from app.api.iot import iot_bp

__all__ = [
    'auth_bp',
    'sensors_bp',
    'actuators_bp',
    'scenes_bp',
    'thresholds_bp',
    'logs_bp',
    'iot_bp'
]