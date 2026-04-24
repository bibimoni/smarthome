"""Threshold API endpoints.

Use Case: UC-2 Configure environmental thresholds (CRUD for rules, activate/deactivate)
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.threshold_service import ThresholdService

thresholds_bp = Blueprint('thresholds', __name__)


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
    return jsonify({
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
    rule = ThresholdService.get_rule_by_id(rule_id)
    if not rule:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)
    return jsonify({'rule': rule.to_dict()}), 200


@thresholds_bp.route('/<int:rule_id>/status', methods=['GET'])
@jwt_required()
def get_rule_status(rule_id):
    status = ThresholdService.get_rule_status(rule_id)
    if not status:
        return _error_response({'code': 'RULE_NOT_FOUND', 'message': 'Không tìm thấy rule.'}, 404)
    return jsonify({'status': status}), 200


@thresholds_bp.route('/sensor/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_rules_for_sensor(sensor_id):
    rules = ThresholdService.get_rules_for_sensor(sensor_id)
    return jsonify({
        'sensor_id': sensor_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/actuator/<int:actuator_id>', methods=['GET'])
@jwt_required()
def get_rules_for_actuator(actuator_id):
    rules = ThresholdService.get_rules_for_actuator(actuator_id)
    return jsonify({
        'actuator_id': actuator_id,
        'rules': [r.to_dict() for r in rules],
        'count': len(rules)
    }), 200


@thresholds_bp.route('/', methods=['POST'])
@jwt_required()
def create_rule():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return _error_response({'code': 'VALIDATION_ERROR', 'message': 'Không có dữ liệu gửi lên.'})

    rule, error = ThresholdService.create_rule(
        sensor_id=data.get('sensor_id'),
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        actuator_id=data.get('actuator_id'),
        action_value=data.get('action_value'),
        description=data.get('description'),
        user_id=user_id,
    )
    if error:
        return _error_response(error)

    return jsonify({
        'message': 'Thiết lập ngưỡng thành công.',
        'rule': rule.to_dict(),
    }), 201


@thresholds_bp.route('/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_rule(rule_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return _error_response({'code': 'VALIDATION_ERROR', 'message': 'Không có dữ liệu gửi lên.'})

    rule, error = ThresholdService.update_rule(
        rule_id=rule_id,
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value'),
        action_value=data.get('action_value'),
        description=data.get('description'),
        is_active=data.get('is_active'),
        user_id=user_id,
    )
    if error:
        return _error_response(error)

    return jsonify({
        'message': 'Cập nhật ngưỡng thành công.',
        'rule': rule.to_dict(),
    }), 200


@thresholds_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    user_id = get_jwt_identity()
    success, error = ThresholdService.delete_rule(rule_id, user_id=user_id)
    if error:
        return _error_response(error)
    return jsonify({'message': 'Xóa rule thành công.', 'success': success}), 200


@thresholds_bp.route('/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_rule(rule_id):
    user_id = get_jwt_identity()
    rule, error = ThresholdService.toggle_rule(rule_id, user_id=user_id)
    if error:
        return _error_response(error)
    return jsonify({
        'message': f"Rule đã được {'kích hoạt' if rule.is_active else 'vô hiệu hóa'}.",
        'rule': rule.to_dict(),
    }), 200


@thresholds_bp.route('/<int:rule_id>/evaluate', methods=['POST'])
@jwt_required()
def evaluate_rule(rule_id):
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
    }), 200


@thresholds_bp.route('/evaluate-all', methods=['POST'])
@jwt_required()
def evaluate_all_rules():
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