import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock
from app.models.user import User, Session, PasswordResetToken


class TestUser:
    def test_set_password(self):
        user = User(email='test@example.com')
        user.set_password('password123')
        assert user.password_hash is not None
        assert user.password_hash != 'password123'
    
    def test_check_password_correct(self):
        user = User(email='test@example.com')
        user.set_password('password123')
        assert user.check_password('password123') is True
    
    def test_check_password_incorrect(self):
        user = User(email='test@example.com')
        user.set_password('password123')
        assert user.check_password('wrongpassword') is False
    
    def test_check_password_no_hash(self):
        user = User(email='test@example.com')
        user.password_hash = None
        assert user.check_password('password123') is False
    
    def test_full_name_both_names(self):
        user = User(email='test@example.com', first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'
    
    def test_full_name_first_only(self):
        user = User(email='test@example.com', first_name='John')
        assert user.full_name == 'John'
    
    def test_full_name_last_only(self):
        user = User(email='test@example.com', last_name='Doe')
        assert user.full_name == 'Doe'
    
    def test_full_name_none(self):
        user = User(email='test@example.com')
        assert user.full_name == ''
    
    def test_to_dict(self):
        user = User(
            id=1,
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            is_active=True,
            is_verified=False,
            created_at=datetime(2024, 1, 1)
        )
        result = user.to_dict()
        assert result['id'] == 1
        assert result['email'] == 'test@example.com'
        assert result['first_name'] == 'John'
        assert result['last_name'] == 'Doe'
        assert result['full_name'] == 'John Doe'
        assert result['is_active'] is True
        assert result['is_verified'] is False
    
    def test_to_dict_include_sensitive(self):
        user = User(
            id=1,
            email='test@example.com',
            google_id='google123'
        )
        result = user.to_dict(include_sensitive=True)
        assert result['google_id'] == 'google123'
    
    def test_repr(self):
        user = User(email='test@example.com')
        assert 'test@example.com' in repr(user)


class TestSession:
    def test_is_expired_false(self):
        session = Session()
        session.expires_at = datetime.utcnow() + timedelta(days=1)
        assert session.is_expired is False
    
    def test_is_expired_true(self):
        session = Session()
        session.expires_at = datetime.utcnow() - timedelta(days=1)
        assert session.is_expired is True
    
    def test_to_dict(self):
        session = Session(
            id=1,
            user_id=1,
            expires_at=datetime(2024, 12, 31),
            created_at=datetime(2024, 1, 1)
        )
        result = session.to_dict()
        assert result['id'] == 1
        assert result['user_id'] == 1


class TestPasswordResetToken:
    def test_is_expired_false(self):
        token = PasswordResetToken()
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        assert token.is_expired is False
    
    def test_is_expired_true(self):
        token = PasswordResetToken()
        token.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert token.is_expired is True
    
    def test_is_valid_true(self):
        token = PasswordResetToken()
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        token.used = False
        assert token.is_valid is True
    
    def test_is_valid_expired(self):
        token = PasswordResetToken()
        token.expires_at = datetime.utcnow() - timedelta(hours=1)
        token.used = False
        assert token.is_valid is False
    
    def test_is_valid_used(self):
        token = PasswordResetToken()
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        token.used = True
        assert token.is_valid is False
    
    def test_generate_otp(self):
        otp = PasswordResetToken.generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_to_dict(self):
        token = PasswordResetToken(
            id=1,
            user_id=1,
            expires_at=datetime(2024, 12, 31),
            used=False
        )
        result = token.to_dict()
        assert result['id'] == 1
        assert result['user_id'] == 1
        assert result['used'] is False
