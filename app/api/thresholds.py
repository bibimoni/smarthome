"""Threshold API endpoints.

Use Case: UC-2 Configure environmental thresholds (CRUD for rules, activate/deactivate)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.threshold_service import ThresholdService

thresholds_bp = Blueprint('thresholds', __name__)


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
    
    return jsonify({
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
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
    
    return jsonify({'rule': rule.to_dict()}), 200


@thresholds_bp.route('/<int:rule_id>/status', methods=['GET'])
@jwt_required()
def get_rule_status(rule_id):
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
    
    return jsonify({'status': status}), 200


@thresholds_bp.route('/sensor/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_rules_for_sensor(sensor_id):
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
    
    return jsonify({
        'sensor_id': sensor_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/actuator/<int:actuator_id>', methods=['GET'])
@jwt_required()
def get_rules_for_actuator(actuator_id):
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
    
    return jsonify({
        'actuator_id': actuator_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/', methods=['POST'])
@jwt_required()
def create_rule():
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
    
    rule, error = ThresholdService.create_rule(
        sensor_id=data.get('sensor_id'),
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        actuator_id=data.get('actuator_id'),
        action_value=data.get('action_value'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Rule created',
        'rule': rule.to_dict()
    }), 201


@thresholds_bp.route('/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_rule(rule_id):
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
    
    rule, error = ThresholdService.update_rule(
        rule_id=rule_id,
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        action_value=data.get('action_value'),
        description=data.get('description'),
        is_active=data.get('is_active')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Rule updated',
        'rule': rule.to_dict()
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
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


@thresholds_bp.route('/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_rule(rule_id):
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
    }), 200


@thresholds_bp.route('/<int:rule_id>/evaluate', methods=['POST'])
@jwt_required()
def evaluate_rule(rule_id):
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
    }), 200


@thresholds_bp.route('/evaluate-all', methods=['POST'])
@jwt_required()
def evaluate_all_rules():
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