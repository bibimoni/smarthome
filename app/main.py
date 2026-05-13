
import os
import logging
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.config import get_config
from app.extensions import db, jwt, cors, swagger


def create_app(config_class=None):


    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")

    _init_extensions(app)

    _register_blueprints(app)

    _register_error_handlers(app)

    _register_commands(app)

    if app.config.get('DEBUG'):
        with app.app_context():
            db.create_all()

    return app


def _init_extensions(app):

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    from app.swagger_template import SWAGGER_TEMPLATE, SWAGGER_CONFIG
    app.config['SWAGGER'] = {**SWAGGER_TEMPLATE, **SWAGGER_CONFIG}
    swagger.init_app(app)

    migrate = Migrate(app, db)

    from app.services.mqtt_service import init_mqtt
    init_mqtt(app)

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

    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'YoloHome API',
            'version': '1.0.0'
        })


def _register_error_handlers(app):


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

    import click

    @app.cli.command('init-db')
    def init_db():

        from app.services.device_service import DeviceService
        from app.models.user import User

        click.echo('Initializing database...')
        db.create_all()


        demo_email = 'demo@yolohome.com'
        demo_user = User.query.filter_by(email=demo_email).first()
        if not demo_user:
            demo_user = User(
                email=demo_email,
                first_name='Demo',
                last_name='User',
                is_active=True,
                is_verified=True
            )
            demo_user.set_password('demo1234')
            db.session.add(demo_user)
            db.session.commit()
            click.echo(f'Created demo user: {demo_email}')

        DeviceService.create_default_devices(user_id=demo_user.id)

        click.echo('Database initialized successfully!')

    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    def create_admin(email, password):

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

        from app.models.user import Session
        count = Session.cleanup_expired()
        click.echo(f'Cleaned up {count} expired sessions.')

    @app.cli.command('cleanup-logs')
    @click.option('--days', default=365, help='Days to keep')
    def cleanup_logs(days):

        from app.models.data import EventLog
        count = EventLog.cleanup_old_logs(days)
        click.echo(f'Cleaned up {count} old event logs.')

    @app.cli.command('cleanup-sensor-data')
    @click.option('--days', default=90, help='Days to keep')
    def cleanup_sensor_data(days):

        from app.models.data import SensorData
        count = SensorData.cleanup_old_data(days)
        click.echo(f'Cleaned up {count} old sensor data records.')


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
