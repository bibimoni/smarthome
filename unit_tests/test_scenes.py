import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


def _make_scene_mock(**kwargs):
    """Create a scene mock with user_id=1 by default."""
    mock = MagicMock()
    mock.user_id = kwargs.pop('user_id', 1)
    mock.to_dict.return_value = kwargs.pop('to_dict', {'id': 1, 'name': 'Good Night'})
    for k, v in kwargs.items():
        setattr(mock, k, v)
    return mock


class TestScenesAPI:
    @pytest.fixture
    def app(self):
        from app.api.scenes import scenes_bp
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(app)
        app.register_blueprint(scenes_bp, url_prefix='/api/scenes')
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_header(self, app):
        with app.app_context():
            token = create_access_token(identity='1')
            return {'Authorization': f'Bearer {token}'}
    
    @patch('app.api.scenes.SceneService')
    def test_get_scenes(self, mock_service, client, auth_header):
        mock_scene = _make_scene_mock()
        mock_service.get_all_scenes.return_value = [mock_scene]
        
        response = client.get('/api/scenes/', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'scenes' in data
    
    @patch('app.api.scenes.SceneService')
    def test_get_scene_by_id(self, mock_service, client, auth_header):
        mock_scene = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_scene
        
        response = client.get('/api/scenes/1', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'scene' in data
    
    @patch('app.api.scenes.SceneService')
    def test_get_scene_not_found(self, mock_service, client, auth_header):
        mock_service.get_scene_by_id.return_value = None
        
        response = client.get('/api/scenes/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_get_scene_status(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_scene = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_scene
        mock_service.get_scene_status.return_value = {'id': 1, 'conditions_met': True}
        
        response = client.get('/api/scenes/1/status', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    @patch('app.api.scenes.SceneService')
    def test_get_scene_status_not_found(self, mock_service, client, auth_header):
        mock_service.get_scene_by_id.return_value = None
        
        response = client.get('/api/scenes/999/status', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_create_scene_success(self, mock_service, client, auth_header):
        mock_scene = MagicMock()
        mock_scene.to_dict.return_value = {'id': 1, 'name': 'Good Night'}
        mock_service.create_scene.return_value = (mock_scene, '')
        
        response = client.post('/api/scenes/',
            json={'name': 'Good Night', 'description': 'Turn off lights'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.scenes.SceneService')
    def test_create_scene_invalid(self, mock_service, client, auth_header):
        mock_service.create_scene.return_value = (None, 'Scene name is required')
        
        response = client.post('/api/scenes/',
            json={'name': ''},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.scenes.SceneService')
    def test_create_scene_no_data(self, mock_service, client, auth_header):
        response = client.post('/api/scenes/', headers=auth_header, data='')
        
        assert response.status_code in [400, 415]
    
    @patch('app.api.scenes.SceneService')
    def test_update_scene_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {'id': 1, 'name': 'Updated'}
        mock_service.update_scene.return_value = (mock_updated, '')
        
        response = client.put('/api/scenes/1',
            json={'name': 'Updated'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.scenes.SceneService')
    def test_update_scene_not_found(self, mock_service, client, auth_header):
        mock_service.get_scene_by_id.return_value = None
        
        response = client.put('/api/scenes/999',
            json={'name': 'Updated'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_delete_scene_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.delete_scene.return_value = (True, '')
        
        response = client.delete('/api/scenes/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.scenes.SceneService')
    def test_delete_scene_not_found(self, mock_service, client, auth_header):
        mock_service.get_scene_by_id.return_value = None
        
        response = client.delete('/api/scenes/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_execute_scene_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.execute_scene.return_value = (True, '')
        
        response = client.post('/api/scenes/1/execute', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.scenes.SceneService')
    def test_execute_scene_not_found(self, mock_service, client, auth_header):
        mock_service.get_scene_by_id.return_value = None
        
        response = client.post('/api/scenes/999/execute', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_execute_scene_inactive(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.execute_scene.return_value = (False, 'Scene is not active')
        
        response = client.post('/api/scenes/1/execute', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.scenes.SceneService')
    def test_add_condition_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        
        mock_condition = MagicMock()
        mock_condition.to_dict.return_value = {'id': 1, 'sensor_id': 1}
        mock_service.add_condition.return_value = (mock_condition, '')
        
        response = client.post('/api/scenes/1/conditions',
            json={'sensor_id': 1, 'operator': '>', 'threshold_value': 30.0},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.scenes.SceneService')
    def test_add_condition_invalid(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.add_condition.return_value = (None, 'Sensor not found')
        
        response = client.post('/api/scenes/1/conditions',
            json={'sensor_id': 999, 'operator': '>', 'threshold_value': 30.0},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_remove_condition_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.remove_condition.return_value = (True, '')
        
        response = client.delete('/api/scenes/1/conditions/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.scenes.SceneService')
    def test_remove_condition_not_found(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.remove_condition.return_value = (False, 'Condition not found')
        
        response = client.delete('/api/scenes/1/conditions/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.scenes.SceneService')
    def test_add_action_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        
        mock_action = MagicMock()
        mock_action.to_dict.return_value = {'id': 1, 'actuator_id': 1}
        mock_service.add_action.return_value = (mock_action, '')
        
        response = client.post('/api/scenes/1/actions',
            json={'actuator_id': 1, 'action_value': 'ON'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.scenes.SceneService')
    def test_remove_action_success(self, mock_service, client, auth_header):
        # Route calls get_scene_by_id for ownership check first
        mock_existing = _make_scene_mock()
        mock_service.get_scene_by_id.return_value = mock_existing
        mock_service.remove_action.return_value = (True, '')
        
        response = client.delete('/api/scenes/1/actions/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.scenes.SceneService')
    def test_check_scenes(self, mock_service, client, auth_header):
        mock_service.check_and_execute_scenes.return_value = None
        
        response = client.post('/api/scenes/check', headers=auth_header)
        
        assert response.status_code == 200
