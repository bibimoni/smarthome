"""Health check endpoints for Docker and monitoring."""

from flask import Blueprint, jsonify, current_app
from app.extensions import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Docker and monitoring.
    
    ---
    tags:
      - Health
    summary: Health check
    description: Check the health status of all services
    security: []
    responses:
      200:
        description: System is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            services:
              type: object
              properties:
                database:
                  type: string
                mqtt:
                  type: string
            version:
              type: string
            environment:
              type: string
      503:
        description: System is unhealthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: "unhealthy"
            services:
              type: object
    """
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check MQTT connection
    try:
        from app.services.mqtt_service import MQTTService
        mqtt = MQTTService.get_instance()
        if mqtt and mqtt.is_connected():
            health_status['services']['mqtt'] = 'healthy'
        else:
            health_status['services']['mqtt'] = 'disconnected'
            # Don't mark as unhealthy since MQTT might reconnect
    except Exception as e:
        health_status['services']['mqtt'] = f'error: {str(e)}'
    
    # Add version info
    health_status['version'] = '1.0.0'
    health_status['environment'] = current_app.config.get('ENV', 'development')
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint for Kubernetes/Docker.
    
    Returns:
        200 if service is ready to accept traffic
    """
    try:
        # Check database is ready
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503