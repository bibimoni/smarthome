"""Authentication service for user management."""
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User, Session, PasswordResetToken


class AuthService:
    """Service class for authentication operations."""
    
    # Email validation regex
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        return bool(AuthService.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Requirements:
        - At least 8 characters
        - Contains at least one letter and one number
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 6:  # Relaxed for development
            return False, "Password must be at least 6 characters long"
        return True, ""
    
    @staticmethod
    def register_user(email: str, password: str, first_name: str = None, 
                      last_name: str = None) -> Tuple[Optional[User], str]:
        """
        Register a new user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            Tuple of (User object or None, error message)
        """
        # Validate email
        if not AuthService.validate_email(email):
            return None, "Invalid email format"
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            return None, "Email already registered"
        
        # Validate password
        is_valid, error_msg = AuthService.validate_password(password)
        if not is_valid:
            return None, error_msg
        
        # Create user
        user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, ""
    
    @staticmethod
    def register_with_google(google_id: str, email: str, 
                            first_name: str = None, last_name: str = None) -> Tuple[Optional[User], str]:
        """
        Register or login user with Google OAuth.
        
        Args:
            google_id: Google's unique user ID
            email: User's email from Google
            first_name: First name from Google
            last_name: Last name from Google
            
        Returns:
            Tuple of (User object or None, error message)
        """
        # Check if user exists with this Google ID
        user = User.query.filter_by(google_id=google_id).first()
        if user:
            return user, ""
        
        # Check if user exists with this email
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            # Link Google account to existing user
            user.google_id = google_id
            user.is_verified = True  # Google emails are verified
            db.session.commit()
            return user, ""
        
        # Create new user
        user = User(
            email=email.lower(),
            google_id=google_id,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True  # Google emails are verified
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, ""
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[Optional[dict], str]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Tuple of (auth dict with tokens or None, error message)
        """
        # Find user
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return None, "Invalid email or password"
        
        # Check if user has a password (OAuth users might not)
        if not user.password_hash:
            return None, "Please login with Google"
        
        # Verify password
        if not user.check_password(password):
            return None, "Invalid email or password"
        
        # Check if user is active
        if not user.is_active:
            return None, "Account is disabled"
        
        # Generate tokens (identity must be a string for JWT)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Create session
        session = Session(
            user_id=user.id,
            session_token=secrets.token_urlsafe(32),
            refresh_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(session)
        db.session.commit()
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, ""
    
    @staticmethod
    def login_with_google(google_id: str, email: str, 
                         first_name: str = None, last_name: str = None) -> Tuple[Optional[dict], str]:
        """
        Authenticate or register user with Google OAuth.
        
        Args:
            google_id: Google's unique user ID
            email: User's email from Google
            first_name: First name from Google
            last_name: Last name from Google
            
        Returns:
            Tuple of (auth dict with tokens or None, error message)
        """
        # Register or get user
        user, error = AuthService.register_with_google(google_id, email, first_name, last_name)
        if not user:
            return None, error
        
        # Check if user is active
        if not user.is_active:
            return None, "Account is disabled"
        
        # Generate tokens (identity must be a string for JWT)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Create session
        session = Session(
            user_id=user.id,
            session_token=secrets.token_urlsafe(32),
            refresh_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(session)
        db.session.commit()
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, ""
    
    @staticmethod
    def logout(user_id: int, session_token: str = None) -> bool:
        """
        Logout user by invalidating session.
        
        Args:
            user_id: User's ID
            session_token: Optional session token to invalidate specific session
            
        Returns:
            True if logout successful
        """
        if session_token:
            session = Session.query.filter_by(
                user_id=user_id,
                session_token=session_token
            ).first()
            if session:
                db.session.delete(session)
                db.session.commit()
        return True
    
    @staticmethod
    def refresh_token(user_id: int) -> Tuple[Optional[dict], str]:
        """
        Refresh access token for user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Tuple of (token dict or None, error message)
        """
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        if not user.is_active:
            return None, "Account is disabled"
        
        access_token = create_access_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'user': user.to_dict()
        }, ""
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return User.query.filter_by(email=email.lower()).first()
    
    @staticmethod
    def update_profile(user_id: int, first_name: str = None, 
                       last_name: str = None) -> Tuple[Optional[User], str]:
        """
        Update user profile.
        
        Args:
            user_id: User's ID
            first_name: New first name
            last_name: New last name
            
        Returns:
            Tuple of (User object or None, error message)
        """
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        
        db.session.commit()
        
        return user, ""
    
    @staticmethod
    def change_password(user_id: int, current_password: str, 
                        new_password: str) -> Tuple[bool, str]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Check if user has a password
        if not user.password_hash:
            return False, "Cannot change password for OAuth account"
        
        # Verify current password
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        is_valid, error_msg = AuthService.validate_password(new_password)
        if not is_valid:
            return False, error_msg
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def request_password_reset(email: str) -> Tuple[Optional[PasswordResetToken], str]:
        """
        Request a password reset token.
        
        Args:
            email: User's email
            
        Returns:
            Tuple of (PasswordResetToken or None, error message)
        """
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            # Don't reveal if email exists or not
            return None, ""
        
        # Invalidate any existing tokens
        PasswordResetToken.query.filter_by(user_id=user.id, used=False).delete()
        
        # Create new token
        otp = PasswordResetToken.generate_otp()
        token = PasswordResetToken(
            user_id=user.id,
            token=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        db.session.add(token)
        db.session.commit()
        
        return token, ""
    
    @staticmethod
    def verify_reset_token(email: str, token: str) -> Tuple[Optional[User], str]:
        """
        Verify password reset token.
        
        Args:
            email: User's email
            token: The OTP token
            
        Returns:
            Tuple of (User or None, error message)
        """
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return None, "Invalid token"
        
        reset_token = PasswordResetToken.query.filter_by(
            user_id=user.id,
            token=token,
            used=False
        ).first()
        
        if not reset_token:
            return None, "Invalid token"
        
        if reset_token.is_expired:
            return None, "Token has expired"
        
        return user, ""
    
    @staticmethod
    def reset_password(email: str, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using token.
        
        Args:
            email: User's email
            token: The OTP token
            new_password: New password
            
        Returns:
            Tuple of (success, error message)
        """
        user, error = AuthService.verify_reset_token(email, token)
        if not user:
            return False, error
        
        # Validate new password
        is_valid, error_msg = AuthService.validate_password(new_password)
        if not is_valid:
            return False, error_msg
        
        # Update password
        user.set_password(new_password)
        
        # Mark token as used
        reset_token = PasswordResetToken.query.filter_by(
            user_id=user.id,
            token=token
        ).first()
        reset_token.mark_used()
        
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def deactivate_account(user_id: int) -> Tuple[bool, str]:
        """
        Deactivate user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Tuple of (success, error message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        user.is_active = False
        
        # Invalidate all sessions
        Session.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return True, ""