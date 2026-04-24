import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.services.auth_service import AuthService


class TestAuthService:
    def test_validate_email_valid(self):
        assert AuthService.validate_email('test@example.com') is True
        assert AuthService.validate_email('user.name@domain.co') is True
    
    def test_validate_email_invalid(self):
        assert AuthService.validate_email('invalid') is False
        assert AuthService.validate_email('test@') is False
        assert AuthService.validate_email('@domain.com') is False
    
    def test_validate_password_valid(self):
        is_valid, error = AuthService.validate_password('password123')
        assert is_valid is True
        assert error == ''
    
    def test_validate_password_too_short(self):
        is_valid, error = AuthService.validate_password('12345')
        assert is_valid is False
        assert '6 characters' in error
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_register_user_success(self, mock_db, mock_user_class):
        mock_user_class.query.filter_by.return_value.first.return_value = None
        mock_user = MagicMock()
        mock_user_class.return_value = mock_user
        
        user, error = AuthService.register_user('test@example.com', 'password123', 'John', 'Doe')
        
        assert error == ''
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_register_user_invalid_email(self, mock_user_class):
        user, error = AuthService.register_user('invalid-email', 'password123')
        
        assert user is None
        assert 'Invalid email' in error
    
    @patch('app.services.auth_service.User')
    def test_register_user_existing_email(self, mock_user_class):
        mock_user_class.query.filter_by.return_value.first.return_value = MagicMock()
        
        user, error = AuthService.register_user('existing@example.com', 'password123')
        
        assert user is None
        assert 'already registered' in error
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_login_success(self, mock_db, mock_user_class):
        mock_user = MagicMock()
        mock_user.password_hash = 'hashed'
        mock_user.is_active = True
        mock_user.check_password.return_value = True
        mock_user.id = 1
        mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        with patch('app.services.auth_service.create_access_token') as mock_access, \
             patch('app.services.auth_service.create_refresh_token') as mock_refresh, \
             patch('app.services.auth_service.Session') as mock_session_class:
            mock_access.return_value = 'access_token'
            mock_refresh.return_value = 'refresh_token'
            
            result, error = AuthService.login('test@example.com', 'password123')
            
            assert error == ''
            assert result['access_token'] == 'access_token'
    
    @patch('app.services.auth_service.User')
    def test_login_user_not_found(self, mock_user_class):
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        result, error = AuthService.login('test@example.com', 'password123')
        
        assert result is None
        assert 'Invalid email or password' in error
    
    @patch('app.services.auth_service.User')
    def test_login_wrong_password(self, mock_user_class):
        mock_user = MagicMock()
        mock_user.password_hash = 'hashed'
        mock_user.check_password.return_value = False
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        result, error = AuthService.login('test@example.com', 'wrongpassword')
        
        assert result is None
        assert 'Invalid email or password' in error
    
    @patch('app.services.auth_service.User')
    def test_login_user_inactive(self, mock_user_class):
        mock_user = MagicMock()
        mock_user.password_hash = 'hashed'
        mock_user.is_active = False
        mock_user.check_password.return_value = True
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        result, error = AuthService.login('test@example.com', 'password123')
        
        assert result is None
        assert 'disabled' in error
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_get_user_by_id(self, mock_db, mock_user_class):
        mock_user = MagicMock()
        mock_user_class.query.get.return_value = mock_user
        
        result = AuthService.get_user_by_id(1)
        
        assert result == mock_user
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_update_profile(self, mock_db, mock_user_class):
        mock_user = MagicMock()
        mock_user_class.query.get.return_value = mock_user
        
        user, error = AuthService.update_profile(1, 'John', 'Doe')
        
        assert error == ''
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_update_profile_user_not_found(self, mock_user_class):
        mock_user_class.query.get.return_value = None
        
        user, error = AuthService.update_profile(999, 'John', 'Doe')
        
        assert user is None
        assert 'not found' in error
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.db')
    def test_change_password_success(self, mock_db, mock_user_class):
        mock_user = MagicMock()
        mock_user.password_hash = 'hashed'
        mock_user.check_password.return_value = True
        mock_user_class.query.get.return_value = mock_user
        
        success, error = AuthService.change_password(1, 'oldpassword', 'newpassword123')
        
        assert success is True
        assert error == ''
    
    @patch('app.services.auth_service.User')
    def test_change_password_wrong_current(self, mock_user_class):
        mock_user = MagicMock()
        mock_user.password_hash = 'hashed'
        mock_user.check_password.return_value = False
        mock_user_class.query.get.return_value = mock_user
        
        success, error = AuthService.change_password(1, 'wrongpassword', 'newpassword123')
        
        assert success is False
        assert 'incorrect' in error
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.PasswordResetToken')
    @patch('app.services.auth_service.db')
    def test_request_password_reset(self, mock_db, mock_token_class, mock_user_class):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        mock_token_class.generate_otp.return_value = '123456'
        
        token, error = AuthService.request_password_reset('test@example.com')
        
        assert error == ''
        mock_db.session.add.assert_called_once()
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.PasswordResetToken')
    @patch('app.services.auth_service.db')
    def test_verify_reset_token_valid(self, mock_db, mock_token_class, mock_user_class):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        mock_token = MagicMock()
        mock_token.is_expired = False
        mock_token_class.query.filter_by.return_value.first.return_value = mock_token
        
        user, error = AuthService.verify_reset_token('test@example.com', '123456')
        
        assert error == ''
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.Session')
    @patch('app.services.auth_service.db')
    def test_deactivate_account(self, mock_db, mock_session_class, mock_user_class):
        mock_user = MagicMock()
        mock_user_class.query.get.return_value = mock_user
        
        success, error = AuthService.deactivate_account(1)
        
        assert success is True
        assert error == ''
        mock_db.session.commit.assert_called_once()
