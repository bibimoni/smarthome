import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask


class TestAuthAPI:
    @pytest.fixture
    def app(self):
        from app.api.auth import auth_bp
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @patch('app.api.auth.AuthService')
    def test_register_success(self, mock_service, client):
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
        mock_service.register_user.return_value = (mock_user, '')
        
        response = client.post('/api/auth/register', 
            json={'email': 'test@example.com', 'password': 'password123'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
    
    @patch('app.api.auth.AuthService')
    def test_register_invalid_email(self, mock_service, client):
        mock_service.register_user.return_value = (None, 'Invalid email format')
        
        response = client.post('/api/auth/register',
            json={'email': 'invalid', 'password': 'password123'})
        
        assert response.status_code == 400
    
    def test_register_no_data(self, client):
        response = client.post('/api/auth/register')
        assert response.status_code in [400, 415]
    
    def test_login_no_data(self, client):
        response = client.post('/api/auth/login')
        assert response.status_code in [400, 415]
    
    @patch('app.api.auth.AuthService')
    def test_login_success(self, mock_service, client):
        mock_service.login.return_value = ({
            'access_token': 'token',
            'refresh_token': 'refresh',
            'user': {'id': 1}
        }, '')
        
        response = client.post('/api/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'})
        
        assert response.status_code == 200
    
    @patch('app.api.auth.AuthService')
    def test_login_invalid_credentials(self, mock_service, client):
        mock_service.login.return_value = (None, 'Invalid email or password')
        
        response = client.post('/api/auth/login',
            json={'email': 'test@example.com', 'password': 'wrong'})
        
        assert response.status_code == 401
    
    @patch('app.api.auth.AuthService')
    def test_register_google_success(self, mock_service, client):
        mock_service.login_with_google.return_value = ({
            'access_token': 'token',
            'user': {'id': 1}
        }, '')
        
        response = client.post('/api/auth/register/google',
            json={'google_id': 'google123', 'email': 'test@gmail.com'})
        
        assert response.status_code == 200
    
    @patch('app.api.auth.AuthService')
    def test_register_google_missing_fields(self, mock_service, client):
        response = client.post('/api/auth/register/google',
            json={'google_id': 'google123'})
        
        assert response.status_code == 400
    
    @patch('app.api.auth.AuthService')
    def test_forgot_password(self, mock_service, client):
        mock_token = MagicMock()
        mock_token.token = '123456'
        mock_service.request_password_reset.return_value = (mock_token, '')
        
        with patch('app.api.auth.EmailService') as mock_email:
            mock_email.get_instance.return_value = None
            
            response = client.post('/api/auth/forgot-password',
                json={'email': 'test@example.com'})
        
        assert response.status_code == 200
    
    @patch('app.api.auth.AuthService')
    def test_reset_password_success(self, mock_service, client):
        mock_service.reset_password.return_value = (True, '')
        
        response = client.post('/api/auth/reset-password',
            json={'email': 'test@example.com', 'otp': '123456', 'new_password': 'newpass123'})
        
        assert response.status_code == 200
    
    @patch('app.api.auth.AuthService')
    def test_reset_password_invalid_otp(self, mock_service, client):
        mock_service.reset_password.return_value = (False, 'Invalid token')
        
        response = client.post('/api/auth/reset-password',
            json={'email': 'test@example.com', 'otp': '000000', 'new_password': 'newpass123'})
        
        assert response.status_code == 400
    
    @patch('app.api.auth.AuthService')
    def test_verify_otp_valid(self, mock_service, client):
        mock_service.verify_reset_token.return_value = (MagicMock(), '')
        
        response = client.post('/api/auth/verify-otp',
            json={'email': 'test@example.com', 'otp': '123456'})
        
        assert response.status_code == 200
    
    @patch('app.api.auth.AuthService')
    def test_verify_otp_invalid(self, mock_service, client):
        mock_service.verify_reset_token.return_value = (None, 'Invalid token')
        
        response = client.post('/api/auth/verify-otp',
            json={'email': 'test@example.com', 'otp': '000000'})
        
        assert response.status_code == 400
