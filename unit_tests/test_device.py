import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.models.device import Sensor, Actuator


class TestSensor:
    def test_get_unit_for_type_temperature(self):
        assert Sensor.get_unit_for_type('temperature') == '°C'
    
    def test_get_unit_for_type_humidity(self):
        assert Sensor.get_unit_for_type('humidity') == '%'
    
    def test_get_unit_for_type_light(self):
        assert Sensor.get_unit_for_type('light') == 'lux'
    
    def test_get_unit_for_type_pir(self):
        assert Sensor.get_unit_for_type('pir') == ''
    
    def test_get_unit_for_type_unknown(self):
        assert Sensor.get_unit_for_type('unknown') == ''
    
    def test_get_range_for_type_temperature(self):
        assert Sensor.get_range_for_type('temperature') == (-40, 80)
    
    def test_get_range_for_type_humidity(self):
        assert Sensor.get_range_for_type('humidity') == (0, 100)
    
    def test_get_range_for_type_light(self):
        assert Sensor.get_range_for_type('light') == (0, 4095)
    
    def test_get_range_for_type_unknown(self):
        assert Sensor.get_range_for_type('unknown') == (None, None)
    
    def test_valid_types(self):
        assert 'temperature' in Sensor.VALID_TYPES
        assert 'humidity' in Sensor.VALID_TYPES
        assert 'light' in Sensor.VALID_TYPES
        assert 'pir' in Sensor.VALID_TYPES
    
    def test_repr(self):
        sensor = Sensor(name='Temperature', type='temperature')
        assert 'Temperature' in repr(sensor)
        assert 'temperature' in repr(sensor)


class TestActuator:
    def test_is_on_true(self):
        actuator = Actuator()
        actuator.current_value = 'ON'
        assert actuator.is_on() is True
    
    def test_is_on_with_value(self):
        actuator = Actuator()
        actuator.current_value = '75'
        assert actuator.is_on() is True
    
    def test_is_on_false(self):
        actuator = Actuator()
        actuator.current_value = 'OFF'
        assert actuator.is_on() is False
    
    def test_is_on_none(self):
        actuator = Actuator()
        actuator.current_value = None
        assert not actuator.is_on()
    
    def test_valid_types(self):
        assert 'fan' in Actuator.VALID_TYPES
        assert 'led' in Actuator.VALID_TYPES
        assert 'rgb' in Actuator.VALID_TYPES
        assert 'servo' in Actuator.VALID_TYPES
        assert 'lcd' in Actuator.VALID_TYPES
    
    def test_valid_modes(self):
        assert 'AUTO' in Actuator.VALID_MODES
        assert 'MANUAL' in Actuator.VALID_MODES
    
    def test_valid_actions(self):
        assert 'ON' in Actuator.VALID_ACTIONS
        assert 'OFF' in Actuator.VALID_ACTIONS
    
    def test_to_dict(self):
        actuator = Actuator(
            id=1,
            name='Fan',
            type='fan',
            feed_key='fan',
            current_value='OFF',
            mode='AUTO',
            is_active=True,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1)
        )
        result = actuator.to_dict()
        assert result['id'] == 1
        assert result['name'] == 'Fan'
        assert result['type'] == 'fan'
        assert result['current_value'] == 'OFF'
        assert result['mode'] == 'AUTO'
        assert result['is_on'] is False
    
    def test_repr(self):
        actuator = Actuator(name='Fan', type='fan')
        assert 'Fan' in repr(actuator)
        assert 'fan' in repr(actuator)
