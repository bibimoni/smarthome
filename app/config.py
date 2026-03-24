"""Application configuration module."""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database - Use SQLite for development by default
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///yolohome.db'  # SQLite for easy development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours for dev
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # Use headers only for token delivery (not cookies)
    JWT_TOKEN_LOCATION = ['headers']
    # Disable CSRF for header-based authentication
    JWT_COOKIE_CSRF_PROTECT = False
    # Allow integer identity (user.id)
    JWT_JSON_KEY = 'identity'
    # Accept token with or without "Bearer " prefix
    JWT_HEADER_TYPE = None
    
    # Google OAuth (Optional - leave empty for development)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    # Email (Optional for development - skipped if not configured)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
    
    # Adafruit IO (for MQTT communication with YoloBit)
    ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME', 'quanghung2405')
    ADAFRUIT_IO_KEY = os.environ.get(
        'ADAFRUIT_IO_KEY',
        'aio_anJO06oMkhLtJbAYhp4yRGMmoFoe'
    )
    
    # Application
    APP_NAME = os.environ.get('APP_NAME', 'YoloHome')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Disable SQL query logging


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=300)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # In production, these must be set
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY must be set in production")
        return key
    
    @property
    def JWT_SECRET_KEY(self):
        key = os.environ.get('JWT_SECRET_KEY')
        if not key:
            raise ValueError("JWT_SECRET_KEY must be set in production")
        return key


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)