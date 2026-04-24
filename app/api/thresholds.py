"""Threshold API endpoints.

Use Case: UC-2 Configure environmental thresholds (CRUD for rules, activate/deactivate)
"""
<<<<<<< HEAD
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
=======
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
from app.services.threshold_service import ThresholdService

thresholds_bp = Blueprint('thresholds', __name__)


<<<<<<< HEAD
@thresholds_bp.route('/', methods=['GET'])
@jwt_required()
def get_rules():
    """
    Get all threshold rules.
    
    UC-2: Configure environmental thresholds
    ---
    tags:
      - Thresholds
    summary: Get all threshold rules
    security:
      - Bearer: []
    parameters:
      - name: is_active
        in: query
        type: boolean
        required: false
        description: Filter by active status
    responses:
      200:
        description: List of threshold rules
        schema:
          type: object
          properties:
            rules:
              type: array
              items:
                $ref: "#/definitions/ThresholdRule"
            count:
              type: integer
    """
    is_active = request.args.get('is_active')
    if is_active is not None:
        is_active = is_active.lower() == 'true'
    
    rules = ThresholdService.get_all_rules(is_active)
    
=======
def _error_response(error: dict, default_status: int = 400):
    status_map = {
        'RULE_NOT_FOUND': 404,
        'SENSOR_NOT_FOUND': 404,
        'ACTUATOR_NOT_FOUND': 404,
        'RULE_CONFLICT': 409,
        'VALIDATION_ERROR': 400,
        'SENSOR_INACTIVE': 400,
        'ACTUATOR_INACTIVE': 400,
    }
    status_code = status_map.get(error.get('code'), default_status)
    payload = {
        'error': error.get('message', 'Unknown error'),
        'code': error.get('code', 'UNKNOWN_ERROR'),
    }
    if error.get('details'):
        payload['details'] = error['details']
    return jsonify(payload), status_code


@thresholds_bp.route('/', methods=['GET'])
@jwt_required()
def get_rules():
    is_active = request.args.get('is_active')
    if is_active is not None:
        is_active = is_active.lower() == 'true'

    rules = ThresholdService.get_all_rules(is_active)
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    return jsonify({
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
<<<<<<< HEAD
    """
    Get a specific threshold rule.
    
    ---
    tags:
      - Thresholds
    summary: Get rule by ID
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Rule details
        schema:
          type: object
          properties:
            rule:
              $ref: "#/definitions/ThresholdRule"
      404:
        description: Rule not found
        schema:
          $ref: "#/definitions/Error"
    """
    rule = ThresholdService.get_rule_by_id(rule_id)
    
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
    
=======
    rule = ThresholdService.get_rule_by_id(rule_id)
    if not rule:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    return jsonify({'rule': rule.to_dict()}), 200


@thresholds_bp.route('/<int:rule_id>/status', methods=['GET'])
@jwt_required()
def get_rule_status(rule_id):
<<<<<<< HEAD
    """
    Get status of a threshold rule including current evaluation.
    
    ---
    tags:
      - Thresholds
    summary: Get rule status
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Rule status
        schema:
          type: object
          properties:
            status:
              type: object
      404:
        description: Rule not found
        schema:
          $ref: "#/definitions/Error"
    """
    status = ThresholdService.get_rule_status(rule_id)
    
    if not status:
        return jsonify({'error': 'Rule not found'}), 404
    
=======
    status = ThresholdService.get_rule_status(rule_id)
    if not status:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    return jsonify({'status': status}), 200


@thresholds_bp.route('/sensor/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_rules_for_sensor(sensor_id):
<<<<<<< HEAD
    """
    Get all rules for a specific sensor.
    
    ---
    tags:
      - Thresholds
    summary: Get rules by sensor ID
    security:
      - Bearer: []
    parameters:
      - name: sensor_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of rules for sensor
        schema:
          type: object
          properties:
            sensor_id:
              type: integer
            rules:
              type: array
              items:
                $ref: "#/definitions/ThresholdRule"
            count:
              type: integer
    """
    rules = ThresholdService.get_rules_for_sensor(sensor_id)
    
=======
    rules = ThresholdService.get_rules_for_sensor(sensor_id)
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    return jsonify({
        'sensor_id': sensor_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/actuator/<int:actuator_id>', methods=['GET'])
@jwt_required()
def get_rules_for_actuator(actuator_id):
<<<<<<< HEAD
    """
    Get all rules controlling a specific actuator.
    
    ---
    tags:
      - Thresholds
    summary: Get rules by actuator ID
    security:
      - Bearer: []
    parameters:
      - name: actuator_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of rules for actuator
        schema:
          type: object
          properties:
            actuator_id:
              type: integer
            rules:
              type: array
              items:
                $ref: "#/definitions/ThresholdRule"
            count:
              type: integer
    """
    rules = ThresholdService.get_rules_for_actuator(actuator_id)
    
=======
    rules = ThresholdService.get_rules_for_actuator(actuator_id)
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    return jsonify({
        'actuator_id': actuator_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/', methods=['POST'])
@jwt_required()
def create_rule():
<<<<<<< HEAD
    """
    Create a new threshold rule.
    
    UC-2: Configure environmental thresholds
    ---
    tags:
      - Thresholds
    summary: Create a new threshold rule
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - sensor_id
            - operator
            - threshold_value
            - actuator_id
            - action_value
          properties:
            sensor_id:
              type: integer
              example: 1
            operator:
              type: string
              enum: [greater_than, less_than, equals]
              example: "greater_than"
            threshold_value:
              type: number
              example: 30.0
            actuator_id:
              type: integer
              example: 1
            action_value:
              type: string
              example: "75"
            description:
              type: string
              example: "Turn on fan when temp exceeds 30C"
    responses:
      201:
        description: Rule created
        schema:
          type: object
          properties:
            message:
              type: string
            rule:
              $ref: "#/definitions/ThresholdRule"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
=======
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return _error_response({'code': 'VALIDATION_ERROR', 'message': 'Không có dữ liệu gửi lên.'})

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    rule, error = ThresholdService.create_rule(
        sensor_id=data.get('sensor_id'),
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        actuator_id=data.get('actuator_id'),
        action_value=data.get('action_value'),
<<<<<<< HEAD
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Rule created',
        'rule': rule.to_dict()
=======
        description=data.get('description'),
        user_id=user_id,
    )
    if error:
        return _error_response(error)

    return jsonify({
        'message': 'Thiết lập ngưỡng thành công.',
        'rule': rule.to_dict(),
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    }), 201


@thresholds_bp.route('/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_rule(rule_id):
<<<<<<< HEAD
    """
    Update a threshold rule.
    
    UC-2: Configure environmental thresholds
    ---
    tags:
      - Thresholds
    summary: Update a threshold rule
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            operator:
              type: string
              enum: [greater_than, less_than, equals]
            threshold_value:
              type: number
            action_value:
              type: string
            description:
              type: string
            is_active:
              type: boolean
    responses:
      200:
        description: Rule updated
        schema:
          type: object
          properties:
            message:
              type: string
            rule:
              $ref: "#/definitions/ThresholdRule"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
      404:
        description: Rule not found
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
=======
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return _error_response({'code': 'VALIDATION_ERROR', 'message': 'Không có dữ liệu gửi lên.'})

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    rule, error = ThresholdService.update_rule(
        rule_id=rule_id,
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        action_value=data.get('action_value'),
        description=data.get('description'),
<<<<<<< HEAD
        is_active=data.get('is_active')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Rule updated',
        'rule': rule.to_dict()
=======
        is_active=data.get('is_active'),
        user_id=user_id,
    )
    if error:
        return _error_response(error)

    return jsonify({
        'message': 'Cập nhật ngưỡng thành công.',
        'rule': rule.to_dict(),
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
<<<<<<< HEAD
    """
    Delete a threshold rule.
    
    UC-2: Configure environmental thresholds
    ---
    tags:
      - Thresholds
    summary: Delete a threshold rule
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Rule deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Rule not found
        schema:
          $ref: "#/definitions/Error"
    """
    success, error = ThresholdService.delete_rule(rule_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Rule deleted'}), 200
=======
    user_id = get_jwt_identity()
    success, error = ThresholdService.delete_rule(rule_id, user_id=user_id)
    if error:
        return _error_response(error)
    return jsonify({'message': 'Xóa rule thành công.', 'success': success}), 200
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f


@thresholds_bp.route('/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_rule(rule_id):
<<<<<<< HEAD
    """
    Toggle a rule active/inactive.
    
    UC-2: Configure environmental thresholds (activate/deactivate)
    ---
    tags:
      - Thresholds
    summary: Toggle rule active/inactive
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Rule toggled
        schema:
          type: object
          properties:
            message:
              type: string
            rule:
              $ref: "#/definitions/ThresholdRule"
      404:
        description: Rule not found
        schema:
          $ref: "#/definitions/Error"
    """
    rule, error = ThresholdService.toggle_rule(rule_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({
        'message': f'Rule {"activated" if rule.is_active else "deactivated"}',
        'rule': rule.to_dict()
=======
    user_id = get_jwt_identity()
    rule, error = ThresholdService.toggle_rule(rule_id, user_id=user_id)
    if error:
        return _error_response(error)
    return jsonify({
        'message': f"Rule đã được {'kích hoạt' if rule.is_active else 'vô hiệu hóa'}.",
        'rule': rule.to_dict(),
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    }), 200


@thresholds_bp.route('/<int:rule_id>/evaluate', methods=['POST'])
@jwt_required()
def evaluate_rule(rule_id):
<<<<<<< HEAD
    """
    Evaluate a rule against current sensor value.
    
    ---
    tags:
      - Thresholds
    summary: Evaluate a rule
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Evaluation result
        schema:
          type: object
          properties:
            rule_id:
              type: integer
            condition_met:
              type: boolean
            action:
              type: string
    """
    condition_met, action = ThresholdService.evaluate_rule(rule_id)
    
    return jsonify({
        'rule_id': rule_id,
        'condition_met': condition_met,
        'action': action
=======
    rule = ThresholdService.get_rule_by_id(rule_id)
    if not rule:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)

    condition_met, action = ThresholdService.evaluate_rule(rule_id)
    status = ThresholdService.get_rule_status(rule_id)
    return jsonify({
        'message': 'Đánh giá rule thành công.',
        'rule_id': rule_id,
        'condition_met': condition_met,
        'action': action,
        'status': status,
    }), 200


@thresholds_bp.route('/<int:rule_id>/execute', methods=['POST'])
@jwt_required()
def execute_rule(rule_id):
    rule = ThresholdService.get_rule_by_id(rule_id)
    if not rule:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)

    executed, message = ThresholdService.evaluate_and_execute(rule_id)
    return jsonify({
        'message': message,
        'rule_id': rule_id,
        'executed': executed,
        'status': ThresholdService.get_rule_status(rule_id),
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
    }), 200


@thresholds_bp.route('/evaluate-all', methods=['POST'])
@jwt_required()
def evaluate_all_rules():
<<<<<<< HEAD
    """
    Evaluate all active rules and execute actions where conditions are met.
    
    ---
    tags:
      - Thresholds
    summary: Evaluate all rules
    security:
      - Bearer: []
    responses:
      200:
        description: Evaluation results
        schema:
          type: object
          properties:
            message:
              type: string
            results:
              type: array
              items:
                type: object
    """
    results = ThresholdService.evaluate_all_rules()
    
    return jsonify({
        'message': 'All rules evaluated',
        'results': results
    }), 200
=======
    results = ThresholdService.evaluate_all_rules()
    return jsonify({
        'message': 'Đã đánh giá tất cả rule active.',
        'results': results,
        'summary': {
            'executed': len(results.get('executed', [])),
            'skipped': len(results.get('skipped', [])),
            'errors': len(results.get('errors', [])),
        }
    }), 200
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
