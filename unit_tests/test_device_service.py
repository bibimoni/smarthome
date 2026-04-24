import pytest
from unittest.mock import MagicMock, patch
from app.services.device_service import DeviceService


class TestDeviceService:
    @patch('app.services.device_service.Sensor')
    @patch('app.services.device_service.db')
    def test_get_all_sensors(self, mock_db, mock_sensor_class):
        mock_sensors = [MagicMock(), MagicMock()]
        mock_sensor_class.query.filter_by.return_value.all.return_value = mock_sensors
        
        result = DeviceService.get_all_sensors()
        
        assert len(result) == 2
    
    @patch('app.services.device_service.Sensor')
    def test_get_sensor_by_id(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor_class.query.get.return_value = mock_sensor
        
        result = DeviceService.get_sensor_by_id(1)
        
        assert result == mock_sensor
    
    @patch('app.services.device_service.Sensor')
    @patch('app.services.device_service.db')
    def test_create_sensor_success(self, mock_db, mock_sensor_class):
        mock_sensor_class.query.filter_by.return_value.first.return_value = None
        mock_sensor_class.VALID_TYPES = ['temperature', 'humidity', 'light', 'pir']
        
        with patch('app.services.device_service.mqtt_service', None):
            sensor, error = DeviceService.create_sensor(
                name='Temperature',
                sensor_type='temperature',
                feed_key='temp'
            )
        
        assert error == ''
    
    @patch('app.services.device_service.Sensor')
    def test_create_sensor_invalid_type(self, mock_sensor_class):
        sensor, error = DeviceService.create_sensor(
            name='Test',
            sensor_type='invalid',
            feed_key='test'
        )
        
        assert sensor is None
        assert 'Invalid sensor type' in error
    
    @patch('app.services.device_service.Sensor')
    def test_create_sensor_duplicate_feed_key(self, mock_sensor_class):
        mock_sensor_class.query.filter_by.return_value.first.return_value = MagicMock()
        mock_sensor_class.VALID_TYPES = ['temperature', 'humidity', 'light', 'pir']
        
        sensor, error = DeviceService.create_sensor(
            name='Test',
            sensor_type='temperature',
            feed_key='existing_key'
        )
        
        assert sensor is None
        assert 'already in use' in error
    
    @patch('app.services.device_service.Sensor')
    @patch('app.services.device_service.db')
    def test_update_sensor(self, mock_db, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor_class.query.get.return_value = mock_sensor
        
        sensor, error = DeviceService.update_sensor(1, name='New Name')
        
        assert error == ''
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.device_service.Sensor')
    def test_update_sensor_not_found(self, mock_sensor_class):
        mock_sensor_class.query.get.return_value = None
        
        sensor, error = DeviceService.update_sensor(999, name='New Name')
        
        assert sensor is None
        assert 'not found' in error
    
    @patch('app.services.device_service.Sensor')
    @patch('app.services.device_service.db')
    def test_delete_sensor(self, mock_db, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor_class.query.get.return_value = mock_sensor
        
        success, error = DeviceService.delete_sensor(1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.device_service.Actuator')
    @patch('app.services.device_service.db')
    def test_get_all_actuators(self, mock_db, mock_actuator_class):
        mock_actuators = [MagicMock(), MagicMock()]
        mock_actuator_class.query.filter_by.return_value.all.return_value = mock_actuators
        
        result = DeviceService.get_all_actuators()
        
        assert len(result) == 2
    
    @patch('app.services.device_service.Actuator')
    def test_get_actuator_by_id(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.get.return_value = mock_actuator
        
        result = DeviceService.get_actuator_by_id(1)
        
        assert result == mock_actuator
    
    @patch('app.services.device_service.Actuator')
    @patch('app.services.device_service.db')
    def test_create_actuator_success(self, mock_db, mock_actuator_class):
        mock_actuator_class.query.filter_by.return_value.first.return_value = None
        mock_actuator_class.VALID_TYPES = ['fan', 'led', 'rgb', 'servo', 'lcd']
        
        actuator, error = DeviceService.create_actuator(
            name='Fan',
            actuator_type='fan',
            feed_key='fan'
        )
        
        assert error == ''
    
    @patch('app.services.device_service.Actuator')
    def test_create_actuator_invalid_type(self, mock_actuator_class):
        actuator, error = DeviceService.create_actuator(
            name='Test',
            actuator_type='invalid',
            feed_key='test'
        )
        
        assert actuator is None
        assert 'Invalid actuator type' in error
    
    @patch('app.services.device_service.Actuator')
    @patch('app.services.device_service.db')
    def test_control_actuator_success(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = True
        mock_actuator_class.query.get.return_value = mock_actuator
        
        with patch('app.services.device_service.mqtt_service', None), \
             patch('app.services.device_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            success, error = DeviceService.control_actuator(1, 'ON', user_id=1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.device_service.Actuator')
    def test_control_actuator_not_found(self, mock_actuator_class):
        mock_actuator_class.query.get.return_value = None
        
        success, error = DeviceService.control_actuator(999, 'ON')
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.device_service.Actuator')
    def test_control_actuator_inactive(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = False
        mock_actuator_class.query.get.return_value = mock_actuator
        
        success, error = DeviceService.control_actuator(1, 'ON')
        
        assert success is False
        assert 'not active' in error
    
    @patch('app.services.device_service.Actuator')
    @patch('app.services.device_service.db')
    def test_set_actuator_mode(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.get.return_value = mock_actuator
        mock_actuator_class.VALID_MODES = ['AUTO', 'MANUAL']
        
        success, error = DeviceService.set_actuator_mode(1, 'MANUAL')
        
        assert success is True
        assert error == ''
    
    @patch('app.services.device_service.Actuator')
    def test_set_actuator_mode_invalid(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.get.return_value = mock_actuator
        
        success, error = DeviceService.set_actuator_mode(1, 'INVALID')
        
        assert success is False
        assert 'Invalid mode' in error
    
    @patch('app.services.device_service.Sensor')
    @patch('app.services.device_service.SensorData')
    @patch('app.services.device_service.db')
    def test_record_sensor_data(self, mock_db, mock_data_class, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor.id = 1
        mock_sensor.is_active = True
        mock_sensor_class.query.filter_by.return_value.first.return_value = mock_sensor
        
        success, error = DeviceService.record_sensor_data('temperature', 25.5)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.device_service.Sensor')
    def test_record_sensor_data_sensor_not_found(self, mock_sensor_class):
        mock_sensor_class.query.filter_by.return_value.first.return_value = None
        
        success, error = DeviceService.record_sensor_data('unknown', 25.5)
        
        assert success is False
        assert 'not found' in error
