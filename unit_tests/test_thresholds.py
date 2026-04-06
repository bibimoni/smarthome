import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


class TestThresholdsAPI:
    @pytest.fixture
    def app(self):
        from app.api.thresholds import thresholds_bp
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(app)
        app.register_blueprint(thresholds_bp, url_prefix='/api/thresholds')
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_header(self, app):
        with app.app_context():
            token = create_access_token(identity='1')
            return {'Authorization': f'Bearer {token}'}
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rules(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1, 'threshold_value': 30.0}
        mock_service.get_all_rules.return_value = [mock_rule]
        
        response = client.get('/api/thresholds/', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rules' in data
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rules_filtered(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1}
        mock_service.get_all_rules.return_value = [mock_rule]
        
        response = client.get('/api/thresholds/?is_active=true', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rule_by_id(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1, 'threshold_value': 30.0}
        mock_service.get_rule_by_id.return_value = mock_rule
        
        response = client.get('/api/thresholds/1', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rule' in data
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rule_not_found(self, mock_service, client, auth_header):
        mock_service.get_rule_by_id.return_value = None
        
        response = client.get('/api/thresholds/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rule_status(self, mock_service, client, auth_header):
        mock_service.get_rule_status.return_value = {'id': 1, 'condition_met': True}
        
        response = client.get('/api/thresholds/1/status', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rule_status_not_found(self, mock_service, client, auth_header):
        mock_service.get_rule_status.return_value = None
        
        response = client.get('/api/thresholds/999/status', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rules_for_sensor(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1}
        mock_service.get_rules_for_sensor.return_value = [mock_rule]
        
        response = client.get('/api/thresholds/sensor/1', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rules' in data
    
    @patch('app.api.thresholds.ThresholdService')
    def test_get_rules_for_actuator(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1}
        mock_service.get_rules_for_actuator.return_value = [mock_rule]
        
        response = client.get('/api/thresholds/actuator/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.thresholds.ThresholdService')
    def test_create_rule_success(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1, 'threshold_value': 30.0}
        mock_service.create_rule.return_value = (mock_rule, '')
        
        response = client.post('/api/thresholds/',
            json={'sensor_id': 1, 'operator': '>', 'threshold_value': 30.0, 'actuator_id': 1, 'action_value': 'ON'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 201
    
    @patch('app.api.thresholds.ThresholdService')
    def test_create_rule_invalid(self, mock_service, client, auth_header):
        mock_service.create_rule.return_value = (None, 'Invalid operator')
        
        response = client.post('/api/thresholds/',
            json={'sensor_id': 1, 'operator': 'invalid', 'threshold_value': 30.0, 'actuator_id': 1, 'action_value': 'ON'},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 400
    
    @patch('app.api.thresholds.ThresholdService')
    def test_update_rule_success(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.to_dict.return_value = {'id': 1}
        mock_service.update_rule.return_value = (mock_rule, '')
        
        response = client.put('/api/thresholds/1',
            json={'threshold_value': 35.0},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.thresholds.ThresholdService')
    def test_update_rule_not_found(self, mock_service, client, auth_header):
        mock_service.update_rule.return_value = (None, 'Rule not found')
        
        response = client.put('/api/thresholds/999',
            json={'threshold_value': 35.0},
            content_type='application/json', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.thresholds.ThresholdService')
    def test_delete_rule_success(self, mock_service, client, auth_header):
        mock_service.delete_rule.return_value = (True, '')
        
        response = client.delete('/api/thresholds/1', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.thresholds.ThresholdService')
    def test_delete_rule_not_found(self, mock_service, client, auth_header):
        mock_service.delete_rule.return_value = (False, 'Rule not found')
        
        response = client.delete('/api/thresholds/999', headers=auth_header)
        
        assert response.status_code == 404
    
    @patch('app.api.thresholds.ThresholdService')
    def test_toggle_rule_success(self, mock_service, client, auth_header):
        mock_rule = MagicMock()
        mock_rule.is_active = False
        mock_rule.to_dict.return_value = {'id': 1, 'is_active': False}
        mock_service.toggle_rule.return_value = (mock_rule, '')
        
        response = client.post('/api/thresholds/1/toggle', headers=auth_header)
        
        assert response.status_code == 200
    
    @patch('app.api.thresholds.ThresholdService')
    def test_evaluate_rule(self, mock_service, client, auth_header):
        mock_service.evaluate_rule.return_value = (True, 'ON')
        
        response = client.post('/api/thresholds/1/evaluate', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['condition_met'] is True
    
    @patch('app.api.thresholds.ThresholdService')
    def test_evaluate_all_rules(self, mock_service, client, auth_header):
        mock_service.evaluate_all_rules.return_value = {'executed': [], 'skipped': [], 'errors': []}
        
        response = client.post('/api/thresholds/evaluate-all', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
