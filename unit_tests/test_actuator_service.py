import pytest
from unittest.mock import MagicMock, patch
from app.services.actuator_service import ActuatorService, get_mqtt_service


class TestActuatorService:
    @patch('app.services.actuator_service.Actuator')
    def test_get_all_actuators(self, mock_actuator_class):
        mock_actuators = [MagicMock(), MagicMock()]
        mock_actuator_class.query.filter_by.return_value.all.return_value = mock_actuators
        
        result = ActuatorService.get_all_actuators()
        
        assert len(result) == 2
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_actuator_by_id(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.get.return_value = mock_actuator
        
        result = ActuatorService.get_actuator_by_id(1)
        
        assert result == mock_actuator
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_actuator_by_feed_key(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.filter_by.return_value.first.return_value = mock_actuator
        
        result = ActuatorService.get_actuator_by_feed_key('fan')
        
        assert result == mock_actuator
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_actuators_by_type(self, mock_actuator_class):
        mock_actuators = [MagicMock()]
        mock_actuator_class.query.filter_by.return_value.all.return_value = mock_actuators
        
        result = ActuatorService.get_actuators_by_type('fan')
        
        assert len(result) == 1
    
    @patch('app.services.actuator_service.Actuator')
    @patch('app.services.actuator_service.db')
    def test_control_actuator_success(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = True
        mock_actuator.feed_key = 'fan'
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_actuator_class.query.get.return_value = mock_actuator
        
        with patch('app.services.actuator_service.get_mqtt_service', return_value=None), \
             patch('app.services.actuator_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            success, error = ActuatorService.control_actuator(1, 'ON', user_id=1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.actuator_service.Actuator')
    def test_control_actuator_not_found(self, mock_actuator_class):
        mock_actuator_class.query.get.return_value = None
        
        success, error = ActuatorService.control_actuator(999, 'ON')
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.actuator_service.Actuator')
    def test_control_actuator_inactive(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = False
        mock_actuator_class.query.get.return_value = mock_actuator
        
        success, error = ActuatorService.control_actuator(1, 'ON')
        
        assert success is False
        assert 'not active' in error
    
    @patch('app.services.actuator_service.Actuator')
    @patch('app.services.actuator_service.db')
    def test_set_actuator_mode_success(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_actuator.mode = 'AUTO'
        mock_actuator_class.query.get.return_value = mock_actuator
        mock_actuator_class.VALID_MODES = ['AUTO', 'MANUAL']
        
        with patch('app.services.actuator_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            success, error = ActuatorService.set_actuator_mode(1, 'MANUAL', user_id=1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.actuator_service.Actuator')
    def test_set_actuator_mode_invalid(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator_class.query.get.return_value = mock_actuator
        mock_actuator_class.VALID_MODES = ['AUTO', 'MANUAL']
        
        success, error = ActuatorService.set_actuator_mode(1, 'INVALID')
        
        assert success is False
        assert 'Invalid mode' in error
    
    @patch('app.services.actuator_service.Actuator')
    @patch('app.services.actuator_service.db')
    def test_toggle_actuator_off_to_on(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = True
        mock_actuator.is_on.return_value = False
        mock_actuator.feed_key = 'fan'
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_actuator_class.query.get.return_value = mock_actuator
        mock_actuator_class.ACTION_ON = 'ON'
        mock_actuator_class.ACTION_OFF = 'OFF'
        
        with patch.object(ActuatorService, 'control_actuator', return_value=(True, '')) as mock_control:
            success, error = ActuatorService.toggle_actuator(1, user_id=1)
            
            assert success is True
            mock_control.assert_called_once_with(1, 'ON', 1)
    
    @patch('app.services.actuator_service.Actuator')
    @patch('app.services.actuator_service.db')
    def test_toggle_actuator_on_to_off(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = True
        mock_actuator.is_on.return_value = True
        mock_actuator.feed_key = 'fan'
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_actuator_class.query.get.return_value = mock_actuator
        mock_actuator_class.ACTION_ON = 'ON'
        mock_actuator_class.ACTION_OFF = 'OFF'
        
        with patch.object(ActuatorService, 'control_actuator', return_value=(True, '')) as mock_control:
            success, error = ActuatorService.toggle_actuator(1, user_id=1)
            
            assert success is True
            mock_control.assert_called_once_with(1, 'OFF', 1)
    
    @patch('app.services.actuator_service.Actuator')
    def test_toggle_actuator_not_found(self, mock_actuator_class):
        mock_actuator_class.query.get.return_value = None
        
        success, error = ActuatorService.toggle_actuator(999)
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_actuator_status(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.id = 1
        mock_actuator.name = 'Fan'
        mock_actuator.type = 'fan'
        mock_actuator.current_value = 'ON'
        mock_actuator.mode = 'AUTO'
        mock_actuator.is_on.return_value = True
        mock_actuator.updated_at = None
        mock_actuator_class.query.get.return_value = mock_actuator
        
        result = ActuatorService.get_actuator_status(1)
        
        assert result['id'] == 1
        assert result['name'] == 'Fan'
        assert result['is_on'] is True
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_actuator_status_not_found(self, mock_actuator_class):
        mock_actuator_class.query.get.return_value = None
        
        result = ActuatorService.get_actuator_status(999)
        
        assert result is None
    
    @patch('app.services.actuator_service.Actuator')
    def test_get_all_actuator_statuses(self, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.id = 1
        mock_actuator.is_active = True
        mock_actuator_class.query.filter_by.return_value.all.return_value = [mock_actuator]
        
        with patch.object(ActuatorService, 'get_actuator_status', return_value={'id': 1}):
            result = ActuatorService.get_all_actuator_statuses()
        
        assert len(result) == 1
    
    @patch('app.services.actuator_service.Actuator')
    @patch('app.services.actuator_service.db')
    def test_set_actuator_value(self, mock_db, mock_actuator_class):
        mock_actuator = MagicMock()
        mock_actuator.is_active = True
        mock_actuator.feed_key = 'fan'
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_actuator_class.query.get.return_value = mock_actuator
        
        with patch.object(ActuatorService, 'control_actuator', return_value=(True, '')):
            success, error = ActuatorService.set_actuator_value(1, '75', user_id=1)
            
            assert success is True
