"""Actuator API endpoints.

Use Cases:
- UC-3: Manual device control with AUTO/MANUAL mode override
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.actuator_service import ActuatorService
from app.services.device_service import DeviceService

actuators_bp = Blueprint('actuators', __name__)


@actuators_bp.route('/', methods=['GET'])
@jwt_required()
def get_actuators():
    """
    Get all actuators.
    
    UC-3: Manual device control
    ---
    tags:
      - Actuators
    summary: Get all actuators
    description: Retrieve a list of all actuators in the system
    security:
      - Bearer: []
    responses:
      200:
        description: List of actuators
        schema:
          type: object
          properties:
            actuators:
              type: array
              items:
                $ref: "#/definitions/Actuator"
            count:
              type: integer
              example: 3
    """
    actuators = DeviceService.get_all_actuators()
    return jsonify({
        'actuators': [a.to_dict() for a in actuators],
        'count': len(actuators)
    }), 200


@actuators_bp.route('/<int:actuator_id>', methods=['GET'])
@jwt_required()
def get_actuator(actuator_id):
    """
    Get a specific actuator.
    
    ---
    tags:
      - Actuators
    summary: Get actuator by ID
    security:
      - Bearer: []
    parameters:
      - name: actuator_id
        in: path
        type: integer
        required: true
        description: Actuator ID
    responses:
      200:
        description: Actuator details
        schema:
          type: object
          properties:
            actuator:
              $ref: "#/definitions/Actuator"
      404:
        description: Actuator not found
        schema:
          $ref: "#/definitions/Error"
    """
    actuator = DeviceService.get_actuator_by_id(actuator_id)
    if not actuator:
        return jsonify({'error': 'Actuator not found'}), 404
    
    return jsonify({'actuator': actuator.to_dict()}), 200


@actuators_bp.route('/status', methods=['GET'])
@jwt_required()
def get_all_status():
    """
    Get status of all actuators.
    
    ---
    tags:
      - Actuators
    summary: Get all actuator statuses
    security:
      - Bearer: []
    responses:
      200:
        description: List of actuator statuses
        schema:
          type: object
          properties:
            actuators:
              type: array
              items:
                type: object
            count:
              type: integer
    """
    statuses = ActuatorService.get_all_actuator_statuses()
    return jsonify({
        'actuators': statuses,
        'count': len(statuses)
    }), 200


@actuators_bp.route('/<int:actuator_id>/status', methods=['GET'])
@jwt_required()
def get_status(actuator_id):
    """
    Get status of a specific actuator.
    
    ---
    tags:
      - Actuators
    summary: Get actuator status
    security:
      - Bearer: []
    parameters:
      - name: actuator_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Actuator status
        schema:
          type: object
          properties:
            status:
              type: object
      404:
        description: Actuator not found
        schema:
          $ref: "#/definitions/Error"
    """
    status = ActuatorService.get_actuator_status(actuator_id)
    if not status:
        return jsonify({'error': 'Actuator not found'}), 404
    
    return jsonify({'status': status}), 200


@actuators_bp.route('/<int:actuator_id>/control', methods=['POST'])
@jwt_required()
def control_actuator(actuator_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    action = str(data.get('action', '')).upper().strip()
    manual_override = bool(data.get('manual_override', True))
    auto_switch_to_manual = bool(data.get('auto_switch_to_manual', False))

    if not action:
        return jsonify({'error': 'Action is required'}), 400

    success, error, result = ActuatorService.control_actuator(
        actuator_id=actuator_id,
        action=action,
        user_id=user_id,
        manual_override=manual_override,
        auto_switch_to_manual=auto_switch_to_manual,
    )

    if error:
        status_code = 404 if 'not found' in error.lower() else 400
        return jsonify({'error': error}), status_code

    return jsonify({
        'message': f'Actuator set to {action}',
        'actuator_id': actuator_id,
        'action': action,
        'result': result,
    }), 200


@actuators_bp.route('/<int:actuator_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_actuator(actuator_id):
    user_id = get_jwt_identity()
    success, error, result = ActuatorService.toggle_actuator(actuator_id, user_id)

    if error:
        return jsonify({'error': error}), 404 if 'not found' in error.lower() else 400

    return jsonify({
        'message': 'Actuator toggled',
        'actuator_id': actuator_id,
        'result': result,
    }), 200

@actuators_bp.route('/<int:actuator_id>/mode', methods=['POST'])
@jwt_required()
def set_mode(actuator_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    mode = str(data.get('mode', '')).upper().strip()
    if not mode:
        return jsonify({'error': 'Mode is required'}), 400

    success, error, result = ActuatorService.set_actuator_mode(actuator_id, mode, user_id)

    if error:
        return jsonify({'error': error}), 404 if 'not found' in error.lower() else 400

    return jsonify({
        'message': f'Mode set to {mode}',
        'actuator_id': actuator_id,
        'mode': mode,
        'result': result,
    }), 200

@actuators_bp.route('/<int:actuator_id>/value', methods=['POST'])
@jwt_required()
def set_value(actuator_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    value = data.get('value')
    if value is None:
        return jsonify({'error': 'Value is required'}), 400

    success, error, result = ActuatorService.set_actuator_value(actuator_id, str(value), user_id)

    if error:
        return jsonify({'error': error}), 404 if 'not found' in error.lower() else 400

    return jsonify({
        'message': f'Actuator value set to {value}',
        'actuator_id': actuator_id,
        'value': value,
        'result': result,
    }), 200


@actuators_bp.route('/', methods=['POST'])
@jwt_required()
def create_actuator():
    """
    Create a new actuator.
    
    Request Body:
        name: Actuator name
        type: Actuator type (fan, led, rgb, servo, lcd)
        feed_key: Adafruit feed key
        description: Optional description
        
    Returns:
        201: Actuator created
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    actuator, error = DeviceService.create_actuator(
        name=data.get('name'),
        actuator_type=data.get('type'),
        feed_key=data.get('feed_key'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Actuator created',
        'actuator': actuator.to_dict()
    }), 201


@actuators_bp.route('/<int:actuator_id>', methods=['PUT'])
@jwt_required()
def update_actuator(actuator_id):
    """
    Update an actuator.
    
    Request Body:
        name: New name
        description: New description
        
    Returns:
        200: Actuator updated
        404: Actuator not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    actuator, error = DeviceService.update_actuator(
        actuator_id=actuator_id,
        name=data.get('name'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({
        'message': 'Actuator updated',
        'actuator': actuator.to_dict()
    }), 200


@actuators_bp.route('/<int:actuator_id>', methods=['DELETE'])
@jwt_required()
def delete_actuator(actuator_id):
    """
    Delete an actuator.
    
    Returns:
        200: Actuator deleted
        404: Actuator not found
    """
    success, error = DeviceService.delete_actuator(actuator_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Actuator deleted'}), 200