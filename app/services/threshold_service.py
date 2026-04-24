"""Threshold service for automation rules management."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.extensions import db
from app.models.automation import ThresholdRule
from app.models.device import Actuator, Sensor, normalize_actuator_name, normalize_sensor_name
from app.models.data import EventLog
from app.services.mqtt_service import mqtt_service


class ThresholdService:
    """Service class for threshold rule management."""

    @staticmethod
    def _error(code: str, message: str, details: dict | None = None) -> dict:
        return {
            'code': code,
            'message': message,
            'details': details or {},
        }

    @staticmethod
    def _normalize_payload(sensor_id=None, operator=None, threshold_value=None, actuator_id=None, action_value=None):
        normalized = {
            'sensor_id': int(sensor_id) if sensor_id not in (None, '') else None,
            'operator': operator.strip() if isinstance(operator, str) else operator,
            'threshold_value': float(threshold_value) if threshold_value not in (None, '') else None,
            'actuator_id': int(actuator_id) if actuator_id not in (None, '') else None,
            'action_value': action_value.strip().upper() if isinstance(action_value, str) else action_value,
        }
        return normalized

    @staticmethod
    def _validate_payload(sensor_id=None, operator=None, threshold_value=None, actuator_id=None,
                          action_value=None, require_all: bool = True) -> tuple[dict | None, dict | None]:
        try:
            payload = ThresholdService._normalize_payload(
                sensor_id=sensor_id,
                operator=operator,
                threshold_value=threshold_value,
                actuator_id=actuator_id,
                action_value=action_value,
            )
        except (TypeError, ValueError):
            return None, ThresholdService._error(
                'VALIDATION_ERROR',
                'Giá trị ngưỡng phải là số hợp lệ.',
                {'field': 'threshold_value'}
            )

        if require_all and payload['sensor_id'] is None:
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng chọn cảm biến.', {'field': 'sensor_id'})
        if require_all and payload['operator'] in (None, ''):
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng chọn toán tử.', {'field': 'operator'})
        if require_all and payload['threshold_value'] is None:
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng nhập giá trị ngưỡng.', {'field': 'threshold_value'})
        if require_all and payload['actuator_id'] is None:
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng chọn thiết bị đầu ra.', {'field': 'actuator_id'})
        if require_all and payload['action_value'] in (None, ''):
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng chọn hành động kích hoạt.', {'field': 'action_value'})

        if payload['operator'] is not None and payload['operator'] not in ThresholdRule.VALID_OPERATORS:
            return None, ThresholdService._error(
                'VALIDATION_ERROR',
                f"Toán tử không hợp lệ. Chỉ chấp nhận: {', '.join(ThresholdRule.VALID_OPERATORS)}",
                {'field': 'operator'}
            )

        if payload['threshold_value'] is not None and not math.isfinite(payload['threshold_value']):
            return None, ThresholdService._error(
                'VALIDATION_ERROR',
                'Giá trị ngưỡng phải là số hữu hạn.',
                {'field': 'threshold_value'}
            )

        if payload['action_value'] in ('', None):
            return None, ThresholdService._error('VALIDATION_ERROR', 'Vui lòng chọn hành động kích hoạt.', {'field': 'action_value'})

        return payload, None

    @staticmethod
    def _get_sensor(sensor_id: int) -> tuple[Sensor | None, dict | None]:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return None, ThresholdService._error('SENSOR_NOT_FOUND', 'Không tìm thấy cảm biến.')
        if not sensor.is_active:
            return None, ThresholdService._error('SENSOR_INACTIVE', f'Cảm biến {sensor.name} đang inactive.')
        return sensor, None

    @staticmethod
    def _get_actuator(actuator_id: int) -> tuple[Actuator | None, dict | None]:
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None, ThresholdService._error('ACTUATOR_NOT_FOUND', 'Không tìm thấy thiết bị đầu ra.')
        if not actuator.is_active:
            return None, ThresholdService._error('ACTUATOR_INACTIVE', f'Thiết bị {actuator.name} đang inactive.')
        return actuator, None

    @staticmethod
    def _find_conflict(sensor_id: int, operator: str, threshold_value: float,
                       actuator_id: int, exclude_rule_id: int | None = None) -> ThresholdRule | None:
        query = ThresholdRule.query.filter_by(
            sensor_id=sensor_id,
            actuator_id=actuator_id,
            operator=operator,
            threshold_value=threshold_value,
        )
        if exclude_rule_id is not None:
            query = query.filter(ThresholdRule.id != exclude_rule_id)
        return query.first()

    @staticmethod
    def _serialize_rule_for_log(rule: ThresholdRule) -> dict:
        return {
            'rule_id': rule.id,
            'sensor_id': rule.sensor_id,
            'sensor_name': normalize_sensor_name(rule.sensor.name if rule.sensor else None, rule.sensor.type if rule.sensor else None, rule.sensor.feed_key if rule.sensor else None) if rule.sensor else None,
            'operator': rule.operator,
            'threshold_value': rule.threshold_value,
            'actuator_id': rule.actuator_id,
            'actuator_name': normalize_actuator_name(rule.actuator.name if rule.actuator else None, rule.actuator.type if rule.actuator else None, rule.actuator.feed_key if rule.actuator else None) if rule.actuator else None,
            'action_value': rule.action_value,
            'is_active': rule.is_active,
            'description': rule.description,
        }

    @staticmethod
    def _log_rule_event(action: str, description: str, rule: ThresholdRule, user_id: int | None = None,
                        metadata: dict | None = None) -> None:
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL,
            description=description,
            actuator_id=rule.actuator_id,
            user_id=user_id,
            device_name=normalize_actuator_name(rule.actuator.name if rule.actuator else None, rule.actuator.type if rule.actuator else None, rule.actuator.feed_key if rule.actuator else None) if rule.actuator else None,
            metadata={
                'category': 'threshold_rule',
                'action': action,
                **(metadata or {}),
            }
        )

    @staticmethod
    def get_all_rules(is_active: bool = None) -> List[ThresholdRule]:
        query = ThresholdRule.query
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        return query.order_by(ThresholdRule.updated_at.desc(), ThresholdRule.id.desc()).all()

    @staticmethod
    def get_rules_for_sensor(sensor_id: int) -> List[ThresholdRule]:
        return ThresholdRule.query.filter_by(sensor_id=sensor_id).order_by(ThresholdRule.updated_at.desc()).all()

    @staticmethod
    def get_rules_for_actuator(actuator_id: int) -> List[ThresholdRule]:
        return ThresholdRule.query.filter_by(actuator_id=actuator_id).order_by(ThresholdRule.updated_at.desc()).all()

    @staticmethod
    def get_rule_by_id(rule_id: int) -> Optional[ThresholdRule]:
        return ThresholdRule.query.get(rule_id)

    @staticmethod
    def create_rule(sensor_id: int, operator: str, threshold_value: float,
                    actuator_id: int, action_value: str,
                    description: str = None, user_id: int | None = None) -> Tuple[Optional[ThresholdRule], Optional[dict]]:
        payload, error = ThresholdService._validate_payload(
            sensor_id=sensor_id,
            operator=operator,
            threshold_value=threshold_value,
            actuator_id=actuator_id,
            action_value=action_value,
            require_all=True,
        )
        if error:
            return None, error

        sensor, error = ThresholdService._get_sensor(payload['sensor_id'])
        if error:
            return None, error

        actuator, error = ThresholdService._get_actuator(payload['actuator_id'])
        if error:
            return None, error

        conflict = ThresholdService._find_conflict(
            sensor_id=payload['sensor_id'],
            operator=payload['operator'],
            threshold_value=payload['threshold_value'],
            actuator_id=payload['actuator_id'],
        )
        if conflict:
            return None, ThresholdService._error(
                'RULE_CONFLICT',
                'Quy tắc xung đột hoặc trùng với ngưỡng đã tồn tại.',
                {
                    'existing_rule_id': conflict.id,
                    'existing_condition': conflict.get_condition_string(),
                    'existing_action_value': conflict.action_value,
                }
            )

        rule = ThresholdRule(
            sensor_id=payload['sensor_id'],
            operator=payload['operator'],
            threshold_value=payload['threshold_value'],
            actuator_id=payload['actuator_id'],
            action_value=payload['action_value'],
            description=(description or '').strip() or None,
            is_active=True,
        )

        db.session.add(rule)
        db.session.commit()

        ThresholdService._log_rule_event(
            action='created',
            description=f"Tạo rule mới: {sensor.name} {rule.operator} {rule.threshold_value}{sensor.unit or ''} -> {actuator.name} = {rule.action_value}",
            rule=rule,
            user_id=user_id,
            metadata={'rule': ThresholdService._serialize_rule_for_log(rule)}
        )

        return rule, None

    @staticmethod
    def update_rule(rule_id: int, operator: str = None, threshold_value: float = None,
                    action_value: str = None, description: str = None,
                    is_active: bool = None, user_id: int | None = None) -> Tuple[Optional[ThresholdRule], Optional[dict]]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None, ThresholdService._error('RULE_NOT_FOUND', 'Không tìm thấy rule.')

        before = ThresholdService._serialize_rule_for_log(rule)

        merged_payload = {
            'sensor_id': rule.sensor_id,
            'operator': operator if operator is not None else rule.operator,
            'threshold_value': threshold_value if threshold_value is not None else rule.threshold_value,
            'actuator_id': rule.actuator_id,
            'action_value': action_value if action_value is not None else rule.action_value,
        }

        payload, error = ThresholdService._validate_payload(**merged_payload, require_all=True)
        if error:
            return None, error

        sensor, error = ThresholdService._get_sensor(payload['sensor_id'])
        if error:
            return None, error

        actuator, error = ThresholdService._get_actuator(payload['actuator_id'])
        if error:
            return None, error

        conflict = ThresholdService._find_conflict(
            sensor_id=payload['sensor_id'],
            operator=payload['operator'],
            threshold_value=payload['threshold_value'],
            actuator_id=payload['actuator_id'],
            exclude_rule_id=rule.id,
        )
        if conflict:
            return None, ThresholdService._error(
                'RULE_CONFLICT',
                'Quy tắc cập nhật bị xung đột với rule đã có.',
                {
                    'existing_rule_id': conflict.id,
                    'existing_condition': conflict.get_condition_string(),
                    'existing_action_value': conflict.action_value,
                }
            )

        rule.operator = payload['operator']
        rule.threshold_value = payload['threshold_value']
        rule.action_value = payload['action_value']
        if description is not None:
            rule.description = description.strip() or None
        if is_active is not None:
            rule.is_active = bool(is_active)

        rule.updated_at = datetime.utcnow()
        db.session.commit()

        ThresholdService._log_rule_event(
            action='updated',
            description=f"Cập nhật rule #{rule.id}: {sensor.name} {rule.operator} {rule.threshold_value}{sensor.unit or ''} -> {actuator.name} = {rule.action_value}",
            rule=rule,
            user_id=user_id,
            metadata={
                'before': before,
                'after': ThresholdService._serialize_rule_for_log(rule),
            }
        )

        return rule, None

    @staticmethod
    def delete_rule(rule_id: int, user_id: int | None = None) -> Tuple[bool, Optional[dict]]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return False, ThresholdService._error('RULE_NOT_FOUND', 'Không tìm thấy rule.')

        snapshot = ThresholdService._serialize_rule_for_log(rule)
        ThresholdService._log_rule_event(
            action='deleted',
            description=f"Xóa rule #{rule.id}: {rule.get_condition_string()} -> {rule.actuator.name if rule.actuator else 'Unknown'} = {rule.action_value}",
            rule=rule,
            user_id=user_id,
            metadata={'deleted_rule': snapshot}
        )

        db.session.delete(rule)
        db.session.commit()
        return True, None

    @staticmethod
    def toggle_rule(rule_id: int, user_id: int | None = None) -> Tuple[Optional[ThresholdRule], Optional[dict]]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None, ThresholdService._error('RULE_NOT_FOUND', 'Không tìm thấy rule.')

        rule.is_active = not rule.is_active
        rule.updated_at = datetime.utcnow()
        db.session.commit()

        ThresholdService._log_rule_event(
            action='toggled',
            description=f"{'Kích hoạt' if rule.is_active else 'Vô hiệu hóa'} rule #{rule.id}: {rule.get_condition_string()} -> {rule.actuator.name if rule.actuator else 'Unknown'} = {rule.action_value}",
            rule=rule,
            user_id=user_id,
            metadata={'after': ThresholdService._serialize_rule_for_log(rule)}
        )

        return rule, None

    @staticmethod
    def evaluate_rule(rule_id: int) -> Tuple[bool, Optional[str]]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule or not rule.is_active:
            return False, None

        sensor = rule.sensor
        latest_data = sensor.get_latest_data() if sensor else None
        if not latest_data:
            return False, None

        if rule.evaluate(latest_data.value):
            return True, rule.action_value
        return False, None

    @staticmethod
    def evaluate_and_execute(rule_id: int) -> Tuple[bool, str]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return False, 'Rule not found'
        if not rule.is_active:
            return False, 'Rule is not active'

        actuator = rule.actuator
        if not actuator:
            return False, 'Actuator not found'
        if actuator.mode != Actuator.MODE_AUTO:
            return False, f'Actuator {actuator.name} is in MANUAL mode'

        sensor = rule.sensor
        latest_data = sensor.get_latest_data() if sensor else None
        if not latest_data:
            return False, 'No sensor data available'

        if not rule.evaluate(latest_data.value):
            return False, 'Condition not met'

        current_value = actuator.current_value
        if current_value == rule.action_value:
            return False, 'Already in desired state'

        actuator.current_value = rule.action_value
        actuator.updated_at = datetime.utcnow()

        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, rule.action_value)

        EventLog.log_event(
            event_type=EventLog.TYPE_AUTO,
            description=f"{rule.get_condition_string()}: {actuator.name} set to {rule.action_value}",
            actuator_id=actuator.id,
            device_name=actuator.name,
            metadata={
                'rule_id': rule.id,
                'sensor_value': latest_data.value,
                'action_value': rule.action_value,
                'triggered_at': datetime.utcnow().isoformat(),
            }
        )

        db.session.commit()
        return True, f'Executed: {actuator.name} set to {rule.action_value}'

    @staticmethod
    def evaluate_all_rules() -> dict:
        rules = ThresholdRule.query.filter_by(is_active=True).all()
        results = {
            'executed': [],
            'skipped': [],
            'errors': []
        }

        for rule in rules:
            try:
                executed, message = ThresholdService.evaluate_and_execute(rule.id)
                if executed:
                    results['executed'].append({
                        'rule_id': rule.id,
                        'message': message
                    })
                else:
                    results['skipped'].append({
                        'rule_id': rule.id,
                        'reason': message
                    })
            except Exception as exc:  # pragma: no cover - defensive path
                results['errors'].append({
                    'rule_id': rule.id,
                    'error': str(exc)
                })
        return results

    @staticmethod
    def get_rule_status(rule_id: int) -> Optional[dict]:
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None

        sensor = rule.sensor
        latest_data = sensor.get_latest_data() if sensor else None
        condition_met = bool(latest_data and rule.evaluate(latest_data.value))

        return {
            'id': rule.id,
            'sensor': {
                'id': sensor.id if sensor else None,
                'name': normalize_sensor_name(sensor.name if sensor else None, sensor.type if sensor else None, sensor.feed_key if sensor else None) if sensor else None,
                'type': sensor.type if sensor else None,
                'current_value': latest_data.value if latest_data else None,
                'unit': sensor.unit if sensor else None,
            },
            'condition': rule.get_condition_string(),
            'condition_met': condition_met,
            'actuator': {
                'id': rule.actuator.id if rule.actuator else None,
                'name': normalize_actuator_name(rule.actuator.name if rule.actuator else None, rule.actuator.type if rule.actuator else None, rule.actuator.feed_key if rule.actuator else None) if rule.actuator else None,
                'current_value': rule.actuator.current_value if rule.actuator else None,
                'mode': rule.actuator.mode if rule.actuator else None,
            },
            'action_value': rule.action_value,
            'is_active': rule.is_active,
            'updated_at': rule.updated_at.isoformat() if rule.updated_at else None,
        }