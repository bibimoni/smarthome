"""IoT Gateway API endpoints.

This module provides endpoints for YoloBit devices to communicate with the backend.
It handles sensor data updates and command retrieval.
"""
from flask import Blueprint, request, jsonify
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
from app.services.mqtt_service import mqtt_service
from app.services.threshold_service import ThresholdService
from app.services.scene_service import SceneService

iot_bp = Blueprint('iot', __name__)


@iot_bp.route('/update', methods=['POST'])
def update_sensor_data():
    """
    Receive sensor data from YoloBit devices.
    
    This endpoint is called by YoloBit devices to send sensor readings.
    It also triggers threshold rule evaluation and scene checking.
    
    Request Body:
        temperature: Temperature value (°C)
        humidity: Humidity value (%)
        light: Light sensor value (0-4095)
        pir: PIR motion detection (0 or 1)
        Or any other sensor feed data
        
    Returns:
        200: Data received successfully
        400: Invalid data
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    results = []
    
    # Process each sensor feed
    for feed_key, value in data.items():
        if feed_key in ['timestamp', 'device_id']:  # Skip metadata
            continue
        
        try:
            # Try to find the sensor and record data
            sensor_data, error = DeviceService.record_sensor_data(feed_key, float(value))
            if sensor_data:
                results.append({
                    'feed': feed_key,
                    'value': value,
                    'recorded': True
                })
            else:
                results.append({
                    'feed': feed_key,
                    'value': value,
                    'recorded': False,
                    'error': error
                })
        except (ValueError, TypeError) as e:
            results.append({
                'feed': feed_key,
                'value': value,
                'recorded': False,
                'error': str(e)
            })
    
    # Evaluate threshold rules after receiving new data
    try:
        ThresholdService.evaluate_all_rules()
    except Exception as e:
        print(f"Error evaluating rules: {e}")
    
    # Check scenes
    try:
        SceneService.check_and_execute_scenes()
    except Exception as e:
        print(f"Error checking scenes: {e}")
    
    return jsonify({
        'message': 'Data received',
        'results': results
    }), 200


@iot_bp.route('/sensor/<feed_key>', methods=['POST'])
def update_single_sensor(feed_key):
    """
    Update a single sensor value.
    
    Args:
        feed_key: Sensor feed key
        
    Request Body:
        value: Sensor value
        
    Returns:
        200: Data recorded
        400: Invalid data
        404: Sensor not found
    """
    data = request.get_json()
    
    if not data or 'value' not in data:
        return jsonify({'error': 'Value is required'}), 400
    
    try:
        value = float(data['value'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid value'}), 400
    
    sensor_data, error = DeviceService.record_sensor_data(feed_key, value)
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    # Evaluate rules for this sensor
    from app.models.device import Sensor
    sensor = Sensor.query.filter_by(feed_key=feed_key).first()
    if sensor:
        try:
            ThresholdService.evaluate_all_rules()
            SceneService.check_and_execute_scenes()
        except Exception as e:
            print(f"Error evaluating: {e}")
    
    return jsonify({
        'message': 'Data recorded',
        'feed_key': feed_key,
        'value': value
    }), 200


@iot_bp.route('/commands', methods=['GET'])
def get_commands():
    """
    Get queued commands for YoloBit devices.
    
    Devices can poll this endpoint to get commands to execute.
    Commands are cleared after being retrieved.
    
    Returns:
        200: List of commands
    """
    if mqtt_service:
        commands = mqtt_service.get_commands()
    else:
        commands = []
    
    return jsonify({
        'commands': commands,
        'count': len(commands)
    }), 200


@iot_bp.route('/command', methods=['POST'])
def queue_command():
    """
    Queue a command for a device.
    
    Request Body:
        command: Command type (e.g., FAN_ON, LED_OFF)
        value: Command value
        
    Returns:
        200: Command queued
        400: Invalid data
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    command = data.get('command')
    value = data.get('value')
    
    if not command:
        return jsonify({'error': 'Command is required'}), 400
    
    if mqtt_service:
        mqtt_service.queue_command(command, value)
    
    return jsonify({
        'message': 'Command queued',
        'command': command,
        'value': value
    }), 200


@iot_bp.route('/status', methods=['GET'])
def get_device_status():
    """
    Get overall device status for the IoT system.
    
    Returns:
        200: Device status summary
    """
    status = DeviceService.get_device_status()
    
    # Add MQTT connection status
    status['mqtt_connected'] = mqtt_service.connected if mqtt_service else False
    
    return jsonify(status), 200


@iot_bp.route('/control', methods=['POST'])
def control_device():
    """
    Control a device directly via feed key.
    Used by external systems or the Adafruit dashboard.
    
    Request Body:
        feed_key: Actuator feed key
        action: Action to perform (ON, OFF, or value)
        
    Returns:
        200: Command sent
        400: Invalid data
        404: Actuator not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    feed_key = data.get('feed_key')
    action = data.get('action')
    
    if not feed_key or not action:
        return jsonify({'error': 'feed_key and action are required'}), 400
    
    # Find actuator
    from app.models.device import Actuator
    actuator = Actuator.query.filter_by(feed_key=feed_key).first()
    
    if not actuator:
        return jsonify({'error': 'Actuator not found'}), 404
    
    # Send command via MQTT
    if mqtt_service:
        success = mqtt_service.publish_actuator_command(feed_key, action)
        if not success:
            return jsonify({'error': 'Failed to send command'}), 500
    else:
        return jsonify({'error': 'MQTT not connected'}), 503
    
    # Update actuator state
    actuator.current_value = action
    from app.extensions import db
    db.session.commit()
    
    return jsonify({
        'message': 'Command sent',
        'feed_key': feed_key,
        'action': action
    }), 200


@iot_bp.route('/sync', methods=['POST'])
def sync_device():
    """
    Sync device state with backend.
    Used when a device comes online and wants to sync its state.
    
    Request Body:
        device_id: Optional device identifier
        sensors: Dict of sensor feed_key: value
        actuators: Dict of actuator feed_key: current_value
        
    Returns:
        200: Sync complete with desired states
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Process sensor updates
    sensors = data.get('sensors', {})
    for feed_key, value in sensors.items():
        try:
            DeviceService.record_sensor_data(feed_key, float(value))
        except (ValueError, TypeError):
            pass
    
    # Get current actuator states to return
    from app.models.device import Actuator
    actuators = Actuator.query.filter_by(is_active=True).all()
    
    desired_states = {}
    for actuator in actuators:
        desired_states[actuator.feed_key] = {
            'value': actuator.current_value,
            'mode': actuator.mode
        }
    
    return jsonify({
        'message': 'Sync complete',
        'desired_states': desired_states,
        'mqtt_connected': mqtt_service.connected if mqtt_service else False
    }), 200


@iot_bp.route('/webhook/adafruit', methods=['POST'])
def adafruit_webhook():
    """
    Webhook endpoint for Adafruit IO.
    Receives data from Adafruit when feed values change.
    
    Request Body (from Adafruit):
        value: New feed value
        feed_id: Feed ID
        created_at: Timestamp
        
    Returns:
        200: Webhook received
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract feed information
    feed_key = data.get('feed_id') or data.get('name')
    value = data.get('value')
    
    if not feed_key or value is None:
        return jsonify({'error': 'Invalid webhook data'}), 400
    
    # Try to record as sensor data
    try:
        DeviceService.record_sensor_data(feed_key, float(value))
    except (ValueError, TypeError):
        pass
    
    # Try to update actuator state
    from app.models.device import Actuator
    actuator = Actuator.query.filter_by(feed_key=feed_key).first()
    if actuator:
        actuator.current_value = str(value)
        from app.extensions import db
        db.session.commit()
    
    return jsonify({'message': 'Webhook received'}), 200