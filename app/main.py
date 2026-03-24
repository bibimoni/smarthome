"""Flask application factory and main entry point."""
import os
import logging
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.config import get_config
from app.extensions import db, jwt, cors, swagger


def create_app(config_class=None):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask application instance
    """
    if config_class is None:
        config_class = get_config()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging for development
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register CLI commands
    _register_commands(app)
    
    # Create tables if not exists (for development)
    if app.config.get('DEBUG'):
        with app.app_context():
            db.create_all()
    
    return app


def _init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Initialize Swagger with custom template and config
    from app.swagger_template import SWAGGER_TEMPLATE, SWAGGER_CONFIG
    app.config['SWAGGER'] = {**SWAGGER_TEMPLATE, **SWAGGER_CONFIG}
    swagger.init_app(app)
    
    # Initialize migrate
    migrate = Migrate(app, db)
    
    # Initialize MQTT service for Adafruit IO
    from app.services.mqtt_service import init_mqtt
    init_mqtt(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expired',
            'message': 'The token has expired. Please log in again.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'The token is invalid or malformed.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'Request does not contain an access token.'
        }), 401


def _register_blueprints(app):
    """Register Flask blueprints."""
    from app.api.auth import auth_bp
    from app.api.sensors import sensors_bp
    from app.api.actuators import actuators_bp
    from app.api.scenes import scenes_bp
    from app.api.thresholds import thresholds_bp
    from app.api.logs import logs_bp
    from app.api.iot import iot_bp
    from app.api.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(sensors_bp, url_prefix='/api/sensors')
    app.register_blueprint(actuators_bp, url_prefix='/api/actuators')
    app.register_blueprint(scenes_bp, url_prefix='/api/scenes')
    app.register_blueprint(thresholds_bp, url_prefix='/api/thresholds')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(iot_bp, url_prefix='/api/iot')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'YoloHome API',
            'version': '1.0.0'
        })


def _register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403


def _register_commands(app):
    """Register custom CLI commands."""
    import click
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database with default data."""
        from app.services.device_service import DeviceService
        
        click.echo('Initializing database...')
        db.create_all()
        
        # Create default sensors and actuators
        DeviceService.create_default_devices()
        
        click.echo('Database initialized successfully!')
    
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    def create_admin(email, password):
        """Create an admin user."""
        from app.models.user import User
        
        user = User.query.filter_by(email=email).first()
        if user:
            click.echo(f'User {email} already exists!')
            return
        
        user = User(email=email)
        user.set_password(password)
        user.is_active = True
        user.is_verified = True
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Admin user {email} created successfully!')
    
    @app.cli.command('cleanup-sessions')
    def cleanup_sessions():
        """Clean up expired sessions."""
        from app.models.user import Session
        count = Session.cleanup_expired()
        click.echo(f'Cleaned up {count} expired sessions.')
    
    @app.cli.command('cleanup-logs')
    @click.option('--days', default=365, help='Days to keep')
    def cleanup_logs(days):
        """Clean up old event logs."""
        from app.models.data import EventLog
        count = EventLog.cleanup_old_logs(days)
        click.echo(f'Cleaned up {count} old event logs.')
    
    @app.cli.command('cleanup-sensor-data')
    @click.option('--days', default=90, help='Days to keep')
    def cleanup_sensor_data(days):
        """Clean up old sensor data."""
        from app.models.data import SensorData
        count = SensorData.cleanup_old_data(days)
        click.echo(f'Cleaned up {count} old sensor data records.')


# Create the application instance for WSGI servers
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)