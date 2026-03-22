"""Sensor API endpoints.

Use Case: UC-1 Real-time environment monitoring
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.sensor_service import SensorService
from app.services.device_service import DeviceService

sensors_bp = Blueprint('sensors', __name__)


@sensors_bp.route('/', methods=['GET'])
@jwt_required()
def get_sensors():
    """
    Get all sensors.
    
    UC-1: Real-time environment monitoring
    ---
    tags:
      - Sensors
    summary: Get all sensors
    description: Retrieve a list of all active sensors in the system
    security:
      - Bearer: []
    responses:
      200:
        description: List of sensors
        schema:
          type: object
          properties:
            sensors:
              type: array
              items:
                $ref: "#/definitions/Sensor"
            count:
              type: integer
              example: 3
    """
    sensors = DeviceService.get_all_sensors()
    return jsonify({
        'sensors': [s.to_dict() for s in sensors],
        'count': len(sensors)
    }), 200


@sensors_bp.route('/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_sensor(sensor_id):
    """
    Get a specific sensor.
    
    ---
    tags:
      - Sensors
    summary: Get sensor by ID
    security:
      - Bearer: []
    parameters:
      - name: sensor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Sensor details
        schema:
          type: object
          properties:
            sensor:
              $ref: "#/definitions/Sensor"
      404:
        description: Sensor not found
        schema:
          $ref: "#/definitions/Error"
    """
    sensor = DeviceService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({'error': 'Sensor not found'}), 404
    
    return jsonify({'sensor': sensor.to_dict()}), 200


@sensors_bp.route('/readings', methods=['GET'])
@jwt_required()
def get_current_readings():
    """
    Get current readings from all sensors.
    
    UC-1: Real-time environment monitoring
    ---
    tags:
      - Sensors
    summary: Get current readings
    security:
      - Bearer: []
    responses:
      200:
        description: Current sensor readings
        schema:
          type: object
          properties:
            readings:
              type: array
              items:
                type: object
            timestamp:
              type: string
              format: date-time
    """
    readings = SensorService.get_current_readings()
    return jsonify({
        'readings': readings,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@sensors_bp.route('/<int:sensor_id>/data', methods=['GET'])
@jwt_required()
def get_sensor_data(sensor_id):
    """
    Get historical data for a sensor.
    
    UC-1: Real-time environment monitoring (history)
    ---
    tags:
      - Sensors
    summary: Get sensor data history
    security:
      - Bearer: []
    parameters:
      - name: sensor_id
        in: path
        type: integer
        required: true
      - name: hours
        in: query
        type: integer
        default: 24
        description: Hours to look back
      - name: start
        in: query
        type: string
        format: date-time
      - name: end
        in: query
        type: string
        format: date-time
    responses:
      200:
        description: Sensor data
        schema:
          type: object
          properties:
            sensor:
              $ref: "#/definitions/Sensor"
            data:
              type: array
              items:
                $ref: "#/definitions/SensorData"
            count:
              type: integer
      404:
        description: Sensor not found
        schema:
          $ref: "#/definitions/Error"
    """
    sensor = DeviceService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({'error': 'Sensor not found'}), 404
    
    # Parse query parameters
    hours = request.args.get('hours', 24, type=int)
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if start_str and end_str:
        try:
            start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            data = SensorService.get_sensor_data_range(sensor_id, start_time, end_time)
        except ValueError:
            return jsonify({'error': 'Invalid datetime format'}), 400
    else:
        data = SensorService.get_sensor_data_history(sensor_id, hours)
    
    return jsonify({
        'sensor': sensor.to_dict(),
        'data': [d.to_dict() for d in data],
        'count': len(data)
    }), 200


@sensors_bp.route('/<int:sensor_id>/statistics', methods=['GET'])
@jwt_required()
def get_sensor_statistics(sensor_id):
    """
    Get statistics for a sensor.
    
    ---
    tags:
      - Sensors
    summary: Get sensor statistics
    security:
      - Bearer: []
    parameters:
      - name: sensor_id
        in: path
        type: integer
        required: true
      - name: hours
        in: query
        type: integer
        default: 24
    responses:
      200:
        description: Sensor statistics
        schema:
          type: object
          properties:
            sensor_id:
              type: integer
            sensor_name:
              type: string
            period_hours:
              type: integer
            statistics:
              type: object
      404:
        description: Sensor not found
        schema:
          $ref: "#/definitions/Error"
    """
    sensor = DeviceService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({'error': 'Sensor not found'}), 404
    
    hours = request.args.get('hours', 24, type=int)
    stats = SensorService.get_sensor_statistics(sensor_id, hours)
    
    return jsonify({
        'sensor_id': sensor_id,
        'sensor_name': sensor.name,
        'period_hours': hours,
        'statistics': stats
    }), 200


@sensors_bp.route('/<int:sensor_id>/latest', methods=['GET'])
@jwt_required()
def get_latest_reading(sensor_id):
    """
    Get the latest reading for a sensor.
    
    ---
    tags:
      - Sensors
    summary: Get latest sensor reading
    security:
      - Bearer: []
    parameters:
      - name: sensor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Latest sensor data
        schema:
          type: object
          properties:
            sensor:
              $ref: "#/definitions/Sensor"
            latest_data:
              $ref: "#/definitions/SensorData"
      404:
        description: Sensor not found
        schema:
          $ref: "#/definitions/Error"
    """
    sensor = DeviceService.get_sensor_by_id(sensor_id)
    if not sensor:
        return jsonify({'error': 'Sensor not found'}), 404
    
    latest = SensorService.get_latest_sensor_data(sensor_id)
    
    return jsonify({
        'sensor': sensor.to_dict(),
        'latest_data': latest.to_dict() if latest else None
    }), 200


@sensors_bp.route('/', methods=['POST'])
@jwt_required()
def create_sensor():
    """
    Create a new sensor.
    
    ---
    tags:
      - Sensors
    summary: Create a new sensor
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - type
          properties:
            name:
              type: string
              example: "Living Room Temperature"
            type:
              type: string
              enum: [temperature, humidity, light, pir]
            unit:
              type: string
              example: "°C"
            min_value:
              type: number
            max_value:
              type: number
            location:
              type: string
            description:
              type: string
    responses:
      201:
        description: Sensor created
        schema:
          type: object
          properties:
            message:
              type: string
            sensor:
              $ref: "#/definitions/Sensor"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    sensor, error = DeviceService.create_sensor(
        name=data.get('name'),
        sensor_type=data.get('type'),
        feed_key=data.get('feed_key'),
        unit=data.get('unit'),
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Sensor created',
        'sensor': sensor.to_dict()
    }), 201


@sensors_bp.route('/<int:sensor_id>', methods=['PUT'])
@jwt_required()
def update_sensor(sensor_id):
    """
    Update a sensor.
    
    Request Body:
        name: New name
        unit: New unit
        min_value: New minimum value
        max_value: New maximum value
        description: New description
        
    Returns:
        200: Sensor updated
        400: Validation error
        404: Sensor not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    sensor, error = DeviceService.update_sensor(
        sensor_id=sensor_id,
        name=data.get('name'),
        unit=data.get('unit'),
        min_value=data.get('min_value'),
        max_value=data.get('max_value'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Sensor updated',
        'sensor': sensor.to_dict()
    }), 200


@sensors_bp.route('/<int:sensor_id>', methods=['DELETE'])
@jwt_required()
def delete_sensor(sensor_id):
    """
    Delete a sensor.
    
    Returns:
        200: Sensor deleted
        404: Sensor not found
    """
    success, error = DeviceService.delete_sensor(sensor_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Sensor deleted'}), 200