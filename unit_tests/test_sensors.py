import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


class TestSensorsAPI:
    @pytest.fixture
    def app(self):
        from app.api.sensors import sensors_bp
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(app)
        app.register_blueprint(sensors_bp, url_prefix='/api/sensors')
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_header(self, app):
        with app.app_context():
            token = create_access_token(identity='1')
            return {'Authorization': f'Bearer {token}'}
    
    @patch('app.api.sensors.DeviceService')
    def test_get_sensors(self, mock_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1, 'name': 'Temperature'}
        mock_service.get_all_sensors.return_value = [mock_sensor]
        
        response = client.get('/api/sensors/', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sensors' in data
        assert data['count'] == 1
    
    @patch('app.api.sensors.DeviceService')
    def test_get_sensor_by_id(self, mock_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1, 'name': 'Temperature'}
        mock_service.get_sensor_by_id.return_value = mock_sensor
        
        response = client.get('/api/sensors/1', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sensor' in data
    
    @patch('app.api.sensors.DeviceService')
    def test_get_sensor_not_found(self, mock_service, client, auth_header):
        mock_service.get_sensor_by_id.return_value = None
        
        response = client.get('/api/sensors/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.sensors.SensorService')
    def test_get_current_readings(self, mock_service, client, auth_header):
        mock_service.get_current_readings.return_value = {'temperature': {'value': 25.0}}
        
        response = client.get('/api/sensors/readings', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'readings' in data
    
    @patch('app.api.sensors.DeviceService')
    @patch('app.api.sensors.SensorService')
    def test_get_sensor_data(self, mock_sensor_service, mock_device_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1}
        mock_device_service.get_sensor_by_id.return_value = mock_sensor
        
        mock_data = MagicMock()
        mock_data.to_dict.return_value = {'value': 25.0}
        mock_sensor_service.get_sensor_data_history.return_value = [mock_data]
        
        response = client.get('/api/sensors/1/data?hours=24', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    @patch('app.api.sensors.DeviceService')
    def test_get_sensor_data_not_found(self, mock_service, client, auth_header):
        mock_service.get_sensor_by_id.return_value = None
        
        response = client.get('/api/sensors/999/data', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.sensors.DeviceService')
    @patch('app.api.sensors.SensorService')
    def test_get_sensor_statistics(self, mock_sensor_service, mock_device_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.name = 'Temperature'
        mock_device_service.get_sensor_by_id.return_value = mock_sensor
        
        mock_sensor_service.get_sensor_statistics.return_value = {'min': 20.0, 'max': 30.0, 'avg': 25.0}
        
        response = client.get('/api/sensors/1/statistics?hours=24', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'statistics' in data
    
    @patch('app.api.sensors.DeviceService')
    @patch('app.api.sensors.SensorService')
    def test_get_latest_reading(self, mock_sensor_service, mock_device_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1}
        mock_device_service.get_sensor_by_id.return_value = mock_sensor
        
        mock_data = MagicMock()
        mock_data.to_dict.return_value = {'value': 25.0}
        mock_sensor_service.get_latest_sensor_data.return_value = mock_data
        
        response = client.get('/api/sensors/1/latest', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.sensors.DeviceService')
    def test_create_sensor_success(self, mock_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1, 'name': 'New Sensor'}
        mock_service.create_sensor.return_value = (mock_sensor, '')
        
        response = client.post('/api/sensors/',
            json={'name': 'New Sensor', 'type': 'temperature', 'feed_key': 'temp'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.sensors.DeviceService')
    def test_create_sensor_invalid(self, mock_service, client, auth_header):
        mock_service.create_sensor.return_value = (None, 'Invalid sensor type')
        
        response = client.post('/api/sensors/',
            json={'name': 'Test', 'type': 'invalid', 'feed_key': 'test'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.sensors.DeviceService')
    def test_update_sensor_success(self, mock_service, client, auth_header):
        mock_sensor = MagicMock()
        mock_sensor.to_dict.return_value = {'id': 1, 'name': 'Updated'}
        mock_service.update_sensor.return_value = (mock_sensor, '')
        
        response = client.put('/api/sensors/1',
            json={'name': 'Updated'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.sensors.DeviceService')
    def test_update_sensor_not_found(self, mock_service, client, auth_header):
        mock_service.update_sensor.return_value = (None, 'Sensor not found')
        
        response = client.put('/api/sensors/999',
            json={'name': 'Updated'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.sensors.DeviceService')
    def test_delete_sensor_success(self, mock_service, client, auth_header):
        mock_service.delete_sensor.return_value = (True, '')
        
        response = client.delete('/api/sensors/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.sensors.DeviceService')
    def test_delete_sensor_not_found(self, mock_service, client, auth_header):
        mock_service.delete_sensor.return_value = (False, 'Sensor not found')
        
        response = client.delete('/api/sensors/999', headers=auth_header)
        
        assert response.status_code == 404
