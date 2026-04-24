import pytest
from unittest.mock import MagicMock, patch
from app.services.threshold_service import ThresholdService


class TestThresholdService:
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_all_rules(self, mock_rule_class):
        mock_rules = [MagicMock(), MagicMock()]
        mock_rule_class.query.all.return_value = mock_rules
        
        result = ThresholdService.get_all_rules()
        
        assert len(result) == 2
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_all_rules_filtered(self, mock_rule_class):
        mock_rules = [MagicMock()]
        mock_rule_class.query.filter_by.return_value.all.return_value = mock_rules
        
        result = ThresholdService.get_all_rules(is_active=True)
        
        assert len(result) == 1
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_rules_for_sensor(self, mock_rule_class):
        mock_rules = [MagicMock()]
        mock_rule_class.query.filter_by.return_value.all.return_value = mock_rules
        
        result = ThresholdService.get_rules_for_sensor(1)
        
        assert len(result) == 1
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_rules_for_actuator(self, mock_rule_class):
        mock_rules = [MagicMock()]
        mock_rule_class.query.filter_by.return_value.all.return_value = mock_rules
        
        result = ThresholdService.get_rules_for_actuator(1)
        
        assert len(result) == 1
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_rule_by_id(self, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule_class.query.get.return_value = mock_rule
        
        result = ThresholdService.get_rule_by_id(1)
        
        assert result == mock_rule
    
    @patch('app.services.threshold_service.ThresholdRule')
    @patch('app.services.threshold_service.Sensor')
    @patch('app.services.threshold_service.Actuator')
    @patch('app.services.threshold_service.db')
    def test_create_rule_success(self, mock_db, mock_actuator_class, mock_sensor_class, mock_rule_class):
        mock_sensor_class.query.get.return_value = MagicMock()
        mock_actuator_class.query.get.return_value = MagicMock()
        mock_rule_class.VALID_OPERATORS = ['>', '<', '==', '>=', '<=']
        
        rule, error = ThresholdService.create_rule(
            sensor_id=1,
            operator='>',
            threshold_value=30.0,
            actuator_id=1,
            action_value='ON'
        )
        
        assert error == ''
    
    @patch('app.services.threshold_service.Sensor')
    def test_create_rule_sensor_not_found(self, mock_sensor_class):
        mock_sensor_class.query.get.return_value = None
        
        rule, error = ThresholdService.create_rule(
            sensor_id=999,
            operator='>',
            threshold_value=30.0,
            actuator_id=1,
            action_value='ON'
        )
        
        assert rule is None
        assert 'Sensor not found' in error
    
    @patch('app.services.threshold_service.Sensor')
    @patch('app.services.threshold_service.Actuator')
    def test_create_rule_actuator_not_found(self, mock_actuator_class, mock_sensor_class):
        mock_sensor_class.query.get.return_value = MagicMock()
        mock_actuator_class.query.get.return_value = None
        
        rule, error = ThresholdService.create_rule(
            sensor_id=1,
            operator='>',
            threshold_value=30.0,
            actuator_id=999,
            action_value='ON'
        )
        
        assert rule is None
        assert 'Actuator not found' in error
    
    @patch('app.services.threshold_service.Sensor')
    @patch('app.services.threshold_service.Actuator')
    def test_create_rule_invalid_operator(self, mock_actuator_class, mock_sensor_class):
        mock_sensor_class.query.get.return_value = MagicMock()
        mock_actuator_class.query.get.return_value = MagicMock()
        
        rule, error = ThresholdService.create_rule(
            sensor_id=1,
            operator='invalid',
            threshold_value=30.0,
            actuator_id=1,
            action_value='ON'
        )
        
        assert rule is None
        assert 'Invalid operator' in error
    
    @patch('app.services.threshold_service.ThresholdRule')
    @patch('app.services.threshold_service.db')
    def test_update_rule_success(self, mock_db, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule_class.query.get.return_value = mock_rule
        
        rule, error = ThresholdService.update_rule(1, threshold_value=35.0)
        
        assert error == ''
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_update_rule_not_found(self, mock_rule_class):
        mock_rule_class.query.get.return_value = None
        
        rule, error = ThresholdService.update_rule(999, threshold_value=35.0)
        
        assert rule is None
        assert 'not found' in error
    
    @patch('app.services.threshold_service.ThresholdRule')
    @patch('app.services.threshold_service.db')
    def test_delete_rule_success(self, mock_db, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule_class.query.get.return_value = mock_rule
        
        success, error = ThresholdService.delete_rule(1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_delete_rule_not_found(self, mock_rule_class):
        mock_rule_class.query.get.return_value = None
        
        success, error = ThresholdService.delete_rule(999)
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.threshold_service.ThresholdRule')
    @patch('app.services.threshold_service.db')
    def test_toggle_rule(self, mock_db, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.is_active = True
        mock_rule_class.query.get.return_value = mock_rule
        
        rule, error = ThresholdService.toggle_rule(1)
        
        assert error == ''
        assert mock_rule.is_active is False
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_evaluate_rule_true(self, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.is_active = True
        mock_rule.evaluate.return_value = True
        mock_rule.action_value = 'ON'
        mock_sensor = MagicMock()
        mock_sensor.get_latest_data.return_value = MagicMock(value=35.0)
        mock_rule.sensor = mock_sensor
        mock_rule_class.query.get.return_value = mock_rule
        
        condition_met, action = ThresholdService.evaluate_rule(1)
        
        assert condition_met is True
        assert action == 'ON'
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_evaluate_rule_inactive(self, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.is_active = False
        mock_rule_class.query.get.return_value = mock_rule
        
        condition_met, action = ThresholdService.evaluate_rule(1)
        
        assert condition_met is False
        assert action is None
    
    @patch('app.services.threshold_service.ThresholdRule')
    @patch('app.services.threshold_service.db')
    def test_evaluate_and_execute_success(self, mock_db, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.is_active = True
        mock_rule.action_value = 'ON'
        mock_rule.evaluate.return_value = True
        mock_rule.get_condition_string.return_value = 'Temperature > 30°C'
        mock_sensor = MagicMock()
        mock_sensor.get_latest_data.return_value = MagicMock(value=35.0)
        mock_rule.sensor = mock_sensor
        mock_actuator = MagicMock()
        mock_actuator.mode = 'AUTO'
        mock_actuator.current_value = 'OFF'
        mock_actuator.feed_key = 'fan'
        mock_actuator.name = 'Fan'
        mock_actuator.id = 1
        mock_rule.actuator = mock_actuator
        mock_rule_class.query.get.return_value = mock_rule
        
        with patch('app.services.threshold_service.mqtt_service', None), \
             patch('app.services.threshold_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            executed, message = ThresholdService.evaluate_and_execute(1)
        
        assert executed is True
        assert 'Executed' in message
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_evaluate_and_execute_manual_mode(self, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.is_active = True
        mock_actuator = MagicMock()
        mock_actuator.mode = 'MANUAL'
        mock_actuator.name = 'Fan'
        mock_rule.actuator = mock_actuator
        mock_rule_class.query.get.return_value = mock_rule
        
        executed, message = ThresholdService.evaluate_and_execute(1)
        
        assert executed is False
        assert 'MANUAL mode' in message
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_rule_status(self, mock_rule_class):
        mock_rule = MagicMock()
        mock_rule.id = 1
        mock_rule.action_value = 'ON'
        mock_rule.is_active = True
        mock_rule.evaluate.return_value = True
        mock_rule.get_condition_string.return_value = 'Temperature > 30°C'
        mock_sensor = MagicMock()
        mock_sensor.id = 1
        mock_sensor.name = 'Temperature'
        mock_sensor.type = 'temperature'
        mock_sensor.unit = '°C'
        mock_sensor.get_latest_data.return_value = MagicMock(value=35.0)
        mock_rule.sensor = mock_sensor
        mock_actuator = MagicMock()
        mock_actuator.id = 1
        mock_actuator.name = 'Fan'
        mock_actuator.current_value = 'OFF'
        mock_actuator.mode = 'AUTO'
        mock_rule.actuator = mock_actuator
        mock_rule_class.query.get.return_value = mock_rule
        
        result = ThresholdService.get_rule_status(1)
        
        assert result['id'] == 1
        assert result['condition_met'] is True
    
    @patch('app.services.threshold_service.ThresholdRule')
    def test_get_rule_status_not_found(self, mock_rule_class):
        mock_rule_class.query.get.return_value = None
        
        result = ThresholdService.get_rule_status(999)
        
        assert result is None
