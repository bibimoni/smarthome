import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.models.data import SensorData, EventLog


class TestSensorData:
    def test_to_dict(self):
        data = SensorData(
            id=1,
            sensor_id=1,
            value=25.5,
            recorded_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        result = data.to_dict()
        assert result['id'] == 1
        assert result['sensor_id'] == 1
        assert result['value'] == 25.5
    
    def test_repr(self):
        data = SensorData(sensor_id=1, value=25.5)
        assert 'sensor=1' in repr(data)
        assert '25.5' in repr(data)


class TestEventLog:
    def test_valid_types(self):
        assert 'ALERT' in EventLog.VALID_TYPES
        assert 'AUTO' in EventLog.VALID_TYPES
        assert 'MANUAL' in EventLog.VALID_TYPES
        assert 'ERROR' in EventLog.VALID_TYPES
        assert 'SCENE' in EventLog.VALID_TYPES
    
    def test_to_dict(self):
        log = EventLog(
            id=1,
            event_type='MANUAL',
            actuator_id=1,
            user_id=1,
            description='User set Fan to ON',
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        result = log.to_dict()
        assert result['id'] == 1
        assert result['event_type'] == 'MANUAL'
        assert result['actuator_id'] == 1
        assert result['description'] == 'User set Fan to ON'
    
    def test_repr(self):
        log = EventLog(event_type='MANUAL', description='Test event')
        assert 'MANUAL' in repr(log)
        assert 'Test event' in repr(log)
