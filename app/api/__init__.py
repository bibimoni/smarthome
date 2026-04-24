<<<<<<< HEAD
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
=======
"""API package."""

# Tránh import eager toàn bộ blueprint tại đây vì dễ gây circular import.
# Hãy import trực tiếp trong app.main hoặc nơi cần dùng.

__all__ = []
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
