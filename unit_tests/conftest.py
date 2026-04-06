import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from flask import Flask
from app.extensions import db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_db_session():
    with patch('app.extensions.db.session') as mock_session:
        yield mock_session


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.email = 'test@example.com'
    user.first_name = 'Test'
    user.last_name = 'User'
    user.is_active = True
    user.is_verified = False
    user.google_id = None
    user.password_hash = 'hashed_password'
    user.full_name = 'Test User'
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.to_dict.return_value = {
        'id': 1,
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'full_name': 'Test User',
        'is_active': True,
        'is_verified': False
    }
    user.check_password.return_value = True
    return user


@pytest.fixture
def mock_sensor():
    sensor = MagicMock()
    sensor.id = 1
    sensor.name = 'Temperature'
    sensor.type = 'temperature'
    sensor.feed_key = 'temperature'
    sensor.unit = '°C'
    sensor.min_value = -40.0
    sensor.max_value = 80.0
    sensor.description = 'DHT20 Temperature Sensor'
    sensor.is_active = True
    sensor.created_at = datetime.utcnow()
    sensor.updated_at = datetime.utcnow()
    sensor.to_dict.return_value = {
        'id': 1,
        'name': 'Temperature',
        'type': 'temperature',
        'feed_key': 'temperature',
        'unit': '°C',
        'min_value': -40.0,
        'max_value': 80.0,
        'description': 'DHT20 Temperature Sensor',
        'is_active': True
    }
    return sensor


@pytest.fixture
def mock_actuator():
    actuator = MagicMock()
    actuator.id = 1
    actuator.name = 'Fan'
    actuator.type = 'fan'
    actuator.feed_key = 'fan'
    actuator.current_value = 'OFF'
    actuator.mode = 'AUTO'
    actuator.description = 'PWM Controlled Fan'
    actuator.is_active = True
    actuator.is_on.return_value = False
    actuator.created_at = datetime.utcnow()
    actuator.updated_at = datetime.utcnow()
    actuator.to_dict.return_value = {
        'id': 1,
        'name': 'Fan',
        'type': 'fan',
        'feed_key': 'fan',
        'current_value': 'OFF',
        'mode': 'AUTO',
        'is_on': False,
        'is_active': True
    }
    return actuator


@pytest.fixture
def mock_sensor_data():
    data = MagicMock()
    data.id = 1
    data.sensor_id = 1
    data.value = 25.5
    data.recorded_at = datetime.utcnow()
    data.to_dict.return_value = {
        'id': 1,
        'sensor_id': 1,
        'value': 25.5,
        'recorded_at': datetime.utcnow().isoformat()
    }
    return data


@pytest.fixture
def mock_threshold_rule():
    rule = MagicMock()
    rule.id = 1
    rule.sensor_id = 1
    rule.operator = '>'
    rule.threshold_value = 30.0
    rule.actuator_id = 1
    rule.action_value = 'ON'
    rule.is_active = True
    rule.description = 'Turn on fan when temp > 30'
    rule.created_at = datetime.utcnow()
    rule.updated_at = datetime.utcnow()
    rule.evaluate.return_value = True
    rule.to_dict.return_value = {
        'id': 1,
        'sensor_id': 1,
        'operator': '>',
        'threshold_value': 30.0,
        'actuator_id': 1,
        'action_value': 'ON',
        'is_active': True
    }
    return rule


@pytest.fixture
def mock_scene():
    scene = MagicMock()
    scene.id = 1
    scene.user_id = 1
    scene.name = 'Good Night'
    scene.description = 'Turn off all lights'
    scene.is_active = True
    scene.last_triggered_at = None
    scene.conditions = []
    scene.actions = []
    scene.created_at = datetime.utcnow()
    scene.updated_at = datetime.utcnow()
    scene.evaluate_conditions.return_value = True
    scene.to_dict.return_value = {
        'id': 1,
        'user_id': 1,
        'name': 'Good Night',
        'description': 'Turn off all lights',
        'is_active': True,
        'conditions': [],
        'actions': []
    }
    return scene


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.id = 1
    session.user_id = 1
    session.session_token = 'test_token'
    session.refresh_token = 'refresh_token'
    session.expires_at = datetime.utcnow() + timedelta(days=30)
    session.is_expired = False
    return session
