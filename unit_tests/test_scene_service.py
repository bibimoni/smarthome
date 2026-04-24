import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.services.scene_service import SceneService


class TestSceneService:
    @patch('app.services.scene_service.Scene')
    def test_get_all_scenes(self, mock_scene_class):
        mock_scenes = [MagicMock(), MagicMock()]
        mock_scene_class.query.filter_by.return_value.filter_by.return_value.all.return_value = mock_scenes
        
        result = SceneService.get_all_scenes(user_id=1)
        
        assert len(result) == 2
    
    @patch('app.services.scene_service.Scene')
    def test_get_scene_by_id(self, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene_class.query.get.return_value = mock_scene
        
        result = SceneService.get_scene_by_id(1)
        
        assert result == mock_scene
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.db')
    def test_create_scene_success(self, mock_db, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.id = 1
        mock_scene_class.return_value = mock_scene
        
        with patch('app.services.scene_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            scene, error = SceneService.create_scene(
                user_id=1,
                name='Good Night',
                description='Turn off lights'
            )
        
        assert error == ''
        mock_db.session.add.assert_called()
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.SceneCondition')
    @patch('app.services.scene_service.SceneAction')
    @patch('app.services.scene_service.Sensor')
    @patch('app.services.scene_service.Actuator')
    @patch('app.services.scene_service.db')
    def test_create_scene_with_conditions_and_actions(self, mock_db, mock_actuator_class, mock_sensor_class, mock_action_class, mock_condition_class, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.id = 1
        mock_scene_class.return_value = mock_scene
        
        mock_sensor_class.query.get.return_value = MagicMock()
        mock_actuator_class.query.get.return_value = MagicMock()
        mock_condition_class.VALID_OPERATORS = ['>', '<', '==', '>=', '<=']
        
        with patch('app.services.scene_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            scene, error = SceneService.create_scene(
                user_id=1,
                name='Auto Fan',
                conditions=[{'sensor_id': 1, 'operator': '>', 'threshold_value': 30.0}],
                actions=[{'actuator_id': 1, 'action_value': 'ON'}]
            )
        
        assert error == ''
    
    def test_create_scene_empty_name(self):
        scene, error = SceneService.create_scene(user_id=1, name='')
        
        assert scene is None
        assert 'required' in error
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.db')
    def test_update_scene_success(self, mock_db, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene_class.query.get.return_value = mock_scene
        
        scene, error = SceneService.update_scene(1, name='New Name')
        
        assert error == ''
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.scene_service.Scene')
    def test_update_scene_not_found(self, mock_scene_class):
        mock_scene_class.query.get.return_value = None
        
        scene, error = SceneService.update_scene(999, name='New Name')
        
        assert scene is None
        assert 'not found' in error
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.db')
    def test_delete_scene_success(self, mock_db, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene_class.query.get.return_value = mock_scene
        
        success, error = SceneService.delete_scene(1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.scene_service.Scene')
    def test_delete_scene_not_found(self, mock_scene_class):
        mock_scene_class.query.get.return_value = None
        
        success, error = SceneService.delete_scene(999)
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.SceneCondition')
    @patch('app.services.scene_service.Sensor')
    @patch('app.services.scene_service.db')
    def test_add_condition_success(self, mock_db, mock_sensor_class, mock_condition_class, mock_scene_class):
        mock_scene_class.query.get.return_value = MagicMock()
        mock_sensor_class.query.get.return_value = MagicMock()
        mock_condition_class.VALID_OPERATORS = ['>', '<', '==', '>=', '<=']
        
        condition, error = SceneService.add_condition(
            scene_id=1,
            sensor_id=1,
            operator='>',
            threshold_value=30.0
        )
        
        assert error == ''
    
    @patch('app.services.scene_service.Scene')
    def test_add_condition_scene_not_found(self, mock_scene_class):
        mock_scene_class.query.get.return_value = None
        
        condition, error = SceneService.add_condition(
            scene_id=999,
            sensor_id=1,
            operator='>',
            threshold_value=30.0
        )
        
        assert condition is None
        assert 'not found' in error
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.SceneCondition')
    @patch('app.services.scene_service.db')
    def test_remove_condition_success(self, mock_db, mock_condition_class, mock_scene_class):
        mock_condition = MagicMock()
        mock_condition_class.query.get.return_value = mock_condition
        
        success, error = SceneService.remove_condition(1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.scene_service.SceneCondition')
    def test_remove_condition_not_found(self, mock_condition_class):
        mock_condition_class.query.get.return_value = None
        
        success, error = SceneService.remove_condition(999)
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.SceneAction')
    @patch('app.services.scene_service.Actuator')
    @patch('app.services.scene_service.db')
    def test_add_action_success(self, mock_db, mock_actuator_class, mock_action_class, mock_scene_class):
        mock_scene_class.query.get.return_value = MagicMock()
        mock_actuator_class.query.get.return_value = MagicMock()
        mock_action = MagicMock()
        mock_action_class.return_value = mock_action
        
        action, error = SceneService.add_action(
            scene_id=1,
            actuator_id=1,
            action_value='ON'
        )
        
        assert error == ''
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.SceneAction')
    @patch('app.services.scene_service.db')
    def test_remove_action_success(self, mock_db, mock_action_class, mock_scene_class):
        mock_action = MagicMock()
        mock_action_class.query.get.return_value = mock_action
        
        success, error = SceneService.remove_action(1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.db')
    def test_execute_scene_success(self, mock_db, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.is_active = True
        mock_scene.name = 'Good Night'
        mock_scene.trigger.return_value = []
        mock_scene_class.query.get.return_value = mock_scene
        
        with patch('app.services.scene_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            success, error = SceneService.execute_scene(1, user_id=1)
        
        assert success is True
        assert error == ''
    
    @patch('app.services.scene_service.Scene')
    def test_execute_scene_not_found(self, mock_scene_class):
        mock_scene_class.query.get.return_value = None
        
        success, error = SceneService.execute_scene(999)
        
        assert success is False
        assert 'not found' in error
    
    @patch('app.services.scene_service.Scene')
    def test_execute_scene_inactive(self, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.is_active = False
        mock_scene_class.query.get.return_value = mock_scene
        
        success, error = SceneService.execute_scene(1)
        
        assert success is False
        assert 'not active' in error
    
    @patch('app.services.scene_service.Scene')
    def test_get_scene_status(self, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.id = 1
        mock_scene.name = 'Good Night'
        mock_scene.is_active = True
        mock_scene.last_triggered_at = None
        mock_scene.evaluate_conditions.return_value = True
        mock_scene.conditions = []
        mock_scene.actions = []
        mock_scene_class.query.get.return_value = mock_scene
        
        result = SceneService.get_scene_status(1)
        
        assert result['id'] == 1
        assert result['is_active'] is True
        assert result['conditions_met'] is True
    
    @patch('app.services.scene_service.Scene')
    def test_get_scene_status_not_found(self, mock_scene_class):
        mock_scene_class.query.get.return_value = None
        
        result = SceneService.get_scene_status(999)
        
        assert result is None
    
    @patch('app.services.scene_service.Scene')
    @patch('app.services.scene_service.db')
    def test_check_and_execute_scenes(self, mock_db, mock_scene_class):
        mock_scene = MagicMock()
        mock_scene.id = 1
        mock_scene.name = 'Test Scene'
        mock_scene.user_id = 1
        mock_scene.last_triggered_at = None
        mock_scene.evaluate_conditions.return_value = True
        mock_scene.trigger.return_value = []
        mock_scene_class.query.filter_by.return_value.all.return_value = [mock_scene]
        
        with patch('app.services.scene_service.EventLog') as mock_event_log:
            mock_event_log.log_event = MagicMock()
            
            SceneService.check_and_execute_scenes()
        
        mock_scene.trigger.assert_called_once()
