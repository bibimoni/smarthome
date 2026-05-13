import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


def _make_actuator_mock(**kwargs):
    """Create an actuator mock with user_id=1 and id=1 by default."""
    mock = MagicMock()
    mock.user_id = kwargs.pop('user_id', 1)
    mock.id = kwargs.pop('id', 1)
    mock.to_dict.return_value = kwargs.pop('to_dict', {'id': 1, 'name': 'Fan'})
    for k, v in kwargs.items():
        setattr(mock, k, v)
    return mock


class TestActuatorsAPI:
    @pytest.fixture
    def app(self):
        from app.api.actuators import actuators_bp
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(app)
        app.register_blueprint(actuators_bp, url_prefix='/api/actuators')
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_header(self, app):
        with app.app_context():
            token = create_access_token(identity='1')
            return {'Authorization': f'Bearer {token}'}
    
    @patch('app.api.actuators.DeviceService')
    def test_get_actuators(self, mock_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_service.get_all_actuators.return_value = [mock_actuator]
        
        response = client.get('/api/actuators/', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'actuators' in data
        assert data['count'] == 1
    
    @patch('app.api.actuators.DeviceService')
    def test_get_actuator_by_id(self, mock_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_service.get_actuator_by_id.return_value = mock_actuator
        
        response = client.get('/api/actuators/1', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'actuator' in data
    
    @patch('app.api.actuators.DeviceService')
    def test_get_actuator_not_found(self, mock_service, client, auth_header):
        mock_service.get_actuator_by_id.return_value = None
        
        response = client.get('/api/actuators/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_get_all_status(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_all_actuators.return_value = [mock_actuator]
        mock_actuator_service.get_all_actuator_statuses.return_value = [{'id': 1, 'name': 'Fan'}]
        
        response = client.get('/api/actuators/status', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'actuators' in data
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_get_status(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.get_actuator_status.return_value = {'id': 1, 'is_on': False}
        
        response = client.get('/api/actuators/1/status', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_get_status_not_found(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_device_service.get_actuator_by_id.return_value = None
        
        response = client.get('/api/actuators/999/status', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_control_actuator_success(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.control_actuator.return_value = (True, '')
        
        response = client.post('/api/actuators/1/control',
            json={'action': 'ON'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_control_actuator_not_found(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_device_service.get_actuator_by_id.return_value = None
        
        response = client.post('/api/actuators/999/control',
            json={'action': 'ON'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_control_actuator_no_action(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        
        response = client.post('/api/actuators/1/control',
            json={},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_toggle_actuator_success(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.toggle_actuator.return_value = (True, '')
        
        response = client.post('/api/actuators/1/toggle', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_toggle_actuator_not_found(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_device_service.get_actuator_by_id.return_value = None
        
        response = client.post('/api/actuators/999/toggle', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_set_mode_success(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.set_actuator_mode.return_value = (True, '')
        
        response = client.post('/api/actuators/1/mode',
            json={'mode': 'MANUAL'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_set_mode_invalid(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.set_actuator_mode.return_value = (False, 'Invalid mode')
        
        response = client.post('/api/actuators/1/mode',
            json={'mode': 'INVALID'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.actuators.DeviceService')
    @patch('app.api.actuators.ActuatorService')
    def test_set_value_success(self, mock_actuator_service, mock_device_service, client, auth_header):
        mock_actuator = _make_actuator_mock()
        mock_device_service.get_actuator_by_id.return_value = mock_actuator
        mock_actuator_service.set_actuator_value.return_value = (True, '')
        
        response = client.post('/api/actuators/1/value',
            json={'value': '75'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.actuators.DeviceService')
    def test_create_actuator_success(self, mock_service, client, auth_header):
        mock_actuator = MagicMock()
        mock_actuator.to_dict.return_value = {'id': 1, 'name': 'Fan'}
        mock_service.create_actuator.return_value = (mock_actuator, '')
        
        response = client.post('/api/actuators/',
            json={'name': 'Fan', 'type': 'fan', 'feed_key': 'fan'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.actuators.DeviceService')
    def test_create_actuator_invalid(self, mock_service, client, auth_header):
        mock_service.create_actuator.return_value = (None, 'Invalid actuator type')
        
        response = client.post('/api/actuators/',
            json={'name': 'Test', 'type': 'invalid', 'feed_key': 'test'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400

    @patch('app.api.actuators.DeviceService')
    def test_create_actuator_requires_feed_key(self, mock_service, client, auth_header):
        response = client.post('/api/actuators/',
            json={'name': 'Fan', 'type': 'fan'},
            content_type='application/json', headers=auth_header)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'feed_key is required'
        mock_service.create_actuator.assert_not_called()
    
    @patch('app.api.actuators.DeviceService')
    def test_update_actuator_success(self, mock_service, client, auth_header):
        mock_existing = _make_actuator_mock()
        mock_service.get_actuator_by_id.return_value = mock_existing
        
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {'id': 1, 'name': 'Updated'}
        mock_service.update_actuator.return_value = (mock_updated, '')
        
        response = client.put('/api/actuators/1',
            json={'name': 'Updated'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.actuators.DeviceService')
    def test_delete_actuator_success(self, mock_service, client, auth_header):
        mock_existing = _make_actuator_mock()
        mock_service.get_actuator_by_id.return_value = mock_existing
        mock_service.delete_actuator.return_value = (True, '')
        
        response = client.delete('/api/actuators/1', headers=auth_header)
        
        assert response.status_code == 200
