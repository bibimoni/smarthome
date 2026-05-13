
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from app.extensions import db


class User(db.Model):


    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    scenes = db.relationship('Scene', backref='user', lazy=True, cascade='all, delete-orphan')
    event_logs = db.relationship('EventLog', backref='user', lazy=True)

    def set_password(self, password: str):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:

        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ""

    def create_session(self) -> 'Session':

        session = Session(
            user_id=self.id,
            session_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(session)
        db.session.commit()
        return session

    def to_dict(self, include_sensitive=False) -> dict:

        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data['google_id'] = self.google_id
        return data

    def __repr__(self):
        return f'<User {self.email}>'


class Session(db.Model):


    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    refresh_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def is_expired(self) -> bool:

        return datetime.utcnow() > self.expires_at

    def refresh(self):

        self.expires_at = datetime.utcnow() + timedelta(days=30)
        db.session.commit()

    def revoke(self):

        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def cleanup_expired():

        expired_sessions = Session.query.filter(Session.expires_at < datetime.utcnow()).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return len(expired_sessions)

    def to_dict(self) -> dict:

        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Session {self.id} for User {self.user_id}>'


class PasswordResetToken(db.Model):


    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(6), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='password_reset_tokens')

    @property
    def is_expired(self) -> bool:

        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:

        return not self.is_expired and not self.used

    @staticmethod
    def generate_otp() -> str:

        import random
        return str(random.randint(100000, 999999))

    def mark_used(self):

        self.used = True
        db.session.commit()

    def to_dict(self) -> dict:

        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
        }
