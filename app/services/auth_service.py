
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User, Session, PasswordResetToken


class AuthService:


    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def validate_email(email: str) -> bool:

        return bool(AuthService.EMAIL_REGEX.match(email))

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:


        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        return True, ""

    @staticmethod
    def register_user(email: str, password: str, first_name: str = None,
                      last_name: str = None) -> Tuple[Optional[User], str]:


        if not AuthService.validate_email(email):
            return None, "Invalid email format"

        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            return None, "Email already registered"

        is_valid, error_msg = AuthService.validate_password(password)
        if not is_valid:
            return None, error_msg

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


        user = User.query.filter_by(google_id=google_id).first()
        if user:
            return user, ""

        user = User.query.filter_by(email=email.lower()).first()
        if user:
            user.google_id = google_id
            user.is_verified = True
            db.session.commit()
            return user, ""

        user = User(
            email=email.lower(),
            google_id=google_id,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True
        )

        db.session.add(user)
        db.session.commit()

        return user, ""

    @staticmethod
    def login(email: str, password: str) -> Tuple[Optional[dict], str]:


        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return None, "Invalid email or password"

        if not user.password_hash:
            return None, "Please login with Google"

        if not user.check_password(password):
            return None, "Invalid email or password"

        if not user.is_active:
            return None, "Account is disabled"

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

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


        user, error = AuthService.register_with_google(google_id, email, first_name, last_name)
        if not user:
            return None, error

        if not user.is_active:
            return None, "Account is disabled"

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

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

        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:

        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def update_profile(user_id: int, first_name: str = None,
                       last_name: str = None) -> Tuple[Optional[User], str]:


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


        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        if not user.password_hash:
            return False, "Cannot change password for OAuth account"

        if not user.check_password(current_password):
            return False, "Current password is incorrect"

        is_valid, error_msg = AuthService.validate_password(new_password)
        if not is_valid:
            return False, error_msg

        user.set_password(new_password)
        db.session.commit()

        return True, ""

    @staticmethod
    def request_password_reset(email: str) -> Tuple[Optional[PasswordResetToken], str]:


        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return None, ""

        PasswordResetToken.query.filter_by(user_id=user.id, used=False).delete()

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


        user, error = AuthService.verify_reset_token(email, token)
        if not user:
            return False, error

        is_valid, error_msg = AuthService.validate_password(new_password)
        if not is_valid:
            return False, error_msg

        user.set_password(new_password)

        reset_token = PasswordResetToken.query.filter_by(
            user_id=user.id,
            token=token
        ).first()
        reset_token.mark_used()

        db.session.commit()

        return True, ""

    @staticmethod
    def deactivate_account(user_id: int) -> Tuple[bool, str]:


        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        user.is_active = False

        Session.query.filter_by(user_id=user_id).delete()

        db.session.commit()

        return True, ""
